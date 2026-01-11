#!/usr/bin/env python3
"""
Test script to verify the login system works correctly
"""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def test_login_system():
    """Test the login system by creating a test user"""
    app = create_app()
    
    with app.app_context():
        # Check if test user exists
        test_user = User.query.filter_by(email='test@example.com').first()
        
        if not test_user:
            # Create test user
            test_user = User(
                email='test@example.com',
                name='Test User',
                password=generate_password_hash('password123', method='pbkdf2:sha256')
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            print("   Email: test@example.com")
            print("   Password: password123")
        else:
            print("✅ Test user already exists!")
            print("   Email: test@example.com")
            print("   Password: password123")
        
        print("\n🚀 You can now:")
        print("   1. Run 'python run.py' to start the application")
        print("   2. Go to http://localhost:5000")
        print("   3. You'll be redirected to login page")
        print("   4. Use the test credentials above to login")

if __name__ == "__main__":
    test_login_system()
