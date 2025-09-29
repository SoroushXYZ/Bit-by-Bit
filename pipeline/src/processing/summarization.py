"""
Step 7: Article Summarization for Newsletter

This step creates concise, newsletter-ready summaries of prioritized articles
with different lengths based on their category (headlines, secondary, optional).
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


class SummarizationStep:
    """
    Article Summarization Step for Newsletter Generation.
    
    This step creates concise summaries of articles based on their category:
    - Headlines: 2-3 sentences (45-60 words)
    - Secondary: 1 sentence (20-30 words)  
    - Optional: Title only or title + 1 line
    """
    
    def __init__(self, config_loader):
        self.step_name = "summarization"
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
        
        # Summarization configuration
        self.summarization_config = self.config['summarization']
        self.max_content_tokens = self.config.get('text_processing', {}).get('max_content_tokens', 2000)
        self.fallback_summary_tokens = self.summarization_config['fallback_summary_tokens']
        
    def _load_input_data(self) -> Dict[str, Any]:
        """Load input data from article prioritization step."""
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
            
            self.logger.info(f"Loaded prioritized articles from input file")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load input data: {e}")
            raise
    
    def _save_output_data(self, output_data: Dict[str, Any]) -> str:
        """Save summarized articles to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_template = self.config['output']['filename_template']
            filename = filename_template.format(timestamp=timestamp)
            
            output_path = Path(self.data_paths['processed']) / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved summarized articles to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save output data: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better processing."""
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
    
    def _prepare_article_for_summarization(self, article: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Prepare article content for summarization based on category."""
        title = self._clean_text(article.get('title', ''))
        content = self._clean_text(article.get('content', ''))
        summary = self._clean_text(article.get('summary', ''))
        
        # Determine content to use based on category and availability
        if category in ['headlines', 'secondary']:
            # For headlines and secondary, try to use full content first
            if content and len(content) > 50:  # Has substantial content
                content_to_use = self._truncate_content(content, self.max_content_tokens)
                content_source = 'full_content'
            elif summary and len(summary) > 20:  # Fall back to summary
                content_to_use = self._truncate_content(summary, self.fallback_summary_tokens)
                content_source = 'summary'
            else:  # No good content available
                content_to_use = ""
                content_source = 'none'
        else:  # Optional articles
            # For optional, try to use content or summary for descriptive sentences
            if content and len(content) > 50:  # Try full content first
                content_to_use = self._truncate_content(content, self.max_content_tokens)
                content_source = 'full_content'
            elif summary and len(summary) > 20:  # Fall back to summary
                content_to_use = self._truncate_content(summary, self.fallback_summary_tokens)
                content_source = 'summary'
            else:  # No good content available
                content_to_use = ""
                content_source = 'none'
        
        return {
            'title': title,
            'content': content_to_use,
            'content_source': content_source,
            'original_summary': summary,
            'url': article.get('url', ''),
            'feed_name': article.get('feed_name', 'Unknown'),
            'quality_score': article.get('quality_score', 0),
            'quality_level': article.get('quality_level', 'unknown')
        }
    
    def _create_summarization_prompt(self, article: Dict[str, Any], category: str) -> str:
        """Create prompt for LLM to summarize article based on category."""
        
        title = article['title']
        content = article['content']
        content_source = article['content_source']
        
        # Define requirements based on category
        if category == 'headlines':
            title_requirement = "8-12 words max (60-80 characters)"
            summary_requirement = "2-3 sentences, 45-60 words total. Include what happened + why it matters"
            example = "Microsoft launched a unified Marketplace combining Azure solutions, AI apps, and Copilot agents. The move streamlines enterprise adoption by cutting setup times and expanding access to over 3,000 AI offerings, making it easier for companies to integrate AI into daily workflows."
        elif category == 'secondary':
            title_requirement = "8-12 words max (60-80 characters)"
            summary_requirement = "1 sentence, 20-30 words. Straight 'what happened'"
            example = "NVIDIA unveiled a new GPU optimized for AI workloads, promising faster performance and lower energy use for enterprise-scale training and inference."
        else:  # optional
            title_requirement = "8-12 words max (60-80 characters)"
            summary_requirement = "1 short, descriptive sentence (15-25 words). More informative than a title but very concise"
            example = "OnePlus 15 launches with latest Snapdragon chipset, promising enhanced performance and efficiency for flagship smartphones."
        
        # Build content section based on what's available
        if content_source == 'full_content':
            content_section = f"Content: {content}"
        elif content_source == 'summary':
            content_section = f"Summary: {content}"
        else:
            content_section = "No detailed content available"
        
        prompt = f"""You are an expert tech newsletter editor. Create a concise, newsletter-ready summary for this article.

ARTICLE DETAILS:
Title: {title}
{content_section}
Category: {category.upper()}

REQUIREMENTS:
- New Title: {title_requirement}
- Summary: {summary_requirement}

EXAMPLE FOR {category.upper()}:
{example}

INSTRUCTIONS:
- Make titles reader-friendly, avoid marketing fluff
- Focus on what happened and why it matters (for headlines)
- Keep language clear and professional
- Ensure the summary fits the word count requirements
- For optional articles: create a short, descriptive sentence that's more informative than a title

Respond ONLY with a JSON object in this exact format:
{{
    "title": "<new concise title>",
    "summary": "<summary based on requirements>",
    "word_count": <actual word count of summary>,
    "content_source_used": "{content_source}"
}}

Focus on creating content that would be valuable for tech professionals and enthusiasts."""

        return prompt
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call Ollama LLM for article summarization with fallback support."""
        try:
            self.logger.debug(f"🤖 Calling LLM for article summarization...")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent results
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")
            
            result = response.json()
            llm_response = result.get('response', '')
            
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
    
    def _create_fallback_summary(self, article: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Create fallback summary when LLM fails."""
        title = article['title']
        content_source = article['content_source']
        
        # For fallback, just clean up the title and use original summary if available
        clean_title = self._clean_text(title)
        
        if category in ['headlines', 'secondary'] and article.get('original_summary'):
            # Use original summary as fallback
            fallback_summary = self._clean_text(article['original_summary'])
            # Truncate if too long
            if len(fallback_summary) > 200:
                fallback_summary = fallback_summary[:200] + "..."
        else:
            # For optional or no summary available, just use title
            fallback_summary = ""
        
        return {
            "title": clean_title,
            "summary": fallback_summary,
            "word_count": len(fallback_summary.split()) if fallback_summary else 0,
            "content_source_used": content_source,
            "fallback_used": True
        }
    
    def _summarize_article(self, article: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Summarize a single article based on its category."""
        try:
            # Prepare article for summarization
            prepared_article = self._prepare_article_for_summarization(article, category)
            
            # Create prompt and call LLM
            prompt = self._create_summarization_prompt(prepared_article, category)
            llm_response = self._call_llm(prompt)
            
            if llm_response is not None:
                # LLM succeeded
                summary_result = llm_response
                summary_result['fallback_used'] = False
                self.logger.debug(f"✅ LLM summarization successful for: {prepared_article['title'][:50]}...")
            else:
                # LLM failed - use fallback
                summary_result = self._create_fallback_summary(prepared_article, category)
                self.logger.warning(f"⚠️ Using fallback summarization for: {prepared_article['title'][:50]}...")
            
            # Add metadata
            summary_result['original_title'] = prepared_article['title']
            summary_result['original_url'] = prepared_article['url']
            summary_result['feed_name'] = prepared_article['feed_name']
            summary_result['quality_score'] = prepared_article['quality_score']
            summary_result['quality_level'] = prepared_article['quality_level']
            summary_result['category'] = category
            
            return summary_result
            
        except Exception as e:
            self.logger.error(f"❌ Error summarizing article: {e}")
            # Return minimal fallback
            return {
                "title": self._clean_text(article.get('title', 'Untitled')),
                "summary": "",
                "word_count": 0,
                "content_source_used": "none",
                "fallback_used": True,
                "error": str(e),
                "original_title": article.get('title', 'Untitled'),
                "original_url": article.get('url', ''),
                "feed_name": article.get('feed_name', 'Unknown'),
                "quality_score": article.get('quality_score', 0),
                "quality_level": article.get('quality_level', 'unknown'),
                "category": category
            }
    
    def execute(self) -> Dict[str, Any]:
        """Execute the summarization step."""
        start_time = time.time()
        
        try:
            self.logger.info(f"🚀 Starting {self.step_name} step")
            
            # Load input data
            input_data = self._load_input_data()
            categorization = input_data.get('categorization', {})
            
            if not categorization:
                self.logger.warning("No categorization data found in input")
                return {
                    'metadata': {
                        'step': self.step_name,
                        'timestamp': datetime.now().isoformat(),
                        'processing_time_seconds': time.time() - start_time,
                        'articles_processed': 0
                    },
                    'summaries': {
                        'headlines': [],
                        'secondary': [],
                        'optional': []
                    },
                    'statistics': {
                        'total_articles': 0,
                        'headlines_count': 0,
                        'secondary_count': 0,
                        'optional_count': 0,
                        'llm_success_count': 0,
                        'fallback_count': 0
                    }
                }
            
            # Process each category
            summaries = {
                'headlines': [],
                'secondary': [],
                'optional': []
            }
            
            statistics = {
                'total_articles': 0,
                'headlines_count': 0,
                'secondary_count': 0,
                'optional_count': 0,
                'llm_success_count': 0,
                'fallback_count': 0
            }
            
            # Process headlines
            headlines = categorization.get('headlines', [])
            self.logger.info(f"📰 Summarizing {len(headlines)} headline articles...")
            for article in headlines:
                summary = self._summarize_article(article, 'headlines')
                summaries['headlines'].append(summary)
                statistics['headlines_count'] += 1
                statistics['total_articles'] += 1
                if summary.get('fallback_used', False):
                    statistics['fallback_count'] += 1
                else:
                    statistics['llm_success_count'] += 1
            
            # Process secondary
            secondary = categorization.get('secondary', [])
            self.logger.info(f"📋 Summarizing {len(secondary)} secondary articles...")
            for article in secondary:
                summary = self._summarize_article(article, 'secondary')
                summaries['secondary'].append(summary)
                statistics['secondary_count'] += 1
                statistics['total_articles'] += 1
                if summary.get('fallback_used', False):
                    statistics['fallback_count'] += 1
                else:
                    statistics['llm_success_count'] += 1
            
            # Process optional
            optional = categorization.get('optional', [])
            self.logger.info(f"📄 Summarizing {len(optional)} optional articles...")
            for article in optional:
                summary = self._summarize_article(article, 'optional')
                summaries['optional'].append(summary)
                statistics['optional_count'] += 1
                statistics['total_articles'] += 1
                if summary.get('fallback_used', False):
                    statistics['fallback_count'] += 1
                else:
                    statistics['llm_success_count'] += 1
            
            processing_time = time.time() - start_time
            
            # Prepare output data
            output_data = {
                'metadata': {
                    'step': self.step_name,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time_seconds': processing_time,
                    'articles_processed': statistics['total_articles'],
                    'llm_model': self.model_name,
                    'max_content_tokens': self.max_content_tokens,
                    'fallback_summary_tokens': self.fallback_summary_tokens
                },
                'summaries': summaries,
                'statistics': statistics
            }
            
            # Save to file
            output_file = self._save_output_data(output_data)
            
            # Log results
            self.logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
            self.logger.info(f"📊 Summarization results:")
            self.logger.info(f"   📰 Headlines: {statistics['headlines_count']}")
            self.logger.info(f"   📋 Secondary: {statistics['secondary_count']}")
            self.logger.info(f"   📄 Optional: {statistics['optional_count']}")
            self.logger.info(f"   ✅ LLM Success: {statistics['llm_success_count']}/{statistics['total_articles']}")
            self.logger.info(f"   🔄 Fallback Used: {statistics['fallback_count']}/{statistics['total_articles']}")
            
            # Show sample summaries
            if summaries['headlines']:
                self.logger.info(f"\n📰 Sample Headline Summaries:")
                for i, summary in enumerate(summaries['headlines'][:2], 1):
                    self.logger.info(f"   {i}. {summary['title']}")
                    if summary['summary']:
                        self.logger.info(f"      {summary['summary']}")
            
            if summaries['secondary']:
                self.logger.info(f"\n📋 Sample Secondary Summaries:")
                for i, summary in enumerate(summaries['secondary'][:2], 1):
                    self.logger.info(f"   {i}. {summary['title']}")
                    if summary['summary']:
                        self.logger.info(f"      {summary['summary']}")
            
            return {
                'success': True,
                **output_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ {self.step_name} step failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'step_name': self.step_name,
                'timestamp': datetime.now().isoformat()
            }
