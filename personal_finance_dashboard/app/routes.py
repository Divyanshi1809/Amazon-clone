from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Transaction
from . import db
from datetime import datetime, timedelta
from flask_login import login_required, current_user, logout_user
from collections import defaultdict
import calendar

main = Blueprint("main", __name__)

# Root route - redirects to login if not authenticated
@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

# Session refresh endpoint
@main.route("/refresh-session")
@login_required
def refresh_session():
    # Refresh the session
    session.modified = True
    return {"status": "success", "message": "Session refreshed"}

# Dashboard
@main.route("/dashboard")
@login_required
def dashboard():
    # Check if session has expired
    if not session.get('_fresh'):
        logout_user()
        session.clear()
        flash("Your session has expired. Please login again.", "warning")
        return redirect(url_for("auth.login"))
    
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expense = sum(abs(t.amount) for t in transactions if t.amount < 0)
    balance = total_income - total_expense

    # Prepare chart data
    chart_data = prepare_chart_data(transactions)

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        **chart_data
    )

def prepare_chart_data(transactions):
    """Prepare data for charts"""
    if not transactions:
        # Return empty chart data if no transactions
        return {
            'monthly_data': {'labels': [], 'income': [], 'expenses': []},
            'category_data': {'labels': [], 'values': []},
            'balance_data': {'labels': [], 'values': []},
            'top_categories_data': {'labels': [], 'values': []}
        }
    
    # Monthly data for the last 6 months
    monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0})
    current_date = datetime.now()
    
    for i in range(6):
        month_date = current_date - timedelta(days=30*i)
        month_key = month_date.strftime('%b %Y')
        monthly_data[month_key] = {'income': 0, 'expenses': 0}
    
    # Category data
    category_data = defaultdict(float)
    
    # Process transactions
    for transaction in transactions:
        month_key = transaction.date.strftime('%b %Y')
        
        if transaction.amount > 0:  # Income
            monthly_data[month_key]['income'] += transaction.amount
        else:  # Expense
            monthly_data[month_key]['expenses'] += abs(transaction.amount)
            category_data[transaction.category] += abs(transaction.amount)
    
    # Sort months chronologically
    sorted_months = sorted(monthly_data.keys(), 
                          key=lambda x: datetime.strptime(x, '%b %Y'))
    
    # Prepare monthly chart data
    monthly_labels = []
    monthly_income = []
    monthly_expenses = []
    monthly_balance = []
    
    for month in sorted_months:
        monthly_labels.append(month)
        monthly_income.append(monthly_data[month]['income'])
        monthly_expenses.append(monthly_data[month]['expenses'])
        monthly_balance.append(monthly_data[month]['income'] - monthly_data[month]['expenses'])
    
    # Prepare category chart data
    category_labels = list(category_data.keys())
    category_values = list(category_data.values())
    
    # Prepare top categories data (top 5)
    sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5]
    top_categories_labels = [cat[0] for cat in sorted_categories]
    top_categories_values = [cat[1] for cat in sorted_categories]
    
    return {
        'monthly_data': {
            'labels': monthly_labels,
            'income': monthly_income,
            'expenses': monthly_expenses
        },
        'category_data': {
            'labels': category_labels,
            'values': category_values
        },
        'balance_data': {
            'labels': monthly_labels,
            'values': monthly_balance
        },
        'top_categories_data': {
            'labels': top_categories_labels,
            'values': top_categories_values
        }
    }

# Add Transaction
@main.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        try:
            date = datetime.strptime(request.form["date"], "%Y-%m-%d")
            category = request.form["category"]
            transaction_type = request.form.get("transaction_type")
            amount = float(request.form["amount"])
            description = request.form.get("description", "")
            
            # Convert expense amounts to negative values
            if transaction_type == "expense":
                amount = -abs(amount)  # Ensure negative for expenses
            elif transaction_type == "income":
                amount = abs(amount)   # Ensure positive for income

            new_transaction = Transaction(
                date=date,
                category=category,
                amount=amount,
                description=description,
                user_id=current_user.id
            )
            db.session.add(new_transaction)
            db.session.commit()
            flash("Transaction added successfully!", "success")
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            flash(f"Error adding transaction: {e}", "danger")

    return render_template("transactions.html")

# Delete Transaction
@main.route("/delete/<int:id>")
@login_required
def delete_transaction(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction deleted successfully!", "success")
    return redirect(url_for("main.dashboard"))
