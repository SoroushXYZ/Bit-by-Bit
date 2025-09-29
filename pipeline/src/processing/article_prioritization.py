"""
Step 6: Article Prioritization using LLM

This step uses LLM to analyze article titles and brief content to categorize
articles into headlines (3-5 most impactful), secondary (8-12 important), 
and optional (remaining articles) based on impact and relevance.
"""

import json
import time
import logging
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class ArticlePrioritizationStep:
    """
    Article Prioritization Step using LLM.
    
    This step analyzes articles to categorize them into:
    - Headlines (3-5 most impactful articles)
    - Secondary (8-12 important articles) 
    - Optional (remaining articles)
    """
    
    def __init__(self, config_loader):
        self.step_name = "article_prioritization"
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load step configuration
        self.config = self.config_loader.get_step_config(self.step_name)
        
        # Get data paths from config loader
        self.data_paths = self.config_loader.get_data_paths()
        
        # LLM configuration
        self.llm_config = self.config['llm']
        self.ollama_endpoint = self.llm_config['server_url']
        self.model_name = self.llm_config['model']
        
        # Prioritization configuration
        self.prioritization_config = self.config['prioritization']
        self.headlines_count = self.prioritization_config['headlines_count']
        self.secondary_count = self.prioritization_config['secondary_count']
        self.content_preview_tokens = self.prioritization_config['content_preview_tokens']
        
        # Impact criteria
        self.impact_criteria = self.prioritization_config['impact_criteria']
        
    def _load_input_data(self) -> List[Dict[str, Any]]:
        """Load input data from deduplication step."""
        import glob
        
        try:
            input_config = self.config['input']
            source_step = input_config['source_step']
            filename_prefix = input_config['filename_prefix']
            
            # Find the most recent file from the source step
            input_path = self.data_paths['processed']
            search_pattern = os.path.join(input_path, f"{filename_prefix}_*.json")
            matching_files = glob.glob(search_pattern)
            
            if not matching_files:
                raise FileNotFoundError(f"No input files found matching pattern: {search_pattern}")
            
            # Get the most recent file
            latest_file = max(matching_files, key=os.path.getctime)
            self.logger.info(f"Loading input data from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            articles = data.get('articles', [])
            self.logger.info(f"Loaded {len(articles)} articles from input file")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to load input data: {e}")
            raise
    
    def _extract_content_preview(self, content: str, max_tokens: int = 50) -> str:
        """Extract first few tokens of content for LLM analysis."""
        if not content:
            return ""
        
        # Simple token approximation (roughly 4 characters per token)
        max_chars = max_tokens * 4
        
        # Clean content and extract preview
        cleaned_content = re.sub(r'\s+', ' ', content.strip())
        
        if len(cleaned_content) <= max_chars:
            return cleaned_content
        
        # Truncate at word boundary
        preview = cleaned_content[:max_chars]
        last_space = preview.rfind(' ')
        if last_space > max_chars * 0.8:  # Don't truncate too much
            preview = preview[:last_space]
        
        return preview + "..."
    
    def _categorize_articles_fallback(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback categorization using quality scores when LLM fails."""
        self.logger.warning("🔄 Using quality-score-based fallback categorization")
        
        # Get fallback configuration
        fallback_config = self.config.get('fallback_strategy', {})
        use_dedup_weight = fallback_config.get('use_deduplication_weight', True)
        dedup_weight = fallback_config.get('deduplication_weight', 2.0)
        
        if use_dedup_weight:
            self.logger.info(f"🔄 Using deduplication weighting (weight={dedup_weight})")
        else:
            self.logger.info("🔄 Using quality scores only (deduplication weighting disabled)")
        
        # Sort articles by composite score (quality + deduplication bonus)
        articles_with_scores = []
        for article in articles:
            quality_score = article.get('quality_score', 0)
            composite_score = quality_score
            
            # Add deduplication weight if enabled and available
            if use_dedup_weight:
                dedup_info = article.get('deduplication_info', {})
                group_size = dedup_info.get('group_size', 1)
                if group_size > 1:  # Only add bonus for articles that were part of duplicate groups
                    dedup_bonus = (group_size - 1) * dedup_weight
                    composite_score += dedup_bonus
                    self.logger.debug(f"Article '{article.get('title', 'Unknown')[:50]}...' gets +{dedup_bonus:.1f} bonus for group_size={group_size}")
            
            articles_with_scores.append((composite_score, article))
        
        # Sort by composite score (descending)
        articles_with_scores.sort(key=lambda x: x[0], reverse=True)
        sorted_articles = [article for _, article in articles_with_scores]
        
        # Categorize based on quality scores
        headlines = []
        secondary = []
        optional = []
        
        # Headlines: Top articles with highest composite scores
        headlines = sorted_articles[:self.headlines_count]
        for i, article in enumerate(headlines):
            article_copy = article.copy()
            quality_score = article.get('quality_score', 0)
            dedup_info = article.get('deduplication_info', {})
            group_size = dedup_info.get('group_size', 1)
            
            if use_dedup_weight and group_size > 1:
                dedup_bonus = (group_size - 1) * dedup_weight
                article_copy['category_reason'] = f'Fallback: Top {i+1} by composite score ({quality_score:.1f} + {dedup_bonus:.1f} dedup bonus, group_size={group_size})'
            else:
                article_copy['category_reason'] = f'Fallback: Top {i+1} by quality score ({quality_score:.1f})'
            
            article_copy['category'] = 'headline'
            article_copy['ranking_score'] = quality_score
            headlines[i] = article_copy
        
        # Secondary: Next batch of articles
        secondary_start = self.headlines_count
        secondary_end = secondary_start + self.secondary_count
        secondary_articles = sorted_articles[secondary_start:secondary_end]
        for i, article in enumerate(secondary_articles):
            article_copy = article.copy()
            quality_score = article.get('quality_score', 0)
            dedup_info = article.get('deduplication_info', {})
            group_size = dedup_info.get('group_size', 1)
            
            if use_dedup_weight and group_size > 1:
                dedup_bonus = (group_size - 1) * dedup_weight
                article_copy['category_reason'] = f'Fallback: Secondary by composite score ({quality_score:.1f} + {dedup_bonus:.1f} dedup bonus, group_size={group_size})'
            else:
                article_copy['category_reason'] = f'Fallback: Secondary by quality score ({quality_score:.1f})'
            
            article_copy['category'] = 'secondary'
            article_copy['ranking_score'] = quality_score
            secondary.append(article_copy)
        
        # Optional: Remaining articles
        optional_articles = sorted_articles[secondary_end:]
        for i, article in enumerate(optional_articles):
            article_copy = article.copy()
            quality_score = article.get('quality_score', 0)
            dedup_info = article.get('deduplication_info', {})
            group_size = dedup_info.get('group_size', 1)
            
            if use_dedup_weight and group_size > 1:
                dedup_bonus = (group_size - 1) * dedup_weight
                article_copy['category_reason'] = f'Fallback: Optional by composite score ({quality_score:.1f} + {dedup_bonus:.1f} dedup bonus, group_size={group_size})'
            else:
                article_copy['category_reason'] = f'Fallback: Optional by quality score ({quality_score:.1f})'
            
            article_copy['category'] = 'optional'
            article_copy['ranking_score'] = quality_score
            optional.append(article_copy)
        
        return {
            'headlines': headlines,
            'secondary': secondary,
            'optional': optional,
            'reasoning': {
                'headlines': f'Fallback: Selected top {len(headlines)} articles by quality score',
                'secondary': f'Fallback: Selected next {len(secondary)} articles by quality score',
                'optional': f'Fallback: Remaining {len(optional)} articles by quality score'
            },
            'rankings': {
                'headlines': {str(i+1): article.get('quality_score', 0) for i, article in enumerate(headlines)},
                'secondary': {str(i+1): article.get('quality_score', 0) for i, article in enumerate(secondary)},
                'optional': {str(i+1): article.get('quality_score', 0) for i, article in enumerate(optional)}
            }
        }
    
    def _create_prioritization_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """Create prompt for LLM to prioritize articles."""
        
        # Prepare article summaries for LLM
        article_summaries = []
        for i, article in enumerate(articles):
            title = article.get('title', 'No title')
            content_preview = self._extract_content_preview(
                article.get('content', ''), 
                self.content_preview_tokens
            )
            feed_name = article.get('feed_name', 'Unknown')
            quality_score = article.get('quality_score', 0)
            
            # Extract deduplication info for importance weighting
            dedup_info = article.get('deduplication_info', {})
            group_size = dedup_info.get('group_size', 1)
            similarity_score = dedup_info.get('max_similarity', 0)
            was_duplicate = dedup_info.get('was_duplicate', False)
            
            # Calculate news importance weight based on coverage
            if was_duplicate and group_size > 1:
                coverage_weight = f" (Covered by {group_size} sources, similarity: {similarity_score:.2f})"
            else:
                coverage_weight = " (Unique coverage)"
            
            article_summaries.append(
                f"{i+1}. Title: {title}\n"
                f"   Content: {content_preview}\n"
                f"   Source: {feed_name}\n"
                f"   Quality Score: {quality_score}\n"
                f"   Coverage: {coverage_weight}\n"
            )
        
        articles_text = "\n".join(article_summaries)
        
        prompt = f"""You are an expert tech news editor with 15+ years of experience creating daily newsletters for tech professionals. Your job is to analyze {len(articles)} articles and categorize them by impact and importance.

HEADLINE SELECTION CRITERIA (in order of priority):
1. **CRITICAL SECURITY VULNERABILITIES** - Zero-day exploits, major breaches, widespread vulnerabilities (highest priority)
2. **BREAKING NEWS** - Major company announcements, regulatory changes, industry-shaking events
3. **SIGNIFICANT PRODUCT LAUNCHES** - Game-changing products, major platform updates, revolutionary tech
4. **INDUSTRY DISRUPTIONS** - Acquisitions, funding rounds, major business changes
5. **AI/ML BREAKTHROUGHS** - Major advances in artificial intelligence and machine learning

SECONDARY SELECTION CRITERIA:
- Important but not breaking news
- Notable updates and developments
- Industry analysis and insights
- Product reviews and comparisons
- Developer tools and open source releases

OPTIONAL SELECTION CRITERIA:
- Interesting but not critical
- Entertainment and lifestyle tech
- Minor updates and announcements
- Opinion pieces and analysis

IMPACT SCORING (0-100):
- 95-100: Critical security issues, major breaches, industry-shaking news
- 90-94: Breaking news, major announcements, significant product launches
- 85-89: Important developments, notable updates, industry analysis
- 80-84: Interesting news, minor updates, product reviews
- 75-79: Optional content, entertainment, opinion pieces

ARTICLES TO ANALYZE:
{articles_text}

Please analyze each article and return a JSON response with this exact format:
{{
    "headlines": [list of article numbers (1-{len(articles)}) for most impactful articles, ordered by importance],
    "secondary": [list of article numbers (1-{len(articles)}) for important articles, ordered by importance],
    "optional": [list of article numbers (1-{len(articles)}) for remaining articles, ordered by importance],
    "rankings": {{
        "headlines": {{"article_number": ranking_score, ...}},
        "secondary": {{"article_number": ranking_score, ...}},
        "optional": {{"article_number": ranking_score, ...}}
    }},
    "reasoning": {{
        "headlines": "Brief explanation of why these were selected as headlines and their ranking order",
        "secondary": "Brief explanation of why these were selected as secondary and their ranking order",
        "optional": "Brief explanation of why these are optional and their ranking order"
    }}
}}

CRITICAL INSTRUCTIONS:
- Security vulnerabilities affecting millions of devices should be TOP priority
- Breaking news and major announcements come next
- Product launches and updates are important but secondary to security
- Gaming reviews and entertainment content should be lower priority
- **COVERAGE WEIGHT**: Articles covered by multiple sources (higher group_size) indicate more important news - use this as a weight in your decision
- **UNIQUE COVERAGE**: Articles with unique coverage might be exclusive or breaking news - consider this for headlines
- Ensure all article numbers 1-{len(articles)} are included exactly once
- Use the impact scoring system to rank articles within each category
- Focus on what tech professionals NEED to know vs. what's interesting

Return only the JSON response, no additional text."""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call Ollama LLM for article prioritization with fallback support."""
        try:
            self.logger.info(f"🤖 Calling LLM for article prioritization...")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            # Simulate LLM failure for testing fallback system
            # Uncomment the line below to test fallback:
            # raise Exception("Simulated LLM failure for testing fallback system")
            
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")
            
            result = response.json()
            llm_response = result.get('response', '')
            
            self.logger.info(f"✅ LLM response received ({len(llm_response)} characters)")
            
            # Parse JSON response
            try:
                # Extract JSON from response (in case there's extra text)
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON found in LLM response")
                
                json_str = llm_response[json_start:json_end]
                parsed_response = json.loads(json_str)
                
                return parsed_response
                
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.error(f"Failed to parse LLM JSON response: {e}")
                self.logger.error(f"Raw response: {llm_response}")
                raise Exception(f"Invalid JSON response from LLM: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ LLM call failed: {e}")
            # Return None to indicate LLM failure - will trigger fallback
            return None
    
    def _categorize_articles(self, articles: List[Dict[str, Any]], llm_response: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize and rank articles based on LLM response."""
        
        headlines = []
        secondary = []
        optional = []
        
        # Create article index mapping
        article_map = {i: article for i, article in enumerate(articles, 1)}
        
        # Get rankings from LLM response
        rankings = llm_response.get('rankings', {})
        
        # Process headlines with ranking
        headlines_with_rank = []
        for article_num in llm_response.get('headlines', []):
            if article_num in article_map:
                article = article_map[article_num].copy()
                article['category'] = 'headline'
                article['category_reason'] = 'Selected by LLM as most impactful'
                # Add ranking score if available
                article['ranking_score'] = rankings.get('headlines', {}).get(str(article_num), 0)
                headlines_with_rank.append((article_num, article))
            else:
                self.logger.warning(f"Invalid article number in headlines: {article_num}")
        
        # Sort headlines by ranking score (higher is better)
        headlines_with_rank.sort(key=lambda x: x[1].get('ranking_score', 0), reverse=True)
        headlines = [article for _, article in headlines_with_rank]
        
        # Process secondary with ranking
        secondary_with_rank = []
        for article_num in llm_response.get('secondary', []):
            if article_num in article_map:
                article = article_map[article_num].copy()
                article['category'] = 'secondary'
                article['category_reason'] = 'Selected by LLM as important'
                # Add ranking score if available
                article['ranking_score'] = rankings.get('secondary', {}).get(str(article_num), 0)
                secondary_with_rank.append((article_num, article))
            else:
                self.logger.warning(f"Invalid article number in secondary: {article_num}")
        
        # Sort secondary by ranking score (higher is better)
        secondary_with_rank.sort(key=lambda x: x[1].get('ranking_score', 0), reverse=True)
        secondary = [article for _, article in secondary_with_rank]
        
        # Process optional with ranking
        optional_with_rank = []
        for article_num in llm_response.get('optional', []):
            if article_num in article_map:
                article = article_map[article_num].copy()
                article['category'] = 'optional'
                article['category_reason'] = 'Categorized by LLM as optional'
                # Add ranking score if available
                article['ranking_score'] = rankings.get('optional', {}).get(str(article_num), 0)
                optional_with_rank.append((article_num, article))
            else:
                self.logger.warning(f"Invalid article number in optional: {article_num}")
        
        # Sort optional by ranking score (higher is better)
        optional_with_rank.sort(key=lambda x: x[1].get('ranking_score', 0), reverse=True)
        optional = [article for _, article in optional_with_rank]
        
        # Add any missing articles to optional (fallback)
        all_categorized = set(llm_response.get('headlines', []) + 
                             llm_response.get('secondary', []) + 
                             llm_response.get('optional', []))
        
        for i, article in enumerate(articles, 1):
            if i not in all_categorized:
                article_copy = article.copy()
                article_copy['category'] = 'optional'
                article_copy['category_reason'] = 'Fallback categorization'
                article_copy['ranking_score'] = 0
                optional.append(article_copy)
                self.logger.warning(f"Article {i} not categorized by LLM, added to optional")
        
        return {
            'headlines': headlines,
            'secondary': secondary,
            'optional': optional,
            'reasoning': llm_response.get('reasoning', {}),
            'rankings': rankings
        }
    
    def _save_output_data(self, output_data: Dict[str, Any]) -> str:
        """Save prioritized articles to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_template = self.config['output']['filename_template']
            filename = filename_template.format(timestamp=timestamp)
            
            output_path = Path(self.data_paths['processed']) / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved prioritized articles to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save output data: {e}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """Execute the article prioritization step."""
        start_time = time.time()
        
        try:
            self.logger.info(f"🚀 Starting {self.step_name} step")
            
            # Load input articles
            articles = self._load_input_data()
            
            if not articles:
                self.logger.warning("No articles to prioritize")
                return {
                    'metadata': {
                        'step': self.step_name,
                        'timestamp': datetime.now().isoformat(),
                        'processing_time_seconds': time.time() - start_time,
                        'articles_processed': 0
                    },
                    'categorization': {
                        'headlines': [],
                        'secondary': [],
                        'optional': []
                    },
                    'statistics': {
                        'total_articles': 0,
                        'headlines_count': 0,
                        'secondary_count': 0,
                        'optional_count': 0
                    }
                }
            
            self.logger.info(f"📊 Prioritizing {len(articles)} articles")
            self.logger.info(f"🎯 Target: {self.headlines_count} headlines, {self.secondary_count} secondary")
            
            # Create prioritization prompt
            prompt = self._create_prioritization_prompt(articles)
            
            # Call LLM for prioritization
            llm_response = self._call_llm(prompt)
            
            # Categorize articles based on LLM response or fallback
            if llm_response is not None:
                # LLM succeeded - use LLM categorization
                categorization = self._categorize_articles(articles, llm_response)
                self.logger.info("✅ Using LLM-based categorization")
            else:
                # LLM failed - check if fallback is enabled
                fallback_config = self.config.get('fallback_strategy', {})
                if fallback_config.get('enable_fallback', True):
                    # Use quality-score fallback
                    categorization = self._categorize_articles_fallback(articles)
                    self.logger.warning("⚠️ Using quality-score fallback categorization")
                else:
                    # Fallback disabled - raise error
                    raise Exception("LLM failed and fallback is disabled in configuration")
            
            processing_time = time.time() - start_time
            
            # Calculate statistics
            headlines_count = len(categorization['headlines'])
            secondary_count = len(categorization['secondary'])
            optional_count = len(categorization['optional'])
            total_categorized = headlines_count + secondary_count + optional_count
            
            # Prepare output data
            output_data = {
                'metadata': {
                    'step': self.step_name,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time_seconds': processing_time,
                    'articles_processed': len(articles),
                    'llm_model': self.model_name,
                    'content_preview_tokens': self.content_preview_tokens,
                    'llm_success': llm_response is not None,
                    'fallback_used': llm_response is None
                },
                'categorization': categorization,
                'statistics': {
                    'total_articles': len(articles),
                    'headlines_count': headlines_count,
                    'secondary_count': secondary_count,
                    'optional_count': optional_count,
                    'total_categorized': total_categorized,
                    'categorization_success_rate': (total_categorized / len(articles)) * 100 if articles else 0,
                    'target_headlines': self.headlines_count,
                    'target_secondary': self.secondary_count,
                    'headlines_target_achieved': headlines_count >= self.headlines_count,
                    'secondary_target_achieved': secondary_count >= self.secondary_count
                },
                'llm_reasoning': llm_response.get('reasoning', {}) if llm_response else {}
            }
            
            # Save to file
            output_file = self._save_output_data(output_data)
            
            # Log results
            self.logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
            self.logger.info(f"📊 Prioritization results:")
            if llm_response is not None:
                self.logger.info(f"   🤖 Method: LLM-based categorization")
            else:
                self.logger.info(f"   🔄 Method: Quality-score fallback categorization")
            self.logger.info(f"   📰 Headlines: {headlines_count}/{self.headlines_count} target")
            self.logger.info(f"   📋 Secondary: {secondary_count}/{self.secondary_count} target")
            self.logger.info(f"   📄 Optional: {optional_count}")
            self.logger.info(f"   ✅ Success rate: {(total_categorized / len(articles)) * 100:.1f}%")
            
            # Show ranking information
            if categorization.get('headlines'):
                self.logger.info(f"📰 Top Headlines (ranked):")
                for i, article in enumerate(categorization['headlines'][:3], 1):
                    score = article.get('ranking_score', 0)
                    self.logger.info(f"   {i}. {article['title'][:60]}... (score: {score})")
            
            if categorization.get('secondary'):
                self.logger.info(f"📋 Top Secondary (ranked):")
                for i, article in enumerate(categorization['secondary'][:3], 1):
                    score = article.get('ranking_score', 0)
                    self.logger.info(f"   {i}. {article['title'][:60]}... (score: {score})")
            
            # Show LLM reasoning
            if llm_response and llm_response.get('reasoning'):
                self.logger.info(f"🤖 LLM Reasoning:")
                for category, reason in llm_response['reasoning'].items():
                    self.logger.info(f"   {category.title()}: {reason}")
            elif llm_response is None:
                self.logger.info(f"🤖 Fallback Reasoning:")
                for category, reason in categorization.get('reasoning', {}).items():
                    self.logger.info(f"   {category.title()}: {reason}")
            
            return output_data
            
        except Exception as e:
            self.logger.error(f"❌ {self.step_name} step failed: {e}")
            raise
