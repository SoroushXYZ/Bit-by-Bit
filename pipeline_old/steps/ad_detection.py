"""
Step 3: Advertisement Detection and Filtering

This step uses a custom DistilBERT model to detect and filter out advertisements
from the content filtered articles.
"""

import json
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.config_loader import ConfigLoader

# For transformers and NLP
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class AdDetectionStep:
    """
    Advertisement Detection Step using custom DistilBERT model.
    
    This step classifies articles as either news or advertisements using
    a fine-tuned DistilBERT model trained on RSS feed data.
    """
    
    def __init__(self, config_loader):
        self.step_name = "ad_detection"
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load step configuration
        self.config = self.config_loader.get_step_config(self.step_name)
        
        # Initialize model
        self.ad_classifier = None
        self.model_loaded = False
        
        # Get data paths from config loader
        self.data_paths = self.config_loader.get_data_paths()
        
    def _load_input_data(self) -> List[Dict[str, Any]]:
        """Load input data from content filtering step."""
        import os
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
    
    def _save_output_data(self, output_data: Dict[str, Any]) -> str:
        """Save output data to file."""
        try:
            output_config = self.config['output']
            filename_prefix = output_config['filename_prefix']
            save_format = output_config['save_format']
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.json"
            
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
        
    def _load_model(self) -> bool:
        """Load the custom DistilBERT ad detection model."""
        if not TRANSFORMERS_AVAILABLE:
            self.logger.error("❌ Transformers not available. Install with: pip install transformers torch")
            return False
            
        try:
            self.logger.info("📥 Loading custom DistilBERT ad detection model...")
            self.ad_classifier = pipeline(
                "text-classification",
                model=self.config['model']['name'],
                tokenizer=self.config['model']['name']
            )
            
            self.logger.info(f"✅ Custom DistilBERT ad detection model loaded successfully")
            self.logger.info(f"   Model: {self.config['model']['name']}")
            self.logger.info(f"   Trained on: {self.config['model']['training_data']}")
            self.logger.info(f"   Performance: {self.config['model']['performance']}")
            
            self.model_loaded = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error loading model: {e}")
            self.logger.error("   Make sure the model is available on Hugging Face")
            return False
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better classification."""
        if not text:
            return ""
            
        # Remove HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove extra punctuation and normalize
        text = re.sub(r'[^\w\s\-.,!?]', '', text)
        
        return text.strip()
    
    def _prepare_text_for_classification(self, article: Dict[str, Any]) -> str:
        """Prepare article text for ad classification."""
        # Use title as primary input (as per model training)
        title = self._clean_text(str(article.get('title', '')))
        
        # Add summary if available for context
        summary = self._clean_text(str(article.get('summary', '')))
        
        # Combine title and summary, but prioritize title
        if summary and len(title) < 50:  # If title is short, add summary
            combined_text = f"{title} {summary}".strip()
        else:
            combined_text = title
        
        # Limit length for DistilBERT (max 128 tokens as per model)
        max_length = self.config['text_processing']['max_length']
        if len(combined_text) > max_length:
            combined_text = combined_text[:max_length] + "..."
        
        return combined_text
    
    def _classify_article(self, article: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Classify a single article as ad or news."""
        try:
            if not text.strip():  # Only process non-empty text
                return {
                    'prediction': 'empty',
                    'confidence_score': 0.0,
                    'is_advertisement': False,
                    'error': 'Empty text'
                }
            
            # Get classification result
            result = self.ad_classifier(text)
            
            # Extract prediction
            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                label = prediction['label']
                score = prediction['score']
            else:
                label = "unknown"
                score = 0.0
            
            # Determine if it's an advertisement
            is_ad = label == self.config['classification']['advertisement_label']
            
            return {
                'prediction': label,
                'confidence_score': score,
                'is_advertisement': is_ad
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error classifying article '{article.get('title', 'Unknown')}': {e}")
            return {
                'prediction': 'error',
                'confidence_score': 0.0,
                'is_advertisement': False,
                'error': str(e)
            }
    
    def _should_include_article(self, classification_result: Dict[str, Any]) -> bool:
        """Determine if article should be included based on classification."""
        # Always exclude advertisements
        if classification_result['is_advertisement']:
            return False
            
        # Check minimum confidence threshold for news
        min_confidence = self.config['filtering']['min_news_confidence']
        if classification_result['confidence_score'] < min_confidence:
            return False
            
        return True
    
    def execute(self) -> Dict[str, Any]:
        """Execute the advertisement detection step."""
        self.logger.info("🚀 Starting advertisement detection step")
        
        # Load model
        if not self._load_model():
            return {
                'success': False,
                'error': 'Failed to load ad detection model',
                'articles_input': 0,
                'articles_passed': 0,
                'pass_rate': 0.0
            }
        
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
        
        self.logger.info(f"📊 Processing {len(articles)} articles for ad detection")
        
        # Process articles
        start_time = time.time()
        passed_articles = []
        filtered_articles = []
        classification_results = []
        
        # Statistics tracking
        prediction_counts = defaultdict(int)
        feed_stats = defaultdict(lambda: {'total': 0, 'ads': 0, 'news': 0})
        
        for i, article in enumerate(articles):
            try:
                # Prepare text for classification
                text = self._prepare_text_for_classification(article)
                
                # Classify article
                classification = self._classify_article(article, text)
                classification['index'] = i
                classification['title'] = article.get('title', 'Unknown')
                classification['feed_name'] = article.get('feed_name', 'Unknown')
                classification['text_analyzed'] = text[:100] + "..." if len(text) > 100 else text
                
                classification_results.append(classification)
                prediction_counts[classification['prediction']] += 1
                
                # Track feed statistics
                feed_name = article.get('feed_name', 'Unknown')
                feed_stats[feed_name]['total'] += 1
                if classification['is_advertisement']:
                    feed_stats[feed_name]['ads'] += 1
                else:
                    feed_stats[feed_name]['news'] += 1
                
                # Decide whether to include article
                if self._should_include_article(classification):
                    passed_articles.append(article)
                else:
                    filtered_articles.append({
                        'article': article,
                        'reason': f"Advertisement detected (confidence: {classification['confidence_score']:.3f})" 
                                if classification['is_advertisement'] 
                                else f"Low confidence news (confidence: {classification['confidence_score']:.3f})",
                        'classification': classification
                    })
                
            except Exception as e:
                self.logger.error(f"❌ Error processing article {i}: {e}")
                # Include article by default if processing fails
                passed_articles.append(article)
        
        processing_time = time.time() - start_time
        
        # Calculate statistics
        total_ads = sum(1 for r in classification_results if r['is_advertisement'])
        total_news = len(classification_results) - total_ads
        
        # Save results
        output_data = {
            'metadata': {
                'step': self.step_name,
                'timestamp': datetime.now().isoformat(),
                'processing_time_seconds': processing_time,
                'model_used': self.config['model']['name'],
                'model_info': self.config['model']
            },
            'statistics': {
                'articles_input': len(articles),
                'articles_passed': len(passed_articles),
                'articles_filtered': len(filtered_articles),
                'pass_rate': (len(passed_articles) / len(articles)) * 100 if articles else 0,
                'prediction_counts': dict(prediction_counts),
                'ad_statistics': {
                    'total_ads': total_ads,
                    'total_news': total_news,
                    'ad_percentage': (total_ads / len(articles)) * 100 if articles else 0,
                    'news_percentage': (total_news / len(articles)) * 100 if articles else 0
                }
            },
            'feed_statistics': {
                feed_name: {
                    'total': stats['total'],
                    'ads': stats['ads'],
                    'news': stats['news'],
                    'ad_rate': (stats['ads'] / stats['total']) * 100 if stats['total'] > 0 else 0
                }
                for feed_name, stats in feed_stats.items()
            },
            'articles': passed_articles,
            'classification_results': classification_results
        }
        
        # Save to file
        output_file = self._save_output_data(output_data)
        
        # Log results
        self.logger.info(f"⏱️  Processing time: {processing_time:.2f} seconds")
        self.logger.info(f"🔍 Ad detection results:")
        for label, count in sorted(prediction_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(articles)) * 100
            self.logger.info(f"   {label}: {count} ({percentage:.1f}%)")
        
        self.logger.info(f"\n📊 Ad vs News Summary:")
        self.logger.info(f"   📰 News articles: {total_news} ({(total_news/len(articles)*100):.1f}%)")
        self.logger.info(f"   📢 Advertisement articles: {total_ads} ({(total_ads/len(articles)*100):.1f}%)")
        
        # Show high-confidence ads
        high_conf_ads = [r for r in classification_results 
                        if r['is_advertisement'] and r['confidence_score'] > 0.8]
        if high_conf_ads:
            self.logger.info(f"\n📢 High-confidence advertisements ({len(high_conf_ads)} total):")
            for i, ad in enumerate(high_conf_ads[:3], 1):
                self.logger.info(f"   {i}. Confidence: {ad['confidence_score']:.3f}")
                self.logger.info(f"      Title: {ad['title'][:80]}...")
                self.logger.info(f"      Feed: {ad['feed_name']}")
        
        # Show feeds with highest ad rates
        feed_ad_rates = []
        for feed_name, stats in feed_stats.items():
            if stats['total'] > 0:
                ad_rate = (stats['ads'] / stats['total']) * 100
                feed_ad_rates.append((feed_name, ad_rate, stats['ads'], stats['total']))
        
        feed_ad_rates.sort(key=lambda x: x[1], reverse=True)
        
        if feed_ad_rates:
            self.logger.info(f"\n📊 Top feeds by ad rate:")
            self.logger.info(f"   {'Feed Name':<30} {'Ad Rate':<10} {'Ads':<5} {'Total':<6}")
            self.logger.info(f"   {'-'*30} {'-'*10} {'-'*5} {'-'*6}")
            for feed_name, ad_rate, ads, total in feed_ad_rates[:5]:
                self.logger.info(f"   {feed_name[:29]:<30} {ad_rate:<9.1f}% {ads:<5} {total:<6}")
        
        self.logger.info(f"💾 Results saved to {output_file}")
        self.logger.info(f"✅ Ad detection completed: {len(passed_articles)}/{len(articles)} articles passed ({output_data['statistics']['pass_rate']:.1f}%)")
        
        return {
            'success': True,
            'articles_input': len(articles),
            'articles_passed': len(passed_articles),
            'articles_filtered': len(filtered_articles),
            'pass_rate': output_data['statistics']['pass_rate'],
            'ad_statistics': output_data['statistics']['ad_statistics'],
            'output_file': output_file,
            'processing_time': processing_time
        }
