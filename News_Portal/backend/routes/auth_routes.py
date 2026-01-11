"""
Authentication routes (login, signup, logout)
"""
from flask import Blueprint, request, jsonify
from models import User, db
from utils.auth import generate_token

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    """User registration"""
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        email = data.get("email", "").strip()
        
        # Validation
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400
        
        if len(password) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400
        
        if email and User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400
        
        # Create user
        user = User(username=username, email=email if email else None)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.username, user.is_admin)
        
        return jsonify({
            "message": "Registration successful",
            "token": token,
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """User login"""
    try:
        data = request.get_json() or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Generate token
        token = generate_token(user.id, user.username, user.is_admin)
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/auth/me", methods=["GET"])
def get_current_user():
    """Get current user info (requires authentication via token_required decorator)"""
    from utils.auth import token_required
    
    @token_required
    def get_user(current_user):
        return jsonify({"user": current_user.to_dict()}), 200
    
    return get_user()

