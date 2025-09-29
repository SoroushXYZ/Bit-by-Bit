"""
Stock Data Collection Module

This module handles collecting stock data from various sources with fallback support.
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.utils.env_loader import EnvLoader


class StockDataCollector:
    """Collects stock data from various sources with fallback support."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the stock data collector."""
        self.config_loader = config_loader
        self.logger = get_logger()
        
        # Load stock data specific config
        self.config = self.config_loader.get_step_config('stock_data')
        
        # Load environment variables for API keys
        self.env_loader = EnvLoader()
        
        # Set random seed for reproducible results
        random.seed(42)
        
        self.logger.info("Stock data collector initialized")
    
    def _get_available_sources(self) -> List[str]:
        """Get list of available data sources based on API keys."""
        available_sources = []
        
        for source_name, source_config in self.config['data_sources'].items():
            if not source_config.get('enabled', False):
                continue
                
            if source_name == 'yahoo_finance':
                # Yahoo Finance doesn't need API key
                available_sources.append(source_name)
            elif self.env_loader.is_service_available(source_name):
                available_sources.append(source_name)
            else:
                self.logger.warning(f"Source {source_name} not available (no API key)")
        
        # Sort by priority
        available_sources.sort(key=lambda x: self.config['data_sources'][x].get('priority', 999))
        
        self.logger.info(f"Available data sources: {available_sources}")
        return available_sources
    
    def _fetch_from_finnhub(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Finnhub API."""
        api_key = self.env_loader.get_api_key('finnhub')
        if not api_key:
            return None
        
        base_url = self.config['data_sources']['finnhub']['base_url']
        stocks_data = {}
        
        try:
            for symbol in symbols:
                self.logger.info(f"Fetching {symbol} from Finnhub...")
                
                # Get quote data
                quote_url = f"{base_url}/quote"
                quote_params = {
                    'symbol': symbol,
                    'token': api_key
                }
                
                quote_response = requests.get(
                    quote_url, 
                    params=quote_params,
                    timeout=self.config['data_sources']['finnhub']['timeout_seconds']
                )
                
                if quote_response.status_code == 200:
                    quote_data = quote_response.json()
                    
                    # Get company profile
                    profile_url = f"{base_url}/stock/profile2"
                    profile_params = {
                        'symbol': symbol,
                        'token': api_key
                    }
                    
                    profile_response = requests.get(
                        profile_url,
                        params=profile_params,
                        timeout=self.config['data_sources']['finnhub']['timeout_seconds']
                    )
                    
                    profile_data = profile_response.json() if profile_response.status_code == 200 else {}
                    
                    # Combine data
                    stocks_data[symbol] = {
                        'symbol': symbol,
                        'name': profile_data.get('name', symbol),
                        'current_price': quote_data.get('c', 0),
                        'price_change': quote_data.get('d', 0),
                        'price_change_percent': quote_data.get('dp', 0),
                        'high': quote_data.get('h', 0),
                        'low': quote_data.get('l', 0),
                        'open': quote_data.get('o', 0),
                        'previous_close': quote_data.get('pc', 0),
                        'volume': quote_data.get('v', 0),
                        'market_cap': profile_data.get('marketCapitalization', 0),
                        'sector': profile_data.get('finnhubIndustry', 'Unknown'),
                        'country': profile_data.get('country', 'Unknown'),
                        'source': 'finnhub',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.logger.info(f"✅ {symbol}: ${quote_data.get('c', 0):.2f} ({quote_data.get('dp', 0):+.2f}%)")
                    
                else:
                    self.logger.warning(f"❌ Failed to fetch {symbol} from Finnhub: {quote_response.status_code}")
                
                # Rate limiting
                time.sleep(1)
            
            return stocks_data
            
        except Exception as e:
            self.logger.error(f"Finnhub API error: {e}")
            return None
    
    def _fetch_from_alpha_vantage(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Alpha Vantage API."""
        api_key = self.env_loader.get_api_key('alpha_vantage')
        if not api_key:
            return None
        
        base_url = self.config['data_sources']['alpha_vantage']['base_url']
        stocks_data = {}
        
        try:
            for symbol in symbols:
                self.logger.info(f"Fetching {symbol} from Alpha Vantage...")
                
                # Get quote data
                quote_url = base_url
                quote_params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                }
                
                quote_response = requests.get(
                    quote_url,
                    params=quote_params,
                    timeout=self.config['data_sources']['alpha_vantage']['timeout_seconds']
                )
                
                if quote_response.status_code == 200:
                    quote_data = quote_response.json()
                    
                    if 'Global Quote' in quote_data:
                        quote = quote_data['Global Quote']
                        
                        stocks_data[symbol] = {
                            'symbol': symbol,
                            'name': symbol,  # Alpha Vantage doesn't provide company name in quote
                            'current_price': float(quote.get('05. price', 0)),
                            'price_change': float(quote.get('09. change', 0)),
                            'price_change_percent': float(quote.get('10. change percent', 0).replace('%', '')),
                            'high': float(quote.get('03. high', 0)),
                            'low': float(quote.get('04. low', 0)),
                            'open': float(quote.get('02. open', 0)),
                            'previous_close': float(quote.get('08. previous close', 0)),
                            'volume': int(quote.get('06. volume', 0)),
                            'source': 'alpha_vantage',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"✅ {symbol}: ${float(quote.get('05. price', 0)):.2f} ({float(quote.get('10. change percent', 0).replace('%', '')):+.2f}%)")
                    else:
                        self.logger.warning(f"❌ No data for {symbol} from Alpha Vantage")
                else:
                    self.logger.warning(f"❌ Failed to fetch {symbol} from Alpha Vantage: {quote_response.status_code}")
                
                # Rate limiting (Alpha Vantage is very strict)
                time.sleep(12)  # 5 requests per minute = 12 seconds between requests
            
            return stocks_data
            
        except Exception as e:
            self.logger.error(f"Alpha Vantage API error: {e}")
            return None
    
    def _fetch_from_polygon(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """Fetch stock data from Polygon.io API."""
        api_key = self.env_loader.get_api_key('polygon')
        if not api_key:
            return None
        
        base_url = self.config['data_sources']['polygon']['base_url']
        stocks_data = {}
        
        try:
            for symbol in symbols:
                self.logger.info(f"Fetching {symbol} from Polygon.io...")
                
                # Get quote data
                quote_url = f"{base_url}/v2/aggs/ticker/{symbol}/prev"
                quote_params = {
                    'apikey': api_key
                }
                
                quote_response = requests.get(
                    quote_url,
                    params=quote_params,
                    timeout=self.config['data_sources']['polygon']['timeout_seconds']
                )
                
                if quote_response.status_code == 200:
                    quote_data = quote_response.json()
                    
                    if 'results' in quote_data and quote_data['results']:
                        result = quote_data['results'][0]
                        
                        # Calculate price change
                        current_price = result.get('c', 0)  # close price
                        previous_close = result.get('o', 0)  # open price
                        price_change = current_price - previous_close
                        price_change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
                        
                        stocks_data[symbol] = {
                            'symbol': symbol,
                            'name': symbol,  # Polygon doesn't provide company name in this endpoint
                            'current_price': current_price,
                            'price_change': price_change,
                            'price_change_percent': price_change_percent,
                            'high': result.get('h', 0),
                            'low': result.get('l', 0),
                            'open': result.get('o', 0),
                            'previous_close': previous_close,
                            'volume': result.get('v', 0),
                            'source': 'polygon',
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        self.logger.info(f"✅ {symbol}: ${current_price:.2f} ({price_change_percent:+.2f}%)")
                    else:
                        self.logger.warning(f"❌ No data for {symbol} from Polygon.io")
                else:
                    self.logger.warning(f"❌ Failed to fetch {symbol} from Polygon.io: {quote_response.status_code}")
                
                # Rate limiting
                time.sleep(1)
            
            return stocks_data
            
        except Exception as e:
            self.logger.error(f"Polygon.io API error: {e}")
            return None
    
    def _create_fallback_data(self) -> Dict[str, Any]:
        """Create fallback stock data when all sources fail."""
        self.logger.warning("🔄 All stock data sources failed, using fallback data")
        
        fallback_data = {}
        companies = self.config['companies']
        
        for company_name, company_info in companies.items():
            symbol = company_info['symbol']
            # Generate some realistic-looking fallback data
            base_price = random.uniform(50, 500)
            change = random.uniform(-10, 10)
            change_percent = (change / base_price) * 100
            
            fallback_data[symbol] = {
                'symbol': symbol,
                'name': company_info['name'],
                'current_price': round(base_price, 2),
                'price_change': round(change, 2),
                'price_change_percent': round(change_percent, 2),
                'high': round(base_price + random.uniform(0, 5), 2),
                'low': round(base_price - random.uniform(0, 5), 2),
                'open': round(base_price - change, 2),
                'previous_close': round(base_price - change, 2),
                'volume': random.randint(1000000, 10000000),
                'market_cap': random.randint(100000000000, 3000000000000),
                'sector': company_info['sector'],
                'source': 'fallback',
                'timestamp': datetime.now().isoformat(),
                'note': 'Data unavailable - using fallback values'
            }
        
        return fallback_data
    
    def _save_data(self, data: Dict[str, Any], filename_template: str) -> str:
        """Save stock data to file."""
        try:
            # Create output directory
            output_dir = Path('data/raw')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = filename_template.format(timestamp=timestamp)
            
            output_path = output_dir / filename
            
            # Save data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Stock data saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save stock data: {e}")
            return ""
    
    def collect(self) -> Dict[str, Any]:
        """Collect stock data from configured sources."""
        try:
            self.logger.info("🚀 Starting stock data collection")
            
            # Get list of companies to fetch
            companies = self.config['companies']
            symbols = [company_info['symbol'] for company_info in companies.values()]
            
            self.logger.info(f"📊 Fetching data for {len(symbols)} companies: {', '.join(symbols)}")
            
            # Get available sources
            available_sources = self._get_available_sources()
            
            if not available_sources:
                self.logger.error("❌ No data sources available")
                return {
                    'success': False,
                    'error': 'No data sources available (no API keys)',
                    'collected_count': 0
                }
            
            # Try each source in priority order
            stocks_data = {}
            successful_sources = 0
            
            for source in available_sources:
                self.logger.info(f"🔄 Trying source: {source}")
                
                if source == 'finnhub':
                    data = self._fetch_from_finnhub(symbols)
                elif source == 'alpha_vantage':
                    data = self._fetch_from_alpha_vantage(symbols)
                elif source == 'polygon':
                    data = self._fetch_from_polygon(symbols)
                else:
                    self.logger.warning(f"Unknown source: {source}")
                    continue
                
                if data:
                    stocks_data.update(data)
                    successful_sources += 1
                    self.logger.info(f"✅ {source} successful: {len(data)} stocks")
                    
                    # If we have data for all symbols, we can stop
                    if len(stocks_data) >= len(symbols):
                        break
                else:
                    self.logger.warning(f"❌ {source} failed")
            
            # If no data collected, use fallback
            if not stocks_data:
                self.logger.warning("🔄 No data collected from any source, using fallback")
                stocks_data = self._create_fallback_data()
            
            # Create final data structure
            final_data = {
                'metadata': {
                    'collection_timestamp': datetime.now().isoformat(),
                    'total_companies': len(companies),
                    'successful_sources': successful_sources,
                    'total_sources_tried': len(available_sources),
                    'data_source': list(set(stock.get('source', 'unknown') for stock in stocks_data.values())),
                    'companies_requested': list(companies.keys())
                },
                'stocks': list(stocks_data.values())
            }
            
            # Save data
            output_file = self._save_data(final_data, self.config['output']['filename_template'])
            
            self.logger.info(f"✅ Stock data collection completed: {len(stocks_data)} stocks from {successful_sources} sources")
            
            return {
                'success': True,
                'collected_count': len(stocks_data),
                'successful_sources': successful_sources,
                'output_file': output_file,
                'data': final_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Stock data collection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'collected_count': 0
            }
