"""
News routes - Fetch news, recommendations, fake news detection, trends, sentiment
"""
from flask import Blueprint, jsonify, request
from typing import Dict, Any, List
from models import NewsArticle, db
from services.news_service import fetch_latest_news
from services.sentiment_service import analyze_sentiment, analyze_sentiment_detailed
from services.recommendation_service import recommendation_service
from services.fake_news_service import fake_news_detector
from services.scraping_service import scraping_service
from services.analytics_service import analytics_service
from utils.auth import token_required
from utils.helpers import normalize_article, analyze_articles_sentiment

news_bp = Blueprint("news_bp", __name__)


@news_bp.route("/news", methods=["GET"])
def get_news():
    """Fetch news articles with optional filters"""
    try:
        category = request.args.get("category", "general")
        country = request.args.get("country", "us")
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 20))
        
        # Try to get from database first
        articles = NewsArticle.query.filter_by(category=category).order_by(
            NewsArticle.published_at.desc()
        ).limit(page_size).offset((page - 1) * page_size).all()
        
        if articles:
            return jsonify({
                "articles": [a.to_dict() for a in articles],
                "total": NewsArticle.query.filter_by(category=category).count(),
                "page": page,
                "pageSize": page_size
            }), 200
        
        # Fallback to API if database empty
        news = fetch_latest_news(category=category, country=country)
        enriched = analyze_articles_sentiment(news)
        
        return jsonify({
            "articles": enriched,
            "total": len(enriched),
            "page": page,
            "pageSize": page_size
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching news: {str(e)}"}), 500


@news_bp.route("/news/<news_id>", methods=["GET"])
def get_news_by_id(news_id):
    """Get a specific news article by ID"""
    try:
        article = NewsArticle.query.filter_by(news_id=news_id).first()
        if article:
            return jsonify({"article": article.to_dict()}), 200
        return jsonify({"message": "Article not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error fetching article: {str(e)}"}), 500


@news_bp.route("/news/search", methods=["GET"])
def search_news():
    """Search news articles"""
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"message": "Search query required"}), 400
        
        # Search in database
        articles = NewsArticle.query.filter(
            (NewsArticle.title.contains(query)) |
            (NewsArticle.description.contains(query))
        ).limit(50).all()
        
        if articles:
            return jsonify({
                "articles": [a.to_dict() for a in articles],
                "query": query,
                "total": len(articles)
            }), 200
        
        # Fallback to API search
        from services.news_service import fetch_latest_news
        news = fetch_latest_news()
        filtered = [
            n for n in news
            if query.lower() in (n.get("title", "") + " " + n.get("description", "")).lower()
        ]
        enriched = analyze_articles_sentiment(filtered[:50])
        
        return jsonify({
            "articles": enriched,
            "query": query,
            "total": len(enriched)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error searching news: {str(e)}"}), 500


@news_bp.route("/news/category/<category>", methods=["GET"])
def get_news_by_category(category):
    """Get news by category"""
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 20))
        
        articles = NewsArticle.query.filter_by(category=category).order_by(
            NewsArticle.published_at.desc()
        ).limit(page_size).offset((page - 1) * page_size).all()
        
        if articles:
            return jsonify({
                "articles": [a.to_dict() for a in articles],
                "category": category,
                "total": NewsArticle.query.filter_by(category=category).count()
            }), 200
        
        # Fallback to API
        news = fetch_latest_news(category=category)
        enriched = analyze_articles_sentiment(news)
        
        return jsonify({
            "articles": enriched,
            "category": category
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching category news: {str(e)}"}), 500


@news_bp.route("/news/sentiment/<sentiment>", methods=["GET"])
def get_news_by_sentiment(sentiment):
    """Get news filtered by sentiment (positive, negative, neutral)"""
    try:
        category = request.args.get("category", "general")
        articles = NewsArticle.query.filter_by(
            sentiment=sentiment.capitalize(),
            category=category
        ).order_by(NewsArticle.published_at.desc()).limit(50).all()
        
        if articles:
            return jsonify({
                "articles": [a.to_dict() for a in articles],
                "sentiment": sentiment
            }), 200
        
        # Fallback: fetch and filter
        news = fetch_latest_news(category=category)
        enriched = analyze_articles_sentiment(news)
        filtered = [n for n in enriched if n.get("sentiment", "").lower() == sentiment.lower()]
        
        return jsonify({
            "articles": filtered,
            "sentiment": sentiment
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error fetching sentiment news: {str(e)}"}), 500


@news_bp.route("/news/recommendations", methods=["GET"])
@token_required
def get_recommendations(current_user):
    """Get personalized news recommendations for user"""
    try:
        top_n = int(request.args.get("limit", 10))
        category = request.args.get("category")
        
        # Get candidate articles
        if category:
            articles_query = NewsArticle.query.filter_by(category=category)
        else:
            articles_query = NewsArticle.query
        
        candidates = articles_query.order_by(NewsArticle.published_at.desc()).limit(100).all()
        
        if not candidates:
            # Fallback to API
            news = fetch_latest_news(category=category or "general")
            candidates_dict = [normalize_article(n) for n in news]
        else:
            candidates_dict = [a.to_dict() for a in candidates]
        
        # Get recommendations
        recommended = recommendation_service.recommend(
            user_id=current_user.id,
            candidate_articles=candidates_dict,
            top_n=top_n
        )
        
        return jsonify({
            "recommendations": recommended,
            "count": len(recommended)
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting recommendations: {str(e)}"}), 500


@news_bp.route("/news/fake-news/predict", methods=["POST"])
def predict_fake_news():
    """Predict if an article is fake news"""
    try:
        data = request.get_json() or {}
        
        # Can accept article dict or text
        if "text" in data:
            article = {"title": data["text"], "description": data.get("text", "")}
        elif "article" in data:
            article = data["article"]
        else:
            # Assume full article data
            article = data
        
        prediction, confidence = fake_news_detector.predict(article)
        fake_score = confidence if prediction == 'fake' else (1 - confidence)
        
        return jsonify({
            "prediction": prediction,  # "real" or "fake"
            "confidence": round(confidence, 3),
            "fake_news_score": round(fake_score, 3),  # 0.0 (real) to 1.0 (fake)
            "article": article.get("title", "")[:100]
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error predicting fake news: {str(e)}"}), 500


@news_bp.route("/news/fake-news/train", methods=["POST"])
@token_required
def train_fake_news_model(current_user):
    """Train fake news detection model (Admin only or with training data)"""
    try:
        # In production, check if user is admin
        # if not current_user.is_admin:
        #     return jsonify({"message": "Admin access required"}), 403
        
        data = request.get_json() or {}
        texts = data.get("texts", [])
        labels = data.get("labels", [])  # 0 = real, 1 = fake
        model_type = data.get("model_type", "logistic_regression")
        
        if not texts or not labels or len(texts) != len(labels):
            # Use sample data for demonstration
            from services.fake_news_service import create_sample_training_data
            texts, labels = create_sample_training_data()
        
        # Train model
        metrics = fake_news_detector.train_model(texts, labels, model_type=model_type)
        
        return jsonify({
            "message": "Model trained successfully",
            "metrics": metrics,
            "model_type": model_type
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error training model: {str(e)}"}), 500


@news_bp.route("/news/analyze-sentiment", methods=["POST"])
def analyze_sentiment_endpoint():
    """Analyze sentiment of text or article"""
    try:
        data = request.get_json() or {}
        text = data.get("text", "")
        article = data.get("article", {})
        
        if text:
            result = analyze_sentiment_detailed(text)
        elif article:
            combined_text = f"{article.get('title', '')} {article.get('description', '')}"
            result = analyze_sentiment_detailed(combined_text)
        else:
            return jsonify({"message": "Text or article required"}), 400
        
        return jsonify({
            "sentiment": result["sentiment"],
            "scores": result["scores"],
            "polarity": result["polarity"],
            "subjectivity": result["subjectivity"]
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error analyzing sentiment: {str(e)}"}), 500


@news_bp.route("/news/trending", methods=["GET"])
def get_trending_topics():
    """Get trending topics"""
    try:
        days = int(request.args.get("days", 7))
        limit = int(request.args.get("limit", 10))
        
        trending = analytics_service.get_trending_topics(days=days, limit=limit)
        
        return jsonify({
            "trending_topics": trending,
            "days": days
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting trending topics: {str(e)}"}), 500


@news_bp.route("/news/categories", methods=["GET"])
def get_categories():
    """Get available news categories"""
    categories = [
        "general", "technology", "business", "sports",
        "entertainment", "health", "science"
    ]
    return jsonify({"categories": categories}), 200


@news_bp.route("/news/sources", methods=["GET"])
def get_sources():
    """Get available news sources"""
    try:
        sources = db.session.query(NewsArticle.source).distinct().limit(50).all()
        source_list = [s[0] for s in sources if s[0]]
        
        if not source_list:
            source_list = ["NewsAPI", "Various Sources"]
        
        return jsonify({"sources": source_list}), 200
    except Exception as e:
        return jsonify({"sources": ["NewsAPI"]}), 200


@news_bp.route("/news/scrape", methods=["POST"])
@token_required
def trigger_scraping(current_user):
    """Trigger news scraping (Admin recommended)"""
    try:
        # In production, check if admin
        # if not current_user.is_admin:
        #     return jsonify({"message": "Admin access required"}), 403
        
        data = request.get_json() or {}
        categories = data.get("categories", None)
        
        stored_count = scraping_service.scrape_and_store(categories=categories)
        
        return jsonify({
            "message": "Scraping completed",
            "articles_stored": stored_count
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error during scraping: {str(e)}"}), 500
