"""
Data collection module for Bit-by-Bit Pipeline.
Handles RSS feeds, GitHub trending, and stock data collection.
"""

from .rss_gathering import RSSGatheringStep
from .github_trending import GitHubTrendingCollector
from .stock_data import StockDataCollector

__all__ = [
    'RSSGatheringStep',
    'GitHubTrendingCollector', 
    'StockDataCollector'
]
