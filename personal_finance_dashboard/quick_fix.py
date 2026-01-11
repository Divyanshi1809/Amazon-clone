#!/usr/bin/env python3
"""
Quick database fix script - automatically fixes the database
"""

from app import create_app, db
from app.models import User, Transaction

def quick_fix():
    """Quickly fix the database by recreating tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Quick database fix in progress...")
            
            # Drop existing tables
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create new tables with proper schema
            print("🏗️  Creating new tables with proper schema...")
            db.create_all()
            
            # Create a test user
            print("👤 Creating test user...")
            test_user = User(
                email='test@example.com',
                name='Test User'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Database fixed successfully!")
            print("\n🔑 Test user created:")
            print("   Email: test@example.com")
            print("   Password: password123")
            
            print("\n🚀 You can now run 'python run.py' and login!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    quick_fix()
