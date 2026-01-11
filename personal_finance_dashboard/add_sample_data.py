from app import create_app, db
from app.models import Transaction, User
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("=== ADDING SAMPLE TRANSACTIONS ===")
    
    # Find your user
    user = User.query.filter_by(email='sethiads@rknec.edu').first()
    
    if not user:
        print("❌ User not found! Please login first.")
        exit()
    
    print(f"✅ Found user: {user.email}")
    
    # Sample categories
    income_categories = ['Salary', 'Freelance', 'Investment', 'Bonus']
    expense_categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Healthcare']
    
    # Sample amounts
    income_amounts = [50000, 15000, 8000, 10000]
    expense_amounts = [2000, 1500, 3000, 5000, 1200, 800]
    
    # Generate transactions for the last 6 months
    current_date = datetime.now()
    
    for month_offset in range(6):
        month_date = current_date - timedelta(days=30*month_offset)
        
        # Add 1-2 income transactions per month
        for _ in range(random.randint(1, 2)):
            category = random.choice(income_categories)
            amount = random.choice(income_amounts)
            date = month_date - timedelta(days=random.randint(0, 25))
            
            transaction = Transaction(
                date=date,
                category=category,
                amount=amount,
                description=f"Sample {category}",
                user_id=user.id
            )
            db.session.add(transaction)
            print(f"✅ Added income: {category} - ₹{amount}")
        
        # Add 3-5 expense transactions per month
        for _ in range(random.randint(3, 5)):
            category = random.choice(expense_categories)
            amount = -random.choice(expense_amounts)  # Negative for expenses
            date = month_date - timedelta(days=random.randint(0, 25))
            
            transaction = Transaction(
                date=date,
                category=category,
                amount=amount,
                description=f"Sample {category} expense",
                user_id=user.id
            )
            db.session.add(transaction)
            print(f"✅ Added expense: {category} - ₹{abs(amount)}")
    
    # Commit all transactions
    db.session.commit()
    
    print(f"\n✅ Added sample transactions successfully!")
    print("🚀 Now refresh your dashboard to see the charts!")

