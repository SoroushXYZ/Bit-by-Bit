"""
Data Filler for Grid Blueprint

Fills the grid blueprint with actual data from various sources:
- News data (headlines and secondary)
- GitHub trending data
- Stock data
- Day number calculation
- Branding order assignment
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


class GridDataFiller:
    """Fills grid blueprint with actual data from various sources."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.logger = get_logger()
        self.config = self.config_loader.get_step_config('gridding')
        self.data_paths = self.config_loader.get_data_paths()
        self.global_config = self.config_loader.global_config
        
        # Get starting timestamp for day calculation
        self.starting_timestamp = self.global_config.get('global', {}).get('starting_timestamp', 1758362400)
    
    def fill_blueprint(self, blueprint_path: str) -> Dict[str, Any]:
        """Fill the grid blueprint with actual data."""
        try:
            self.logger.info(f"🎯 Starting data filling for blueprint: {blueprint_path}")
            
            # Load blueprint
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                blueprint = json.load(f)
            
            # Load data sources
            news_data = self._load_news_data()
            github_data = self._load_github_data()
            stock_data = self._load_stock_data()
            
            # Fill components with data
            self._fill_headlines(blueprint, news_data)
            self._fill_quick_links(blueprint, news_data)
            self._fill_github_repos(blueprint, github_data)
            self._fill_stocks(blueprint, stock_data)
            self._fill_branding_order(blueprint)
            self._fill_day_number(blueprint)
            self._fill_bits(blueprint)
            
            # Save filled blueprint
            output_path = self._save_filled_blueprint(blueprint, blueprint_path)
            
            self.logger.info(f"✅ Data filling completed: {output_path}")
            return {
                'success': True,
                'filled_blueprint_path': output_path,
                'components_filled': len(blueprint['components'])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data filling failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_news_data(self) -> Dict[str, Any]:
        """Load processed news data."""
        try:
            # Try to load summarized content first (most processed)
            summarized_path = Path(self.data_paths['processed']) / 'summarized_content_20250929_023403.json'
            if summarized_path.exists():
                with open(summarized_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert summarized format to articles format
                    articles = []
                    if 'summaries' in data:
                        # Add headlines
                        for item in data['summaries'].get('headlines', []):
                            articles.append({
                                'title': item.get('original_title', ''),
                                'summary': item.get('summary', ''),
                                'source': 'RSS',
                                'url': item.get('original_url', ''),
                                'quality_score': 85  # Headlines are high quality
                            })
                        # Add secondary articles
                        for item in data['summaries'].get('secondary', []):
                            articles.append({
                                'title': item.get('original_title', ''),
                                'summary': item.get('summary', ''),
                                'source': 'RSS',
                                'url': item.get('original_url', ''),
                                'quality_score': 75  # Secondary articles
                            })
                    return {'articles': articles}
            
            # Fallback to prioritized content
            prioritized_path = Path(self.data_paths['processed']) / 'prioritized_content_20250929_023328.json'
            if prioritized_path.exists():
                with open(prioritized_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert prioritized format to articles format
                    articles = []
                    if 'articles' in data:
                        for item in data['articles']:
                            articles.append({
                                'title': item.get('title', ''),
                                'summary': item.get('summary', ''),
                                'source': item.get('source', 'RSS'),
                                'url': item.get('url', ''),
                                'quality_score': item.get('quality_score', 0)
                            })
                    return {'articles': articles}
            
            # Fallback to quality scored content
            quality_path = Path(self.data_paths['processed']) / 'quality_scored_content_20250929_023316.json'
            if quality_path.exists():
                with open(quality_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert quality scored format to articles format
                    articles = []
                    if 'articles' in data:
                        for item in data['articles']:
                            articles.append({
                                'title': item.get('title', ''),
                                'summary': item.get('summary', ''),
                                'source': item.get('source', 'RSS'),
                                'url': item.get('url', ''),
                                'quality_score': item.get('quality_score', 0)
                            })
                    return {'articles': articles}
            
            self.logger.warning("⚠️  No news data found, using empty data")
            return {'articles': []}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load news data: {e}")
            return {'articles': []}
    
    def _load_github_data(self) -> Dict[str, Any]:
        """Load GitHub trending data."""
        try:
            github_path = Path(self.data_paths['processed']) / 'github_trending_20250929_023411.json'
            if github_path.exists():
                with open(github_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            self.logger.warning("⚠️  No GitHub data found, using empty data")
            return {'repositories': []}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load GitHub data: {e}")
            return {'repositories': []}
    
    def _load_stock_data(self) -> Dict[str, Any]:
        """Load stock data."""
        try:
            stock_path = Path(self.data_paths['raw']) / 'stock_data_20250929_023004.json'
            if stock_path.exists():
                with open(stock_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            self.logger.warning("⚠️  No stock data found, using empty data")
            return {'stocks': []}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load stock data: {e}")
            return {'stocks': []}
    
    def _fill_headlines(self, blueprint: Dict[str, Any], news_data: Dict[str, Any]):
        """Fill headline components with news data."""
        articles = news_data.get('articles', [])
        headline_components = [comp for comp in blueprint['components'] if comp['type'] == 'headline']
        
        self.logger.info(f"📰 Filling {len(headline_components)} headlines with {len(articles)} articles")
        
        for i, component in enumerate(headline_components):
            if i < len(articles):
                article = articles[i]
                component['data'] = {
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'quality_score': article.get('quality_score', 0)
                }
                self.logger.info(f"  ✅ Filled headline_{i+1}: {article.get('title', '')[:50]}...")
            else:
                self.logger.warning(f"  ⚠️  No article available for headline_{i+1}")
    
    def _fill_quick_links(self, blueprint: Dict[str, Any], news_data: Dict[str, Any]):
        """Fill quick link components with remaining news data."""
        articles = news_data.get('articles', [])
        quick_link_components = [comp for comp in blueprint['components'] if comp['type'] == 'quick_link']
        
        # Skip first 4 articles (used for headlines)
        remaining_articles = articles[4:]
        
        self.logger.info(f"🔗 Filling {len(quick_link_components)} quick links with {len(remaining_articles)} remaining articles")
        
        for i, component in enumerate(quick_link_components):
            if i < len(remaining_articles):
                article = remaining_articles[i]
                component['data'] = {
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'quality_score': article.get('quality_score', 0)
                }
                self.logger.info(f"  ✅ Filled quick_link_{i+1}: {article.get('title', '')[:50]}...")
            else:
                self.logger.warning(f"  ⚠️  No article available for quick_link_{i+1}")
    
    def _fill_github_repos(self, blueprint: Dict[str, Any], github_data: Dict[str, Any]):
        """Fill GitHub repository components."""
        repos = github_data.get('repositories', [])
        github_components = [comp for comp in blueprint['components'] if comp['type'] == 'github_repo']
        
        self.logger.info(f"🐙 Filling {len(github_components)} GitHub repos with {len(repos)} repositories")
        
        for i, component in enumerate(github_components):
            if i < len(repos):
                repo = repos[i]
                component['data'] = {
                    'name': repo.get('repo_name', ''),
                    'description': repo.get('summary', ''),
                    'url': repo.get('github_url', ''),
                    'stars': repo.get('stars', 0),
                    'language': repo.get('primary_language', ''),
                    'rank': repo.get('rank', i + 1)
                }
                self.logger.info(f"  ✅ Filled github_repo_{i+1}: {repo.get('repo_name', '')}")
            else:
                self.logger.warning(f"  ⚠️  No repository available for github_repo_{i+1}")
    
    def _fill_stocks(self, blueprint: Dict[str, Any], stock_data: Dict[str, Any]):
        """Fill stock components (max 5 stocks)."""
        stocks = stock_data.get('stocks', [])[:5]  # Limit to first 5 stocks
        stock_components = [comp for comp in blueprint['components'] if comp['type'] == 'stock']
        
        self.logger.info(f"📈 Filling {len(stock_components)} stocks with {len(stocks)} stock data")
        
        for i, component in enumerate(stock_components):
            if i < len(stocks):
                stock = stocks[i]
                component['data'] = {
                    'symbol': stock.get('symbol', ''),
                    'price': stock.get('current_price', 0.0),
                    'change': stock.get('price_change', 0.0),
                    'change_percent': stock.get('price_change_percent', 0.0),
                    'company_name': stock.get('name', '')
                }
                self.logger.info(f"  ✅ Filled stock_{i+1}: {stock.get('symbol', '')} - ${stock.get('current_price', 0.0)}")
            else:
                self.logger.warning(f"  ⚠️  No stock data available for stock_{i+1}")
    
    def _fill_branding_order(self, blueprint: Dict[str, Any]):
        """Assign order IDs to branding components based on reading order (top to bottom, left to right)."""
        branding_components = [comp for comp in blueprint['components'] if comp['type'] == 'branding']
        
        # Sort by row (top to bottom), then by column (left to right)
        branding_components.sort(key=lambda x: (x['position']['row'], x['position']['column']))
        
        self.logger.info(f"🏷️  Assigning branding order to {len(branding_components)} components")
        
        for i, component in enumerate(branding_components):
            component['data'] = {
                'order_id': i + 1
            }
            self.logger.info(f"  ✅ Branding at row {component['position']['row']}, col {component['position']['column']} -> order {i + 1}")
    
    def _fill_day_number(self, blueprint: Dict[str, Any]):
        """Fill day number component with calculated day."""
        # Look for day number components with different possible type names
        day_components = []
        for comp in blueprint['components']:
            if comp['type'] in ['dayNumber', 'day_number', 'day'] or 'day' in comp['id'].lower():
                day_components.append(comp)
        
        if not day_components:
            self.logger.warning("⚠️  No day number components found")
            return
        
        # Calculate current day number
        current_timestamp = int(datetime.now().timestamp())
        days_passed = (current_timestamp - self.starting_timestamp) // 86400  # 86400 seconds in a day
        
        for component in day_components:
            component['data'] = {
                'day_number': days_passed
            }
            self.logger.info(f"  ✅ Day number: {days_passed} (days since {self.starting_timestamp})")
    
    def _fill_bits(self, blueprint: Dict[str, Any]):
        """Fill bit components (already have placeholder data)."""
        bit_components = [comp for comp in blueprint['components'] if comp['type'] == 'bit']
        
        self.logger.info(f"🔢 Found {len(bit_components)} bit components (already filled)")
        
        # Bits are already filled with placeholder data, no need to modify
        for component in bit_components:
            if not component.get('data'):
                component['data'] = {
                    'content': 'bit'
                }
    
    def _save_filled_blueprint(self, blueprint: Dict[str, Any], original_path: str) -> str:
        """Save the filled blueprint to a new file."""
        try:
            # Create output filename
            original_path = Path(original_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"filled_grid_blueprint_{timestamp}.json"
            output_path = Path(self.data_paths['output']) / output_filename
            
            # Save blueprint
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Filled blueprint saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save filled blueprint: {e}")
            raise
