"""
RSS Gathering Step for Bit-by-Bit Newsletter Pipeline.
Gathers raw RSS feed data from configured sources with error handling.
"""

import json
import feedparser
import requests
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class RSSGatheringStep:
    """Step 1: Gather raw RSS feed data from configured sources."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.logger = get_logger()
        self.step_config = self._load_step_config()
        self.rss_feeds = self._load_rss_feeds()
        self.data_paths = config_loader.get_data_paths()
        
        # Ensure data directories exist
        self._ensure_directories()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        return text.strip()
    
    def _load_step_config(self) -> Dict[str, Any]:
        """Load and validate RSS gathering step configuration."""
        try:
            config = self.config_loader.get_step_config('rss_gathering')
            required_fields = ['settings', 'output', 'error_handling']
            self.config_loader.validate_step_config(config, required_fields)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load RSS gathering configuration: {e}")
            raise
    
    def _load_rss_feeds(self) -> List[Dict[str, Any]]:
        """Load RSS feeds configuration."""
        try:
            rss_config_path = self.step_config['rss_feeds_config']
            with open(rss_config_path, 'r', encoding='utf-8') as f:
                rss_config = json.load(f)
            
            # Filter enabled feeds
            enabled_feeds = [feed for feed in rss_config['feeds'] if feed.get('enabled', True)]
            self.logger.info(f"Loaded {len(enabled_feeds)} enabled RSS feeds from {rss_config_path}")
            return enabled_feeds
        except Exception as e:
            self.logger.error(f"Failed to load RSS feeds configuration: {e}")
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
    
    def _fetch_feed(self, feed: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Fetch a single RSS feed with error handling."""
        feed_name = feed['name']
        feed_url = feed['url']
        
        try:
            self.logger.debug(f"Fetching feed: {feed_name}")
            
            # Add timeout and retry logic
            response = requests.get(
                feed_url,
                timeout=self.step_config['settings']['timeout_seconds'],
                headers={'User-Agent': 'Bit-by-Bit Newsletter Pipeline/1.0'}
            )
            response.raise_for_status()
            
            # Parse RSS feed
            parsed_feed = feedparser.parse(response.content)
            
            if parsed_feed.bozo:
                self.logger.warning(f"Feed {feed_name} has parsing warnings: {parsed_feed.bozo_exception}")
            
            # Process articles
            articles = self._process_feed_articles(parsed_feed, feed)
            
            feed_stats = {
                'feed_name': feed_name,
                'feed_url': feed_url,
                'feed_category': feed.get('category', 'Unknown'),
                'articles_found': len(parsed_feed.entries),
                'articles_processed': len(articles),
                'success': True,
                'error': None,
                'fetch_time': datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully fetched {feed_name}: {len(articles)} articles")
            return feed_name, {'articles': articles, 'stats': feed_stats}
            
        except Exception as e:
            error_msg = f"Failed to fetch feed {feed_name}: {str(e)}"
            self.logger.error(error_msg, exception=e)
            
            feed_stats = {
                'feed_name': feed_name,
                'feed_url': feed_url,
                'feed_category': feed.get('category', 'Unknown'),
                'articles_found': 0,
                'articles_processed': 0,
                'success': False,
                'error': str(e),
                'fetch_time': datetime.now().isoformat()
            }
            
            return feed_name, {'articles': [], 'stats': feed_stats}
    
    def _process_feed_articles(self, parsed_feed: feedparser.FeedParserDict, feed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and filter articles from a parsed RSS feed."""
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=self.step_config['settings']['max_age_hours'])
        
        max_items = self.step_config['settings']['max_items_per_feed']
        
        for entry in parsed_feed.entries[:max_items]:
            article = self._parse_article(entry, feed)
            if article:
                # Filter by age - include articles without dates (assume recent)
                if article['published']:
                    try:
                        article_date = datetime.fromisoformat(article['published'].replace('Z', '+00:00'))
                        if article_date >= cutoff_time:
                            articles.append(article)
                    except Exception as e:
                        # If date parsing fails, include the article anyway
                        self.logger.warning(f"Date parsing failed for article, including anyway: {e}")
                        articles.append(article)
                else:
                    # If no date, include it (might be recent)
                    articles.append(article)
        
        return articles
    
    def _parse_article(self, entry: feedparser.FeedParserDict, feed_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a single RSS entry into standardized format - matches notebook logic."""
        try:
            # Handle different date formats
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6])
            
            # Clean content
            title = self.clean_text(entry.get('title', ''))
            summary = self.clean_text(entry.get('summary', ''))
            description = self.clean_text(entry.get('description', ''))
            
            # Use description if summary is empty
            if not summary and description:
                summary = description
            
            # Extract content - handle different content formats
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = self.clean_text(entry.content[0].get('value', ''))
            elif hasattr(entry, 'description') and entry.description:
                content = self.clean_text(entry.description)
            
            article = {
                'title': title,
                'url': entry.get('link', ''),
                'summary': summary,
                'content': content,
                'published': published_date.isoformat() if published_date else None,
                'author': entry.get('author', ''),
                'feed_name': feed_info['name'],
                'feed_category': feed_info.get('category', 'Unknown'),
                'feed_url': feed_info['url'],
                'tags': [tag.term for tag in entry.get('tags', [])],
                'guid': entry.get('id', entry.get('guid', '')),
                'collected_at': datetime.now().isoformat(),
                'raw_entry': {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'author': entry.get('author', '')
                }
            }
            
            return article
            
        except Exception as e:
            self.logger.warning(f"Error parsing article from {feed_info['name']}: {e}")
            return None
    
    def _should_include_article(self, article: Dict[str, Any]) -> bool:
        """Apply basic filtering to determine if article should be included - permissive like notebook."""
        # Only check for title - be permissive for raw data collection
        if not article.get('title'):
            return False
        
        # Optional: Check minimum content length (but be lenient)
        min_length = self.step_config.get('filtering', {}).get('min_content_length', 10)  # Lower threshold
        content = article.get('content', '') or article.get('summary', '')
        if len(content) < min_length:
            # Still include if it has a title and URL
            if article.get('title') and article.get('url'):
                return True
            return False
        
        return True
    
    def _save_results(self, all_articles: List[Dict[str, Any]], feed_stats: List[Dict[str, Any]]) -> str:
        """Save gathered data to file."""
        try:
            # Use fixed filename within run directory
            filename_template = self.step_config['output']['filename_template']
            # Convert rss_raw_{timestamp}.json to rss_raw.json
            filename = filename_template.replace('_{timestamp}', '').replace('{timestamp}_', '').replace('{timestamp}', '')
            output_path = Path(self.data_paths['raw']) / filename
            
            # Prepare output data
            output_data = {
                'metadata': {
                    'collection_timestamp': datetime.now().isoformat(),
                    'total_articles': len(all_articles),
                    'total_feeds_processed': len(feed_stats),
                    'successful_feeds': len([s for s in feed_stats if s['success']]),
                    'failed_feeds': len([s for s in feed_stats if not s['success']]),
                    'step_name': 'rss_gathering',
                    'pipeline_version': self.config_loader.base_config.get('pipeline', {}).get('version', '1.0.0')
                },
                'feed_statistics': feed_stats,
                'articles': all_articles
            }
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(all_articles)} articles to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save RSS gathering results: {e}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """Execute the RSS gathering step."""
        self.logger.info("Starting RSS gathering step")
        
        try:
            all_articles = []
            feed_stats = []
            failed_feeds = 0
            consecutive_failures = 0
            max_consecutive = self.step_config['error_handling']['max_consecutive_failures']
            
            # Process feeds with parallel requests
            settings = self.step_config['settings']
            with ThreadPoolExecutor(max_workers=settings['parallel_requests']) as executor:
                # Submit all feed fetching tasks
                future_to_feed = {
                    executor.submit(self._fetch_feed, feed): feed 
                    for feed in self.rss_feeds
                }
                
                # Process completed tasks
                for future in as_completed(future_to_feed):
                    feed_name, result = future.result()
                    articles = result['articles']
                    stats = result['stats']
                    
                    feed_stats.append(stats)
                    all_articles.extend(articles)
                    
                    if not stats['success']:
                        failed_feeds += 1
                        consecutive_failures += 1
                        
                        # Check if we should stop due to too many consecutive failures
                        if (consecutive_failures >= max_consecutive and 
                            self.step_config['error_handling']['skip_feeds_after_max_failures']):
                            self.logger.critical(f"Too many consecutive failures ({consecutive_failures}), stopping RSS gathering")
                            break
                    else:
                        consecutive_failures = 0
                    
                    # Add delay between requests
                    time.sleep(settings['request_delay_seconds'])
            
            # Save results
            output_file = self._save_results(all_articles, feed_stats)
            
            # Prepare step result
            result = {
                'success': True,
                'step_name': 'rss_gathering',
                'articles_collected': len(all_articles),
                'feeds_processed': len(feed_stats),
                'feeds_successful': len([s for s in feed_stats if s['success']]),
                'feeds_failed': len([s for s in feed_stats if not s['success']]),
                'output_file': output_file,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"RSS gathering completed: {result['articles_collected']} articles from {result['feeds_successful']}/{result['feeds_processed']} feeds")
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'step_name': 'rss_gathering',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.logger.critical("RSS gathering step failed", exception=e)
            return error_result
