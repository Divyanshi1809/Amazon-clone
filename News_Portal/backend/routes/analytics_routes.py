"""
Analytics routes - User analytics, dashboard data, statistics
"""
from flask import Blueprint, jsonify, request
from utils.auth import token_required
from services.analytics_service import analytics_service

analytics_bp = Blueprint("analytics_bp", __name__)


@analytics_bp.route("/analytics/user", methods=["GET"])
@token_required
def get_user_analytics(current_user):
    """Get analytics for current user"""
    try:
        days = int(request.args.get("days", 30))
        
        reading_stats = analytics_service.get_user_reading_stats(current_user.id, days)
        interaction_stats = analytics_service.get_user_interaction_stats(current_user.id, days)
        ctr = analytics_service.get_click_through_rate(current_user.id, days)
        
        return jsonify({
            "user_id": current_user.id,
            "username": current_user.username,
            "reading_stats": reading_stats,
            "interaction_stats": interaction_stats,
            "click_through_rate": ctr,
            "period_days": days
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting user analytics: {str(e)}"}), 500


@analytics_bp.route("/analytics/dashboard", methods=["GET"])
@token_required
def get_dashboard_analytics(current_user):
    """Get comprehensive dashboard analytics"""
    try:
        days = int(request.args.get("days", 30))
        
        analytics = analytics_service.get_comprehensive_analytics(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting dashboard analytics: {str(e)}"}), 500


@analytics_bp.route("/analytics/trending", methods=["GET"])
def get_trending():
    """Get trending topics (public endpoint)"""
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


@analytics_bp.route("/analytics/sentiment", methods=["GET"])
def get_sentiment_analysis():
    """Get sentiment analysis statistics (public endpoint)"""
    try:
        days = int(request.args.get("days", 7))
        
        sentiment_data = analytics_service.get_sentiment_analysis(days=days)
        
        return jsonify(sentiment_data), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting sentiment analysis: {str(e)}"}), 500


@analytics_bp.route("/analytics/fake-news-stats", methods=["GET"])
def get_fake_news_stats():
    """Get fake news detection statistics"""
    try:
        days = int(request.args.get("days", 30))
        
        stats = analytics_service.get_fake_news_stats(days=days)
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting fake news stats: {str(e)}"}), 500


@analytics_bp.route("/analytics/ctr", methods=["GET"])
@token_required
def get_ctr(current_user):
    """Get click-through rate for user"""
    try:
        days = int(request.args.get("days", 30))
        
        ctr = analytics_service.get_click_through_rate(current_user.id, days)
        
        return jsonify(ctr), 200
        
    except Exception as e:
        return jsonify({"message": f"Error getting CTR: {str(e)}"}), 500

