"""
Guardian API Data Collector
Fetches tech news from The Guardian API
"""

import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GuardianCollector:
    def __init__(self):
        self.api_key = os.getenv('GUARDIAN_API_KEY')
        self.base_url = 'https://content.guardianapis.com/search'
        
        if not self.api_key:
            raise ValueError("GUARDIAN_API_KEY not found in environment variables")
    
    def fetch_articles(self, 
                      query: str = "technology",
                      section: str = "technology",
                      days_back: int = 7,
                      page_size: int = 20,
                      order_by: str = "newest") -> List[Dict]:
        """
        Fetch articles from Guardian API
        
        Args:
            query: Search terms (e.g., "artificial intelligence", "startup")
            section: Section to search (technology, business, science)
            days_back: How many days back to search
            page_size: Number of articles to fetch (max 50)
            order_by: Sort by newest, oldest, or relevance
        
        Returns:
            List of article dictionaries
        """
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        params = {
            'q': query,
            'section': section,
            'from-date': from_date.strftime('%Y-%m-%d'),
            'to-date': to_date.strftime('%Y-%m-%d'),
            'order-by': order_by,
            'page-size': min(page_size, 50),  # API limit is 50
            'show-fields': 'all',
            'api-key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('response', {}).get('results', [])
            
            # Clean and structure the data
            cleaned_articles = []
            for article in articles:
                cleaned_article = {
                    'title': article.get('webTitle', ''),
                    'url': article.get('webUrl', ''),
                    'section': article.get('sectionName', ''),
                    'published': article.get('webPublicationDate', ''),
                    'summary': article.get('fields', {}).get('trailText', ''),
                    'content': article.get('fields', {}).get('body', ''),
                    'thumbnail': article.get('fields', {}).get('thumbnail', ''),
                    'tags': [tag.get('webTitle', '') for tag in article.get('tags', [])]
                }
                cleaned_articles.append(cleaned_article)
            
            return cleaned_articles
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def get_tech_news(self, days_back: int = 1) -> List[Dict]:
        """Get general tech news"""
        return self.fetch_articles(
            query="technology",
            section="technology",
            days_back=days_back
        )
    
    def get_ai_news(self, days_back: int = 1) -> List[Dict]:
        """Get AI-related news"""
        return self.fetch_articles(
            query="artificial intelligence OR machine learning OR AI",
            section="technology",
            days_back=days_back
        )
    
    def get_startup_news(self, days_back: int = 1) -> List[Dict]:
        """Get startup and business tech news"""
        return self.fetch_articles(
            query="startup OR venture capital OR funding",
            section="business",
            days_back=days_back
        )
    
    def get_science_tech(self, days_back: int = 1) -> List[Dict]:
        """Get science and research tech news"""
        return self.fetch_articles(
            query="technology",
            section="science",
            days_back=days_back
        )

def test_guardian_api():
    """Test function to verify API is working"""
    try:
        collector = GuardianCollector()
        
        print("🔍 Testing Guardian API...")
        print(f"API Key: {'✅ Found' if collector.api_key else '❌ Missing'}")
        
        # Test basic tech news
        print("\n📰 Fetching tech news...")
        articles = collector.get_tech_news(days_back=1)
        
        if articles:
            print(f"✅ Successfully fetched {len(articles)} articles")
            print("\n📋 Sample articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"{i}. {article['title']}")
                print(f"   Published: {article['published']}")
                print(f"   Section: {article['section']}")
                print(f"   URL: {article['url']}")
                print()
        else:
            print("❌ No articles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_guardian_api()
