"""
Real-Time News Scraping Pipeline
Supports: RSS feeds, NewsAPI
"""
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import feedparser
from bs4 import BeautifulSoup

from models import NewsArticle, db
from config import Config
from utils.helpers import normalize_article, stable_id_from_url
from services.sentiment_service import analyze_sentiment
from services.fake_news_service import fake_news_detector


class NewsScrapingService:
    """Service for scraping news from various sources"""
    
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.news_api_base = "https://newsapi.org/v2"
    
    def fetch_from_newsapi(
        self,
        category: str = "general",
        country: str = "us",
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI"""
        try:
            url = f"{self.news_api_base}/top-headlines"
            params = {
                "category": category,
                "country": country,
                "pageSize": page_size,
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            normalized = []
            
            for article in articles:
                normalized_article = normalize_article(article)
                normalized_article["category"] = category
                normalized.append(normalized_article)
            
            return normalized
            
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []
    
    def fetch_from_rss(self, rss_url: str, category: str = "general") -> List[Dict[str, Any]]:
        """Fetch news from RSS feed"""
        try:
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:50]:  # Limit to 50 entries
                article = {
                    "id": stable_id_from_url(entry.get("link", "")),
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "imageUrl": None,
                    "publishedAt": entry.get("published", ""),
                    "source": feed.feed.get("title", "RSS Feed"),
                    "author": entry.get("author", ""),
                    "category": category
                }
                
                # Try to extract image from content
                if hasattr(entry, 'content'):
                    for content in entry.content:
                        soup = BeautifulSoup(content.value, 'html.parser')
                        img = soup.find('img')
                        if img and img.get('src'):
                            article["imageUrl"] = img['src']
                            break
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error fetching from RSS: {e}")
            return []
    
    def scrape_all_sources(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """Scrape from all available sources"""
        if categories is None:
            categories = ["general", "technology", "business", "sports", "entertainment", "health", "science"]
        
        all_articles = []
        
        # Fetch from NewsAPI for each category
        for category in categories:
            articles = self.fetch_from_newsapi(category=category, country="us", page_size=20)
            all_articles.extend(articles)
        
        # Add popular RSS feeds (example)
        rss_feeds = [
            # Add your RSS feeds here
            # {"url": "https://rss.cnn.com/rss/edition.rss", "category": "general"},
        ]
        
        for feed_config in rss_feeds:
            articles = self.fetch_from_rss(feed_config["url"], feed_config["category"])
            all_articles.extend(articles)
        
        return all_articles
    
    def store_articles(self, articles: List[Dict[str, Any]], analyze_sentiment_flag: bool = True):
        """Store articles in database with sentiment and fake news analysis"""
        stored_count = 0
        
        for article_data in articles:
            try:
                news_id = article_data.get("id") or stable_id_from_url(article_data.get("url", ""))
                
                # Check if article already exists
                existing = NewsArticle.query.filter_by(news_id=news_id).first()
                if existing:
                    continue
                
                # Parse published date
                from utils.helpers import parse_datetime
                published_at = parse_datetime(article_data.get("publishedAt"))
                if not published_at:
                    published_at = datetime.utcnow()
                
                # Analyze sentiment
                sentiment = None
                if analyze_sentiment_flag:
                    text = article_data.get("description") or article_data.get("title") or ""
                    sentiment = analyze_sentiment(text)
                
                # Predict fake news
                fake_prediction, fake_confidence = fake_news_detector.predict(article_data)
                fake_score = fake_confidence if fake_prediction == 'fake' else (1 - fake_confidence)
                
                # Create article
                article = NewsArticle(
                    news_id=news_id,
                    title=article_data.get("title", ""),
                    description=article_data.get("description"),
                    content=article_data.get("content"),
                    url=article_data.get("url", ""),
                    image_url=article_data.get("imageUrl"),
                    source=article_data.get("source", ""),
                    author=article_data.get("author"),
                    category=article_data.get("category", "general"),
                    sentiment=sentiment,
                    published_at=published_at,
                    fake_news_score=fake_score,
                    fake_news_prediction=fake_prediction
                )
                
                db.session.add(article)
                stored_count += 1
                
            except Exception as e:
                print(f"Error storing article: {e}")
                continue
        
        try:
            db.session.commit()
            print(f"Stored {stored_count} new articles")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing articles: {e}")
        
        return stored_count
    
    def scrape_and_store(self, categories: List[str] = None) -> int:
        """Main method: scrape articles and store in database"""
        articles = self.scrape_all_sources(categories)
        return self.store_articles(articles, analyze_sentiment_flag=True)


# Global instance
scraping_service = NewsScrapingService()

