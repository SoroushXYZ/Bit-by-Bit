"""
GitHub Trending Data Collection Module

This module handles collecting trending GitHub repositories from OSS Insight API.
"""

import sys
import json
import time
import requests
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

try:
    from langdetect import detect, LangDetectException
except ImportError:
    detect = None
    LangDetectException = Exception


class GitHubTrendingCollector:
    """Collects trending GitHub repositories from OSS Insight API."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the GitHub trending collector."""
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load GitHub trending specific config
        self.config = self.config_loader.get_step_config('github_trending')
        
        # Load global config for LLM settings
        self.global_config = self.config_loader.global_config
        
        self.logger.info("GitHub trending collector initialized")
    
    def _is_english_text(self, text: str) -> bool:
        """
        Check if text is primarily in English using langdetect or pattern matching.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text appears to be English
        """
        if not text or pd.isna(text):
            return False
        
        try:
            if detect:
                # Use langdetect if available
                detected_lang = detect(str(text))
                return detected_lang == 'en'
        except (LangDetectException, TypeError):
            pass
        
        # Fallback: check for common non-English patterns
        text_str = str(text).lower()
        
        # Common non-English indicators
        non_english_patterns = [
            r'[\u4e00-\u9fff]',  # Chinese characters
            r'[\u3040-\u309f]',  # Hiragana
            r'[\u30a0-\u30ff]',  # Katakana
            r'[\u0400-\u04ff]',  # Cyrillic
            r'[\u0600-\u06ff]',  # Arabic
            r'[\u0590-\u05ff]',  # Hebrew
        ]
        
        # Check for non-English patterns
        for pattern in non_english_patterns:
            if re.search(pattern, text_str):
                return False
        
        # Check for common non-English words/phrases
        non_english_indicators = [
            '中文', '中国', '日本語', '한국어', 'русский', 'français', 'español',
            'deutsch', 'italiano', 'português', '中文版', '日本語版', '한국어판',
            '基于', '使用', '开发', '项目', '工具', '框架', '系统', '应用',
            '開発', 'プロジェクト', 'ツール', 'フレームワーク', 'システム', 'アプリ',
            '개발', '프로젝트', '도구', '프레임워크', '시스템', '애플리케이션'
        ]
        
        for indicator in non_english_indicators:
            if indicator in text_str:
                return False
        
        return True
    
    def _fetch_trending_repos(self) -> Optional[Dict[str, Any]]:
        """
        Fetch trending repositories from OSS Insight API.
        
        Returns:
            dict: API response data or None if failed
        """
        api_config = self.config.get('api', {})
        params = self.config.get('parameters', {})
        
        base_url = api_config.get('base_url', 'https://api.ossinsight.io/v1/trends/repos/')
        timeout = api_config.get('timeout', 30)
        retry_attempts = api_config.get('retry_attempts', 3)
        retry_delay = api_config.get('retry_delay', 1)
        
        # Build request URL
        url = f"{base_url}?period={params.get('period', 'past_24_hours')}&language={params.get('language', 'All')}"
        
        self.logger.info(f"Fetching trending repositories from: {url}")
        
        for attempt in range(retry_attempts):
            try:
                response = requests.get(
                    url, 
                    headers={'Accept': 'application/json'}, 
                    timeout=timeout
                )
                response.raise_for_status()
                
                data = response.json()
                self.logger.info(f"Successfully fetched {len(data.get('data', {}).get('rows', []))} repositories")
                return data
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All API request attempts failed")
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error during API request: {e}")
                return None
        
        return None
    
    def _filter_repositories(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter repositories based on configuration criteria.
        
        Args:
            repos: List of repository data
            
        Returns:
            List of filtered repositories
        """
        filtering_config = self.config.get('filtering', {})
        
        if not repos:
            return []
        
        # Convert to DataFrame for easier filtering
        df = pd.DataFrame(repos)
        
        # Convert stars to numeric
        df['stars_numeric'] = pd.to_numeric(df['stars'], errors='coerce')
        
        original_count = len(df)
        self.logger.info(f"Starting with {original_count} repositories")
        
        # Filter by minimum stars
        min_stars = filtering_config.get('min_stars', 10)
        if min_stars > 0:
            df = df[df['stars_numeric'] >= min_stars]
            self.logger.info(f"After min_stars filter: {len(df)} repositories")
        
        # Filter by English language if enabled
        if filtering_config.get('english_only', True):
            english_mask = df['description'].apply(self._is_english_text)
            df = df[english_mask]
            self.logger.info(f"After English filter: {len(df)} repositories")
        
        # Filter out patterns
        exclude_patterns = filtering_config.get('exclude_patterns', [])
        if exclude_patterns:
            pattern_mask = ~df['description'].str.contains('|'.join(exclude_patterns), case=False, na=False)
            df = df[pattern_mask]
            self.logger.info(f"After exclude patterns filter: {len(df)} repositories")
        
        # Ensure required fields are present
        required_fields = filtering_config.get('required_fields', [])
        for field in required_fields:
            df = df[df[field].notna()]
        self.logger.info(f"After required fields filter: {len(df)} repositories")
        
        # Convert back to list of dicts
        filtered_repos = df.to_dict('records')
        
        self.logger.info(f"Filtering complete: {len(filtered_repos)}/{original_count} repositories kept")
        return filtered_repos
    
    def _fetch_readme_content(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch README content for a repository.
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            
        Returns:
            dict: README information or None if not found
        """
        readme_config = self.config.get('readme', {})
        
        if not readme_config.get('enabled', True):
            return None
        
        timeout = readme_config.get('timeout', 10)
        variants = readme_config.get('variants', ['README.md', 'readme.md'])
        branches = readme_config.get('branches', ['main', 'master'])
        min_length = readme_config.get('min_length', 50)
        max_length = readme_config.get('max_length', 100000)
        
        # Try different README variants and branches
        for branch in branches:
            for variant in variants:
                readme_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{variant}"
                
                try:
                    response = requests.get(readme_url, timeout=timeout)
                    if response.status_code == 200:
                        content = response.text
                        
                        # Check if content meets length requirements
                        if min_length <= len(content) <= max_length:
                            return {
                                'readme_url': readme_url,
                                'readme_content': content,
                                'readme_length': len(content),
                                'status': 'success'
                            }
                except Exception:
                    continue
        
        return {
            'readme_url': None,
            'readme_content': None,
            'readme_length': 0,
            'status': 'not_found'
        }
    
    def _add_readme_data(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add README content to top repositories.
        
        Args:
            repos: List of repository data
            
        Returns:
            List of repositories with README data added
        """
        readme_config = self.config.get('readme', {})
        max_repos = readme_config.get('max_repositories', 10)
        delay = self.config.get('performance', {}).get('delay_between_requests', 0.5)
        
        # Sort by stars and take top N
        repos_with_stars = [r for r in repos if 'stars_numeric' in r or 'stars' in r]
        if not repos_with_stars:
            return repos
        
        # Sort by stars (convert to int for proper sorting)
        for repo in repos_with_stars:
            if 'stars_numeric' not in repo:
                try:
                    repo['stars_numeric'] = int(repo.get('stars', 0))
                except (ValueError, TypeError):
                    repo['stars_numeric'] = 0
        
        top_repos = sorted(repos_with_stars, key=lambda x: x.get('stars_numeric', 0), reverse=True)[:max_repos]
        
        self.logger.info(f"Fetching README content for top {len(top_repos)} repositories")
        
        for i, repo in enumerate(top_repos):
            repo_name = repo.get('repo_name', '')
            if not repo_name:
                continue
            
            self.logger.info(f"Fetching README for {repo_name} ({i+1}/{len(top_repos)})")
            
            readme_info = self._fetch_readme_content(repo_name)
            repo.update(readme_info)
            
            # Add delay between requests
            if i < len(top_repos) - 1:
                time.sleep(delay)
        
        # Count successful README fetches
        successful_readmes = len([r for r in top_repos if r.get('status') == 'success'])
        self.logger.info(f"README fetching complete: {successful_readmes}/{len(top_repos)} successful")
        
        return repos
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect trending GitHub repositories.
        
        Returns:
            dict: Collection results with success status and data
        """
        try:
            self.logger.info("Starting GitHub trending data collection")
            
            # Fetch trending repositories from API
            api_data = self._fetch_trending_repos()
            if not api_data:
                return {
                    'success': False,
                    'error': 'Failed to fetch data from OSS Insight API',
                    'collected_count': 0
                }
            
            # Extract repository data
            repos = api_data.get('data', {}).get('rows', [])
            if not repos:
                return {
                    'success': False,
                    'error': 'No repository data found in API response',
                    'collected_count': 0
                }
            
            # Filter repositories
            filtered_repos = self._filter_repositories(repos)
            
            # Add README data to top repositories
            repos_with_readme = self._add_readme_data(filtered_repos)
            
            # Prepare output data
            output_data = {
                'repositories': repos_with_readme,
                'metadata': {
                    'source': 'oss_insight_api',
                    'api_url': 'https://api.ossinsight.io/v1/trends/repos/',
                    'period': self.config.get('parameters', {}).get('period', 'past_24_hours'),
                    'language': self.config.get('parameters', {}).get('language', 'All'),
                    'total_fetched': len(repos),
                    'total_filtered': len(filtered_repos),
                    'total_with_readme': len(repos_with_readme),
                    'collected_at': datetime.now().isoformat(),
                    'filtering_applied': {
                        'english_only': self.config.get('filtering', {}).get('english_only', True),
                        'min_stars': self.config.get('filtering', {}).get('min_stars', 10),
                        'exclude_patterns': self.config.get('filtering', {}).get('exclude_patterns', [])
                    }
                }
            }
            
            # Save to file if configured
            self._save_output_data(output_data)
            
            result = {
                'success': True,
                'collected_count': len(repos_with_readme),
                'data': output_data,
                'metadata': output_data['metadata']
            }
            
            self.logger.info(f"GitHub trending collection completed: {result['collected_count']} repositories")
            return result
            
        except Exception as e:
            self.logger.error(f"GitHub trending collection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'collected_count': 0
            }
    
    def _save_output_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Save collected data to file.
        
        Args:
            data: Data to save
            
        Returns:
            str: Path to saved file or None if failed
        """
        try:
            output_config = self.config.get('output', {})
            
            if not output_config.get('format') == 'json':
                return None
            
            # Create output directory (run-scoped raw path)
            output_dir = Path(self.config_loader.get_data_paths()['raw'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use fixed filename within run directory
            output_path = output_dir / 'github_trending.json'
            
            # Save data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"GitHub trending data saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save GitHub trending data: {e}")
            return None