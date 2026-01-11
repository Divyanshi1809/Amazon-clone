"""
Smart News Recommendation System using TF-IDF + Cosine Similarity
"""
import pickle
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from models import UserInteraction, ReadingHistory, NewsArticle, db
from config import Config


class RecommendationService:
    """Content-based filtering recommendation system"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.article_vectors = None
        self.article_ids = []
        self.load_or_build_model()
    
    def load_or_build_model(self):
        """Load existing vectorizer or build new one"""
        if os.path.exists(Config.RECOMMENDATION_VECTORIZER_PATH):
            try:
                with open(Config.RECOMMENDATION_VECTORIZER_PATH, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            except Exception as e:
                print(f"Error loading vectorizer: {e}")
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95
                )
    
    def save_model(self):
        """Save the vectorizer"""
        Config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(Config.RECOMMENDATION_VECTORIZER_PATH, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def prepare_text(self, article: Dict[str, Any]) -> str:
        """Combine title, description, and content for TF-IDF"""
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        content = article.get('content', '') or ''
        return f"{title} {description} {content}".strip()
    
    def build_user_profile(self, user_id: int) -> Optional[np.ndarray]:
        """Build user profile based on reading history and interactions"""
        try:
            # Get user's reading history
            history = ReadingHistory.query.filter_by(user_id=user_id).all()
            interactions = UserInteraction.query.filter_by(user_id=user_id).all()
            
            if not history and not interactions:
                return None
            
            # Get news IDs user has interacted with
            news_ids = set()
            for h in history:
                if h.time_spent_seconds > 30:  # Only consider if read for > 30 seconds
                    news_ids.add(h.news_id)
            for i in interactions:
                if i.interaction_type in ['click', 'view', 'like']:
                    news_ids.add(i.news_id)
            
            if not news_ids:
                return None
            
            # Get articles from database or from recent news
            articles = []
            for news_id in list(news_ids)[:50]:  # Limit to 50 articles
                article = NewsArticle.query.filter_by(news_id=news_id).first()
                if article:
                    articles.append({
                        'title': article.title or '',
                        'description': article.description or '',
                        'content': article.content or ''
                    })
            
            if not articles:
                return None
            
            # Prepare texts and compute weighted average
            texts = [self.prepare_text(a) for a in articles]
            if not any(texts):
                return None
            
            # Fit vectorizer on user's articles and transform
            user_vectors = self.vectorizer.fit_transform(texts)
            # Average the vectors to get user profile
            user_profile = np.mean(user_vectors.toarray(), axis=0)
            return user_profile.reshape(1, -1)
            
        except Exception as e:
            print(f"Error building user profile: {e}")
            return None
    
    def get_category_preferences(self, user_id: int) -> Dict[str, float]:
        """Get user's category preferences based on interactions"""
        try:
            interactions = UserInteraction.query.filter_by(user_id=user_id).all()
            history = ReadingHistory.query.filter_by(user_id=user_id).all()
            
            category_scores = {}
            
            # Weight interactions
            for interaction in interactions:
                if interaction.category:
                    category_scores[interaction.category] = category_scores.get(interaction.category, 0) + 1
            
            # Weight reading time
            for h in history:
                if h.category and h.time_spent_seconds > 30:
                    category_scores[h.category] = category_scores.get(h.category, 0) + (h.time_spent_seconds / 60)
            
            # Normalize scores
            total = sum(category_scores.values())
            if total > 0:
                return {k: v / total for k, v in category_scores.items()}
            return {}
            
        except Exception as e:
            print(f"Error getting category preferences: {e}")
            return {}
    
    def fit_on_articles(self, articles: List[Dict[str, Any]]):
        """Fit TF-IDF vectorizer on articles"""
        texts = [self.prepare_text(article) for article in articles]
        if texts:
            self.article_vectors = self.vectorizer.fit_transform(texts)
            self.save_model()
    
    def recommend(
        self,
        user_id: int,
        candidate_articles: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend articles based on user profile and content similarity
        """
        if not candidate_articles:
            return []
        
        try:
            # Build user profile
            user_profile = self.build_user_profile(user_id)
            category_prefs = self.get_category_preferences(user_id)
            
            # Prepare candidate texts
            candidate_texts = [self.prepare_text(a) for a in candidate_articles]
            
            # Transform candidates
            if hasattr(self.vectorizer, 'vocabulary_') and self.vectorizer.vocabulary_:
                candidate_vectors = self.vectorizer.transform(candidate_texts)
            else:
                # Fit on candidates if vectorizer not fitted
                candidate_vectors = self.vectorizer.fit_transform(candidate_texts)
            
            scores = []
            
            for idx, article in enumerate(candidate_articles):
                score = 0.0
                
                # Content similarity score
                if user_profile is not None:
                    candidate_vec = candidate_vectors[idx:idx+1]
                    similarity = cosine_similarity(user_profile, candidate_vec)[0][0]
                    score += similarity * 0.7  # 70% weight on content
                
                # Category preference score
                article_category = article.get('category', '').lower()
                if article_category and article_category in category_prefs:
                    score += category_prefs[article_category] * 0.3  # 30% weight on category
                
                scores.append((score, article))
            
            # Sort by score descending
            scores.sort(key=lambda x: x[0], reverse=True)
            
            # Return top N
            return [article for _, article in scores[:top_n]]
            
        except Exception as e:
            print(f"Error in recommendation: {e}")
            # Fallback: return recent articles
            return candidate_articles[:top_n]
    
    def get_trending_articles(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending articles based on interaction counts"""
        from datetime import datetime, timedelta
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count interactions per news_id
            interactions = UserInteraction.query.filter(
                UserInteraction.created_at >= cutoff_date
            ).all()
            
            news_counts = {}
            for interaction in interactions:
                news_counts[interaction.news_id] = news_counts.get(interaction.news_id, 0) + 1
            
            # Sort by count and get top news_ids
            sorted_news = sorted(news_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [news_id for news_id, _ in sorted_news]
            
        except Exception as e:
            print(f"Error getting trending articles: {e}")
            return []


# Global instance
recommendation_service = RecommendationService()

