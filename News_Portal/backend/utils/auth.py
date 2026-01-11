"""
JWT Authentication utilities
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User
from config import Config

def generate_token(user_id: int, username: str, is_admin: bool = False, secret_key: str = None) -> str:
    """Generate JWT token for user"""
    if secret_key is None:
        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
        except RuntimeError:
            secret_key = Config.JWT_SECRET_KEY
    
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token: str, secret_key: str = None) -> dict:
    """Verify JWT token and return payload"""
    if secret_key is None:
        try:
            secret_key = current_app.config['JWT_SECRET_KEY']
        except RuntimeError:
            secret_key = Config.JWT_SECRET_KEY
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 401
        
        # Add user to kwargs
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated

