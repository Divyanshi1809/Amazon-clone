"""
User routes (bookmarks, user interactions)
"""
from flask import Blueprint, request, jsonify
from models import Bookmark, db, UserInteraction, ReadingHistory, NewsArticle
from utils.auth import token_required
from datetime import datetime

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/bookmarks", methods=["GET"])
@token_required
def get_bookmarks(current_user):
    """Get user's bookmarks"""
    try:
        bookmarks = Bookmark.query.filter_by(user_id=current_user.id).order_by(Bookmark.created_at.desc()).all()
        return jsonify({
            "bookmarks": [b.to_dict() for b in bookmarks]
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching bookmarks: {str(e)}"}), 500


@user_bp.route("/bookmarks", methods=["POST"])
@token_required
def add_bookmark(current_user):
    """Add a bookmark"""
    try:
        data = request.get_json() or {}
        news_id = data.get("news_id")
        
        if not news_id:
            return jsonify({"message": "news_id is required"}), 400
        
        # Check if already bookmarked
        existing = Bookmark.query.filter_by(user_id=current_user.id, news_id=news_id).first()
        if existing:
            return jsonify({"message": "Already bookmarked", "bookmark": existing.to_dict()}), 200
        
        # Create bookmark
        bookmark = Bookmark(
            user_id=current_user.id,
            news_id=news_id,
            title=data.get("title"),
            url=data.get("url"),
            image_url=data.get("image_url") or data.get("imageUrl"),
            source=data.get("source"),
            sentiment=data.get("sentiment"),
            category=data.get("category")
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({
            "message": "Bookmark added",
            "bookmark": bookmark.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error adding bookmark: {str(e)}"}), 500


@user_bp.route("/bookmarks/<news_id>", methods=["DELETE"])
@token_required
def remove_bookmark(current_user, news_id):
    """Remove a bookmark"""
    try:
        bookmark = Bookmark.query.filter_by(user_id=current_user.id, news_id=news_id).first()
        
        if not bookmark:
            return jsonify({"message": "Bookmark not found"}), 404
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return jsonify({"message": "Bookmark removed"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error removing bookmark: {str(e)}"}), 500


@user_bp.route("/bookmarks/check/<news_id>", methods=["GET"])
@token_required
def check_bookmark(current_user, news_id):
    """Check if article is bookmarked"""
    try:
        bookmark = Bookmark.query.filter_by(user_id=current_user.id, news_id=news_id).first()
        return jsonify({"is_bookmarked": bookmark is not None}), 200
    except Exception as e:
        return jsonify({"message": f"Error checking bookmark: {str(e)}"}), 500


@user_bp.route("/interactions", methods=["POST"])
@token_required
def track_interaction(current_user):
    """Track user interaction with article"""
    try:
        data = request.get_json() or {}
        news_id = data.get("news_id")
        interaction_type = data.get("interaction_type", "click")  # click, view, like, share
        category = data.get("category")
        
        if not news_id:
            return jsonify({"message": "news_id is required"}), 400
        
        interaction = UserInteraction(
            user_id=current_user.id,
            news_id=news_id,
            interaction_type=interaction_type,
            category=category
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            "message": "Interaction tracked",
            "interaction": interaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error tracking interaction: {str(e)}"}), 500


@user_bp.route("/reading-history", methods=["POST"])
@token_required
def track_reading_time(current_user):
    """Track reading time for an article"""
    try:
        data = request.get_json() or {}
        news_id = data.get("news_id")
        time_spent_seconds = data.get("time_spent_seconds", 0)
        category = data.get("category")
        
        if not news_id:
            return jsonify({"message": "news_id is required"}), 400
        
        # Find or create reading history entry
        history = ReadingHistory.query.filter_by(
            user_id=current_user.id,
            news_id=news_id,
            completed_at=None
        ).first()
        
        if history:
            history.time_spent_seconds += time_spent_seconds
            if data.get("completed"):
                history.completed_at = datetime.utcnow()
        else:
            history = ReadingHistory(
                user_id=current_user.id,
                news_id=news_id,
                time_spent_seconds=time_spent_seconds,
                category=category
            )
            if data.get("completed"):
                history.completed_at = datetime.utcnow()
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            "message": "Reading time tracked",
            "history": history.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error tracking reading time: {str(e)}"}), 500
