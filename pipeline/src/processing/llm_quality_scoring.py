"""
Step 4: LLM Content Quality Scoring

This step uses an LLM to evaluate content quality and provide detailed scoring
for newsletter curation purposes.
"""

import json
import time
import logging
import os
import re
import requests
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from tqdm import tqdm

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class LLMQualityScoringStep:
    """
    LLM Content Quality Scoring Step.
    
    This step uses an LLM to evaluate content quality based on multiple criteria
    including technical depth, news value, readability, and relevance.
    """
    
    def __init__(self, config_loader):
        self.step_name = "llm_quality_scoring"
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load step configuration
        self.config = self.config_loader.get_step_config(self.step_name)
        
        # Get data paths from config loader
        self.data_paths = self.config_loader.get_data_paths()
        
        # LLM configuration
        self.llm_config = self.config['llm']
        self.url = self.llm_config['server_url']
        self.model = self.llm_config['model']
        self.temperature = self.llm_config.get('temperature', 0.3)
        self.seed = self.llm_config.get('seed', 42)
        self.max_tokens = self.llm_config.get('max_tokens', 2000)
        self.max_retries = self.llm_config.get('max_retries', 3)
        
        # Quality scoring configuration
        self.scoring_config = self.config['scoring']
        self.min_quality_score = self.scoring_config.get('min_quality_score', 60)
        
    def _load_input_data(self) -> List[Dict[str, Any]]:
        """Load input data from ad detection step."""
        import glob
        
        try:
            input_config = self.config['input']
            source_step = input_config['source_step']
            filename_prefix = input_config['filename_prefix']
            
            # Load fixed input file within run directory
            input_path = self.data_paths['processed']
            fixed_input = os.path.join(input_path, f"{filename_prefix}.json")
            if not os.path.exists(fixed_input):
                raise FileNotFoundError(f"Input file not found: {fixed_input}")
            self.logger.info(f"Loading input data from: {fixed_input}")
            
            with open(fixed_input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            articles = data.get('articles', [])
            self.logger.info(f"Loaded {len(articles)} articles from input file")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to load input data: {e}")
            raise
    
    def _save_output_data(self, output_data: Dict[str, Any]) -> str:
        """Save output data to file."""
        try:
            output_config = self.config['output']
            filename_prefix = output_config['filename_prefix']
            save_format = output_config['save_format']
            
            # Use fixed filename within run directory
            filename = f"{filename_prefix}.json"
            
            # Save to processed data path
            output_path = self.data_paths['processed']
            filepath = os.path.join(output_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved output data to: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to save output data: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better LLM processing."""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove excessive punctuation but keep common punctuation
        text = re.sub(r'[^\w\s\-.,!?:;()]', '', text)
        
        return text.strip()
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limits."""
        if not content:
            return ""
        
        # Rough estimation: 1 token ≈ 4 characters for English text
        max_chars = max_tokens * 4
        
        if len(content) <= max_chars:
            return content
        
        # Truncate at word boundary
        truncated = content[:max_chars]
        last_space = truncated.rfind(' ')
        
        if last_space > max_chars * 0.8:  # If we can find a good word boundary
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    
    def _create_quality_analysis_prompt(self, article: Dict[str, Any]) -> str:
        """Create a sophisticated prompt for content quality analysis."""
        title = self._clean_text(article.get('title', ''))
        content = self._clean_text(article.get('content', ''))
        
        # Truncate content for LLM processing
        content_for_analysis = self._truncate_content(content, self.max_tokens)
        
        prompt = f"""You are an expert content curator for a high-quality tech newsletter. Analyze this article and provide a comprehensive quality assessment.

ARTICLE DETAILS:
Title: {title}
Content: {content_for_analysis}

EVALUATION CRITERIA:
1. **Technical Depth** (1-100): How technically informative and detailed is the content?
2. **News Value** (1-100): How newsworthy and timely is this information?
3. **Clarity & Readability** (1-100): How clear, well-structured, and readable is the writing?
4. **Impact & Relevance** (1-100): How significant is this for tech professionals and enthusiasts?
5. **Originality** (1-100): How original and insightful is the content vs generic information?

SCORING GUIDELINES:
- 90-100: Exceptional quality, must-read content
- 80-89: High quality, very valuable
- 70-79: Good quality, worth reading
- 60-69: Acceptable quality, decent content
- 50-59: Below average, questionable value
- 1-49: Poor quality, not suitable

Respond ONLY with a JSON object in this exact format:

{{
    "technical_depth": <1-100>,
    "news_value": <1-100>,
    "clarity_readability": <1-100>,
    "impact_relevance": <1-100>,
    "originality": <1-100>,
    "overall_quality": <1-100>,
    "content_type": "<news|analysis|tutorial|announcement|opinion|other>",
    "tech_relevance": "<high|medium|low>",
    "target_audience": "<beginners|intermediate|advanced|general>",
    "key_strengths": ["<strength1>", "<strength2>"],
    "key_weaknesses": ["<weakness1>", "<weakness2>"],
    "reasoning": "<brief explanation of overall assessment>"
}}

Focus on content that would be valuable for tech professionals, entrepreneurs, and tech enthusiasts. Be strict with quality standards."""

        return prompt
    
    def _analyze_content_with_llm(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content using LLM with retry logic."""
        prompt = self._create_quality_analysis_prompt(article)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "seed": self.seed
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making LLM request (attempt {attempt + 1}/{self.max_retries})")
                
                # Add a small progress indicator for LLM request
                with tqdm(total=1, desc="🤖 LLM processing", leave=False, bar_format="{desc}: {elapsed}") as llm_progress:
                    response = requests.post(
                        f"{self.url}/api/generate",
                        json=payload,
                        timeout=120
                    )
                    llm_progress.update(1)
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get('response', '')
                    
                    # Extract JSON from response
                    try:
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            analysis = json.loads(json_match.group())
                            
                            # Validate required fields
                            required_fields = ['technical_depth', 'news_value', 'clarity_readability', 
                                             'impact_relevance', 'originality', 'overall_quality']
                            
                            if all(field in analysis for field in required_fields):
                                return {
                                    'success': True,
                                    'analysis': analysis,
                                    'raw_response': response_text,
                                    'attempt': attempt + 1
                                }
                            else:
                                raise ValueError(f"Missing required fields in analysis: {analysis}")
                        else:
                            raise ValueError("No JSON found in response")
                            
                    except (json.JSONDecodeError, ValueError) as e:
                        if attempt < self.max_retries - 1:
                            self.logger.warning(f"JSON parsing failed (attempt {attempt + 1}): {e}")
                            time.sleep(1)  # Brief delay before retry
                            continue
                        else:
                            raise e
                else:
                    raise requests.RequestException(f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"LLM request failed (attempt {attempt + 1}): {e}")
                    time.sleep(2)  # Longer delay for network issues
                    continue
                else:
                    raise e
        
        # If we get here, all retries failed
        raise Exception(f"All {self.max_retries} attempts failed")
    
    def _calculate_quality_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional quality metrics from LLM analysis."""
        scores = {
            'technical_depth': analysis.get('technical_depth', 0),
            'news_value': analysis.get('news_value', 0),
            'clarity_readability': analysis.get('clarity_readability', 0),
            'impact_relevance': analysis.get('impact_relevance', 0),
            'originality': analysis.get('originality', 0),
            'overall_quality': analysis.get('overall_quality', 0)
        }
        
        # Calculate derived metrics
        avg_score = sum(scores.values()) / len(scores)
        min_score = min(scores.values())
        max_score = max(scores.values())
        
        # Quality level classification
        if avg_score >= 85:
            quality_level = 'excellent'
        elif avg_score >= 75:
            quality_level = 'high'
        elif avg_score >= 65:
            quality_level = 'good'
        elif avg_score >= 55:
            quality_level = 'fair'
        else:
            quality_level = 'poor'
        
        return {
            'scores': scores,
            'average_score': round(avg_score, 1),
            'min_score': min_score,
            'max_score': max_score,
            'quality_level': quality_level,
            'score_consistency': round(max_score - min_score, 1)
        }
    
    def _should_include_article(self, metrics: Dict[str, Any]) -> bool:
        """Determine if article should be included based on quality metrics."""
        return metrics['average_score'] >= self.min_quality_score
    
    def execute(self) -> Dict[str, Any]:
        """Execute the LLM quality scoring step."""
        self.logger.info("🚀 Starting LLM content quality scoring step")
        
        # Load input data
        articles = self._load_input_data()
        if not articles:
            self.logger.warning("⚠️ No articles found in input data")
            return {
                'success': True,
                'articles_input': 0,
                'articles_passed': 0,
                'pass_rate': 0.0,
                'message': 'No articles to process'
            }
        
        self.logger.info(f"📊 Processing {len(articles)} articles for quality scoring")
        
        # Process articles
        start_time = time.time()
        passed_articles = []
        filtered_articles = []
        quality_results = []
        
        # Statistics tracking
        quality_levels = defaultdict(int)
        content_types = defaultdict(int)
        tech_relevance = defaultdict(int)
        
        # Initialize counters for progress tracking
        llm_success_count = 0
        llm_error_count = 0
        
        # Create progress bar for article processing
        progress_bar = tqdm(
            articles, 
            desc="🔍 Analyzing articles with LLM", 
            unit="article",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        
        for i, article in enumerate(progress_bar):
            try:
                # Update progress bar with current article info
                article_title = article.get('title', 'Unknown')[:50]
                progress_bar.set_postfix({
                    'current': article_title,
                    'passed': len(passed_articles),
                    'filtered': len(filtered_articles),
                    'llm_ok': llm_success_count,
                    'llm_err': llm_error_count
                })
                
                self.logger.debug(f"Analyzing article {i+1}/{len(articles)}: {article_title}...")
                
                # Analyze content with LLM
                llm_result = self._analyze_content_with_llm(article)
                
                if llm_result['success']:
                    llm_success_count += 1
                    analysis = llm_result['analysis']
                    metrics = self._calculate_quality_metrics(analysis)
                    
                    # Track statistics
                    quality_levels[metrics['quality_level']] += 1
                    content_types[analysis.get('content_type', 'unknown')] += 1
                    tech_relevance[analysis.get('tech_relevance', 'unknown')] += 1
                    
                    # Create comprehensive result
                    result = {
                        'article_index': i,
                        'title': article.get('title', 'Unknown'),
                        'url': article.get('url', ''),
                        'feed_name': article.get('feed_name', 'Unknown'),
                        'llm_analysis': analysis,
                        'quality_metrics': metrics,
                        'processing_info': {
                            'llm_attempts': llm_result['attempt'],
                            'processing_time': time.time() - start_time
                        }
                    }
                    
                    quality_results.append(result)
                    
                    # Decide whether to include article
                    if self._should_include_article(metrics):
                        passed_articles.append(article)
                    else:
                        filtered_articles.append({
                            'article': article,
                            'reason': f"Quality score too low: {metrics['average_score']:.1f} < {self.min_quality_score}",
                            'quality_metrics': metrics
                        })
                else:
                    llm_error_count += 1
                    self.logger.error(f"LLM analysis failed for article {i}")
                    # Include article by default if LLM analysis fails
                    passed_articles.append(article)
                
            except Exception as e:
                llm_error_count += 1
                self.logger.error(f"❌ Error processing article {i}: {e}")
                # Include article by default if processing fails
                passed_articles.append(article)
        
        processing_time = time.time() - start_time
        
        # Close progress bar and show final summary
        progress_bar.close()
        
        # Show final progress summary
        self.logger.info(f"📊 Final Progress Summary:")
        self.logger.info(f"   ✅ LLM Success: {llm_success_count}/{len(articles)}")
        self.logger.info(f"   ❌ LLM Errors: {llm_error_count}/{len(articles)}")
        self.logger.info(f"   📈 Articles Passed: {len(passed_articles)}")
        self.logger.info(f"   📉 Articles Filtered: {len(filtered_articles)}")
        
        # Save results
        output_data = {
            'metadata': {
                'step': self.step_name,
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'llm_config': self.llm_config,
                'scoring_config': self.scoring_config
            },
            'statistics': {
                'articles_input': len(articles),
                'articles_passed': len(passed_articles),
                'articles_filtered': len(filtered_articles),
                'pass_rate': (len(passed_articles) / len(articles)) * 100 if articles else 0,
                'quality_level_distribution': dict(quality_levels),
                'content_type_distribution': dict(content_types),
                'tech_relevance_distribution': dict(tech_relevance),
                'average_processing_time_per_article': processing_time / len(articles) if articles else 0
            },
            'articles': passed_articles,
            'quality_results': quality_results
        }
        
        # Save to file
        output_file = self._save_output_data(output_data)
        
        # Log results
        self.logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
        self.logger.info(f"📊 Quality scoring results:")
        self.logger.info(f"   Articles passed: {len(passed_articles)}/{len(articles)} ({output_data['statistics']['pass_rate']:.1f}%)")
        
        self.logger.info(f"\n📊 Quality Level Distribution:")
        for level, count in sorted(quality_levels.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(articles)) * 100
            self.logger.info(f"   {level}: {count} ({percentage:.1f}%)")
        
        self.logger.info(f"\n📊 Content Type Distribution:")
        for content_type, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(articles)) * 100
            self.logger.info(f"   {content_type}: {count} ({percentage:.1f}%)")
        
        # Show high-quality articles
        high_quality = [r for r in quality_results if r['quality_metrics']['quality_level'] in ['excellent', 'high']]
        if high_quality:
            self.logger.info(f"\n⭐ High-quality articles ({len(high_quality)} total):")
            for i, result in enumerate(high_quality[:3], 1):
                self.logger.info(f"   {i}. Quality: {result['quality_metrics']['quality_level']} ({result['quality_metrics']['average_score']:.1f})")
                self.logger.info(f"      Title: {result['title'][:80]}...")
                self.logger.info(f"      Feed: {result['feed_name']}")
        
        self.logger.info(f"💾 Results saved to {output_file}")
        self.logger.info(f"✅ Quality scoring completed: {len(passed_articles)}/{len(articles)} articles passed ({output_data['statistics']['pass_rate']:.1f}%)")
        
        return {
            'success': True,
            'articles_input': len(articles),
            'articles_passed': len(passed_articles),
            'articles_filtered': len(filtered_articles),
            'pass_rate': output_data['statistics']['pass_rate'],
            'quality_statistics': output_data['statistics'],
            'output_file': output_file,
            'processing_time': processing_time
        }
