from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    # Clear any existing session
    session.clear()
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=False)  # Don't remember user
            session.permanent = False  # Session expires when browser closes
            flash("Login successful! Welcome back.", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.signup"))

        try:
            new_user = User(
                email=email,
                name=name
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=False)  # Don't remember user
            session.permanent = False  # Session expires when browser closes
            flash("Account created successfully! Welcome!", "success")
            return redirect(url_for("main.dashboard"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {e}", "danger")

    return render_template("signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method == "POST":
        password = request.form.get("password")
        
        if current_user.check_password(password):
            from .models import Transaction
            Transaction.query.filter_by(user_id=current_user.id).delete()
            
            user_to_delete = current_user
            logout_user()
            session.clear()
            
            db.session.delete(user_to_delete)
            db.session.commit()
            
            flash("Your account has been deleted successfully.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Incorrect password. Account deletion cancelled.", "danger")
    
    return render_template("delete_account.html")
