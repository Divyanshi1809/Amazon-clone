"""
User Analytics Service
Tracks: reading time, categories, click-through rates, trending topics
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import func, desc
from collections import defaultdict

from models import UserInteraction, ReadingHistory, NewsArticle, db, User


class AnalyticsService:
    """Service for user and content analytics"""
    
    def get_user_reading_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get reading statistics for a user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total reading time
            history = ReadingHistory.query.filter(
                ReadingHistory.user_id == user_id,
                ReadingHistory.started_at >= cutoff_date
            ).all()
            
            total_seconds = sum(h.time_spent_seconds for h in history)
            total_articles = len(history)
            avg_reading_time = total_seconds / total_articles if total_articles > 0 else 0
            
            # Category breakdown
            category_time = defaultdict(int)
            category_count = defaultdict(int)
            for h in history:
                if h.category:
                    category_time[h.category] += h.time_spent_seconds
                    category_count[h.category] += 1
            
            # Most read categories
            top_categories = sorted(
                category_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                "total_reading_time_seconds": total_seconds,
                "total_reading_time_minutes": round(total_seconds / 60, 2),
                "total_articles_read": total_articles,
                "average_reading_time_seconds": round(avg_reading_time, 2),
                "category_breakdown": {
                    cat: {
                        "count": count,
                        "total_time_seconds": category_time[cat],
                        "total_time_minutes": round(category_time[cat] / 60, 2)
                    }
                    for cat, count in category_count.items()
                },
                "top_categories": [{"category": cat, "count": count} for cat, count in top_categories]
            }
            
        except Exception as e:
            print(f"Error getting user reading stats: {e}")
            return {}
    
    def get_user_interaction_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get interaction statistics for a user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            interactions = UserInteraction.query.filter(
                UserInteraction.user_id == user_id,
                UserInteraction.created_at >= cutoff_date
            ).all()
            
            # Count by type
            type_counts = defaultdict(int)
            for interaction in interactions:
                type_counts[interaction.interaction_type] += 1
            
            # Category breakdown
            category_counts = defaultdict(int)
            for interaction in interactions:
                if interaction.category:
                    category_counts[interaction.category] += 1
            
            return {
                "total_interactions": len(interactions),
                "interactions_by_type": dict(type_counts),
                "interactions_by_category": dict(category_counts),
                "most_interacted_categories": sorted(
                    category_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            print(f"Error getting user interaction stats: {e}")
            return {}
    
    def get_trending_topics(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending topics based on interactions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count interactions per category
            category_counts = db.session.query(
                UserInteraction.category,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.created_at >= cutoff_date,
                UserInteraction.category.isnot(None)
            ).group_by(UserInteraction.category).order_by(desc('count')).limit(limit).all()
            
            return [
                {"category": category, "interaction_count": count}
                for category, count in category_counts
            ]
            
        except Exception as e:
            print(f"Error getting trending topics: {e}")
            return []
    
    def get_sentiment_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get sentiment distribution of news"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            articles = NewsArticle.query.filter(
                NewsArticle.published_at >= cutoff_date,
                NewsArticle.sentiment.isnot(None)
            ).all()
            
            sentiment_counts = defaultdict(int)
            for article in articles:
                sentiment_counts[article.sentiment] += 1
            
            total = len(articles)
            sentiment_percentages = {
                sentiment: round((count / total * 100), 2) if total > 0 else 0
                for sentiment, count in sentiment_counts.items()
            }
            
            return {
                "total_articles": total,
                "sentiment_counts": dict(sentiment_counts),
                "sentiment_percentages": sentiment_percentages
            }
            
        except Exception as e:
            print(f"Error getting sentiment analysis: {e}")
            return {}
    
    def get_click_through_rate(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """Calculate click-through rate"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = UserInteraction.query.filter(
                UserInteraction.created_at >= cutoff_date
            )
            
            if user_id:
                query = query.filter(UserInteraction.user_id == user_id)
            
            interactions = query.all()
            
            # Count clicks vs views
            clicks = sum(1 for i in interactions if i.interaction_type == 'click')
            views = sum(1 for i in interactions if i.interaction_type == 'view')
            
            ctr = (clicks / views * 100) if views > 0 else 0
            
            return {
                "total_clicks": clicks,
                "total_views": views,
                "click_through_rate": round(ctr, 2)
            }
            
        except Exception as e:
            print(f"Error calculating CTR: {e}")
            return {}
    
    def get_fake_news_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics about fake news detection"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            articles = NewsArticle.query.filter(
                NewsArticle.published_at >= cutoff_date,
                NewsArticle.fake_news_prediction.isnot(None)
            ).all()
            
            fake_count = sum(1 for a in articles if a.fake_news_prediction == 'fake')
            real_count = sum(1 for a in articles if a.fake_news_prediction == 'real')
            total = len(articles)
            
            avg_fake_score = sum(a.fake_news_score for a in articles if a.fake_news_score) / total if total > 0 else 0
            
            return {
                "total_analyzed": total,
                "fake_count": fake_count,
                "real_count": real_count,
                "fake_percentage": round((fake_count / total * 100), 2) if total > 0 else 0,
                "average_fake_score": round(avg_fake_score, 3)
            }
            
        except Exception as e:
            print(f"Error getting fake news stats: {e}")
            return {}
    
    def get_comprehensive_analytics(self, user_id: int = None, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data"""
        analytics = {
            "trending_topics": self.get_trending_topics(days=7),
            "sentiment_analysis": self.get_sentiment_analysis(days=days),
            "click_through_rate": self.get_click_through_rate(user_id=user_id, days=days),
            "fake_news_stats": self.get_fake_news_stats(days=days)
        }
        
        if user_id:
            analytics["user_reading_stats"] = self.get_user_reading_stats(user_id, days)
            analytics["user_interaction_stats"] = self.get_user_interaction_stats(user_id, days)
        
        return analytics


# Global instance
analytics_service = AnalyticsService()

