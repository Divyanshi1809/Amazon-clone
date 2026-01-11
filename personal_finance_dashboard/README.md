# Personal Finance Dashboard

A Flask-based personal finance dashboard with secure user authentication and transaction management.

## Features

- 🔐 **Secure Login System** - Every user must authenticate before accessing the dashboard
- 👤 **User Management** - Individual user accounts with isolated data
- 💰 **Transaction Tracking** - Add, view, and delete financial transactions
- 📊 **Dashboard Analytics** - View income, expenses, and balance
- 🎨 **Modern UI** - Clean, responsive design with Bootstrap

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Test User (Optional)
```bash
python test_login.py
```
This creates a test user with:
- Email: `test@example.com`
- Password: `password123`

### 3. Run the Application
```bash
python run.py
```

### 4. Access the Application
- Open your browser and go to `http://localhost:5000`
- You'll be automatically redirected to the login page
- Use your credentials to login
- After successful login, you'll be redirected to the dashboard

## How the Login System Works

1. **Root Route Protection**: The root route (`/`) automatically redirects unauthenticated users to the login page
2. **Login Required**: All dashboard and transaction routes are protected with `@login_required` decorator
3. **Session Management**: Flask-Login handles user sessions securely
4. **User Isolation**: Each user can only see and manage their own transactions

## Routes

- `/` - Root route (redirects to login if not authenticated)
- `/login` - Login page
- `/signup` - User registration page
- `/dashboard` - Main dashboard (requires login)
- `/add` - Add new transaction (requires login)
- `/delete/<id>` - Delete transaction (requires login)

## Security Features

- Password hashing using PBKDF2 with SHA256
- Session-based authentication
- Route protection with Flask-Login
- User data isolation
- Secure logout functionality

## Database

The application uses SQLite with the following models:
- **User**: email, password (hashed), name
- **Transaction**: date, amount, category, description, user_id

## Customization

You can modify the following files to customize the application:
- `app/templates/` - HTML templates
- `app/static/` - CSS and JavaScript files
- `app/models.py` - Database models
- `app/routes.py` - Application routes and logic
