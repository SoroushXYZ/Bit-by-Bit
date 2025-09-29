"""
Content Filtering Step for Bit-by-Bit Newsletter Pipeline.
Applies basic content filtering for length and language detection.
"""

import json
import re
import os
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.config_loader import ConfigLoader

# Import langdetect for language detection
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class ContentFilteringStep:
    """Step 2: Basic content filtering for length and language detection."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.logger = get_logger()
        self.step_config = self._load_step_config()
        self.data_paths = config_loader.get_data_paths()
        
        # Ensure data directories exist
        self._ensure_directories()
        
        # Check dependencies
        self._check_dependencies()
    
    def _load_step_config(self) -> Dict[str, Any]:
        """Load and validate content filtering step configuration."""
        try:
            config = self.config_loader.get_step_config('content_filtering')
            required_fields = ['input', 'filters', 'output', 'error_handling']
            self.config_loader.validate_step_config(config, required_fields)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load content filtering configuration: {e}")
            raise
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        try:
            for path_name, path in self.data_paths.items():
                Path(path).mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {path}")
        except Exception as e:
            self.logger.error(f"Failed to create data directories: {e}")
            raise
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not LANGDETECT_AVAILABLE:
            self.logger.warning("langdetect not available - language detection will be disabled")
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        if not text:
            return 0
        # Simple word counting - split by whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    def _get_combined_text(self, article: Dict[str, Any], fields: List[str]) -> str:
        """Get combined text from specified fields."""
        combined_parts = []
        for field in fields:
            value = article.get(field, '')
            if value:
                combined_parts.append(str(value))
        return ' '.join(combined_parts)
    
    def _check_word_count(self, article: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Check if article meets minimum word count requirements."""
        filter_config = self.step_config['filters']['word_count']
        
        if not filter_config.get('enabled', True):
            return True, {'reason': 'word_count_disabled'}
        
        min_words = filter_config.get('min_words', 100)
        check_fields = filter_config.get('check_fields', ['content'])
        combined_check = filter_config.get('combined_check', True)
        
        if combined_check:
            # Check combined text from all specified fields
            combined_text = self._get_combined_text(article, check_fields)
            word_count = self._count_words(combined_text)
            passes = word_count >= min_words
            
            return passes, {
                'word_count': word_count,
                'min_required': min_words,
                'checked_fields': check_fields,
                'combined_text_length': len(combined_text)
            }
        else:
            # Check each field individually
            field_results = {}
            all_pass = True
            
            for field in check_fields:
                field_text = article.get(field, '')
                field_word_count = self._count_words(field_text)
                field_passes = field_word_count >= min_words
                field_results[field] = {
                    'word_count': field_word_count,
                    'passes': field_passes
                }
                if not field_passes:
                    all_pass = False
            
            return all_pass, {
                'min_required': min_words,
                'field_results': field_results
            }
    
    def _detect_language(self, text: str) -> Tuple[Optional[str], float]:
        """Detect language of text."""
        if not LANGDETECT_AVAILABLE or not text:
            return None, 0.0
        
        try:
            # Clean text for better detection
            cleaned_text = re.sub(r'[^\w\s]', ' ', text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            if len(cleaned_text) < 10:  # Too short for reliable detection
                return None, 0.0
            
            detected_lang = detect(cleaned_text)
            # langdetect doesn't provide confidence, so we use a default
            confidence = 0.9 if detected_lang else 0.0
            
            return detected_lang, confidence
            
        except LangDetectException as e:
            self.logger.debug(f"Language detection failed: {e}")
            return None, 0.0
        except Exception as e:
            self.logger.debug(f"Unexpected error in language detection: {e}")
            return None, 0.0
    
    def _check_language(self, article: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Check if article is in target language."""
        filter_config = self.step_config['filters']['language_detection']
        
        if not filter_config.get('enabled', True) or not LANGDETECT_AVAILABLE:
            return True, {'reason': 'language_detection_disabled'}
        
        target_language = filter_config.get('target_language', 'en')
        confidence_threshold = filter_config.get('confidence_threshold', 0.8)
        check_fields = filter_config.get('check_fields', ['content'])
        combined_check = filter_config.get('combined_check', True)
        
        if combined_check:
            # Check combined text from all specified fields
            combined_text = self._get_combined_text(article, check_fields)
            detected_lang, confidence = self._detect_language(combined_text)
            
            if detected_lang is None:
                # If detection fails, include the article (fallback behavior)
                if self.step_config['error_handling']['fallback_on_language_detection_failure']:
                    return True, {
                        'reason': 'detection_failed_fallback',
                        'detected_language': None,
                        'confidence': 0.0
                    }
                else:
                    return False, {
                        'reason': 'detection_failed',
                        'detected_language': None,
                        'confidence': 0.0
                    }
            
            passes = detected_lang == target_language and confidence >= confidence_threshold
            
            return passes, {
                'detected_language': detected_lang,
                'target_language': target_language,
                'confidence': confidence,
                'confidence_threshold': confidence_threshold,
                'checked_fields': check_fields
            }
        else:
            # Check each field individually (at least one must pass)
            field_results = {}
            any_pass = False
            
            for field in check_fields:
                field_text = article.get(field, '')
                detected_lang, confidence = self._detect_language(field_text)
                
                field_passes = (detected_lang == target_language and 
                              confidence >= confidence_threshold) if detected_lang else False
                
                field_results[field] = {
                    'detected_language': detected_lang,
                    'confidence': confidence,
                    'passes': field_passes
                }
                
                if field_passes:
                    any_pass = True
            
            return any_pass, {
                'target_language': target_language,
                'confidence_threshold': confidence_threshold,
                'field_results': field_results
            }
    
    def _check_basic_quality(self, article: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Check basic quality requirements."""
        filter_config = self.step_config['filters']['basic_quality']
        
        if not filter_config.get('enabled', True):
            return True, {'reason': 'basic_quality_disabled'}
        
        # Check title length
        title = article.get('title', '')
        min_title_length = filter_config.get('min_title_length', 10)
        title_passes = len(title) >= min_title_length
        
        # Check for excluded patterns in title
        exclude_patterns = filter_config.get('exclude_patterns', [])
        case_sensitive = filter_config.get('case_sensitive', False)
        
        title_excluded = False
        matched_pattern = None
        if exclude_patterns:
            title_to_check = title if case_sensitive else title.lower()
            for pattern in exclude_patterns:
                pattern_to_check = pattern if case_sensitive else pattern.lower()
                if pattern_to_check in title_to_check:
                    title_excluded = True
                    matched_pattern = pattern
                    break
        
        # Check URL requirement
        require_url = filter_config.get('require_url', True)
        url_passes = not require_url or bool(article.get('url'))
        
        passes = title_passes and not title_excluded and url_passes
        
        return passes, {
            'title_length': len(title),
            'min_title_length': min_title_length,
            'title_excluded': title_excluded,
            'matched_pattern': matched_pattern,
            'has_url': bool(article.get('url')),
            'require_url': require_url
        }
    
    def _filter_article(self, article: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Apply all filters to an article."""
        filter_results = {}
        
        # Apply word count filter
        word_count_passes, word_count_details = self._check_word_count(article)
        filter_results['word_count'] = {
            'passes': word_count_passes,
            'details': word_count_details
        }
        
        # Apply language detection filter
        language_passes, language_details = self._check_language(article)
        filter_results['language'] = {
            'passes': language_passes,
            'details': language_details
        }
        
        # Apply basic quality filter
        quality_passes, quality_details = self._check_basic_quality(article)
        filter_results['basic_quality'] = {
            'passes': quality_passes,
            'details': quality_details
        }
        
        # Article passes if all enabled filters pass
        overall_passes = (word_count_passes and language_passes and quality_passes)
        
        return overall_passes, filter_results
    
    def _load_input_data(self) -> List[Dict[str, Any]]:
        """Load input data from RSS gathering step."""
        try:
            input_config = self.step_config['input']
            input_path = input_config['input_path']
            filename_pattern = input_config['filename_pattern']
            
            # Find the most recent file matching the pattern
            search_pattern = os.path.join(input_path, filename_pattern)
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
    
    def _save_results(self, filtered_articles: List[Dict[str, Any]], 
                     filter_stats: Dict[str, Any]) -> str:
        """Save filtered results to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_template = self.step_config['output']['filename_template']
            filename = filename_template.format(timestamp=timestamp)
            
            output_path = Path(self.data_paths['processed']) / filename
            
            # Prepare output data
            output_data = {
                'metadata': {
                    'processing_timestamp': datetime.now().isoformat(),
                    'total_articles_input': filter_stats['total_input'],
                    'total_articles_passed': len(filtered_articles),
                    'total_articles_rejected': filter_stats['total_rejected'],
                    'filter_pass_rate': filter_stats['pass_rate'],
                    'step_name': 'content_filtering',
                    'pipeline_version': self.config_loader.base_config.get('pipeline', {}).get('version', '1.0.0')
                },
                'filter_statistics': filter_stats,
                'articles': filtered_articles
            }
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(filtered_articles)} filtered articles to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save filtering results: {e}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """Execute the content filtering step."""
        self.logger.info("Starting content filtering step")
        
        try:
            # Load input data
            articles = self._load_input_data()
            
            # Apply filters
            filtered_articles = []
            filter_stats = {
                'total_input': len(articles),
                'total_rejected': 0,
                'filter_breakdown': {
                    'word_count': {'passed': 0, 'rejected': 0},
                    'language': {'passed': 0, 'rejected': 0},
                    'basic_quality': {'passed': 0, 'rejected': 0}
                },
                'rejection_reasons': []
            }
            
            # Process articles
            for article in articles:
                passes, filter_results = self._filter_article(article)
                
                if passes:
                    filtered_articles.append(article)
                    
                    # Update stats for passed filters
                    for filter_name, result in filter_results.items():
                        if result['passes']:
                            filter_stats['filter_breakdown'][filter_name]['passed'] += 1
                else:
                    filter_stats['total_rejected'] += 1
                    
                    # Update stats for failed filters
                    for filter_name, result in filter_results.items():
                        if not result['passes']:
                            filter_stats['filter_breakdown'][filter_name]['rejected'] += 1
                    
                    # Log rejection reason
                    rejection_reasons = []
                    for filter_name, result in filter_results.items():
                        if not result['passes']:
                            rejection_reasons.append(filter_name)
                    
                    if rejection_reasons:
                        filter_stats['rejection_reasons'].append({
                            'title': article.get('title', 'No title')[:50],
                            'reasons': rejection_reasons,
                            'filter_results': filter_results
                        })
            
            # Calculate pass rate
            filter_stats['pass_rate'] = (len(filtered_articles) / len(articles) * 100) if articles else 0
            
            # Save results
            output_file = self._save_results(filtered_articles, filter_stats)
            
            # Prepare step result
            result = {
                'success': True,
                'step_name': 'content_filtering',
                'articles_input': len(articles),
                'articles_passed': len(filtered_articles),
                'articles_rejected': filter_stats['total_rejected'],
                'pass_rate': filter_stats['pass_rate'],
                'output_file': output_file,
                'filter_statistics': filter_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Content filtering completed: {len(filtered_articles)}/{len(articles)} articles passed ({filter_stats['pass_rate']:.1f}%)")
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'step_name': 'content_filtering',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.logger.critical("Content filtering step failed", exception=e)
            return error_result
