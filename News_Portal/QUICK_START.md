# Quick Start Guide - Run the Project

## Prerequisites Check
```powershell
python --version    # Should be 3.11+
node --version      # Should be 16+
npm --version       # Should come with Node.js
```

## Step 1: Backend Setup

### 1.1 Navigate to backend directory
```powershell
cd backend
```

### 1.2 Create virtual environment
```powershell
python -m venv venv
```

### 1.3 Activate virtual environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 1.4 Install Python dependencies
```powershell
pip install -r requirements.txt
```

### 1.5 Download NLTK data (required for sentiment analysis)
```powershell
python -c "import nltk; nltk.download('vader_lexicon')"
```

### 1.6 Create .env file (optional - has defaults)
```powershell
# Create .env file in backend directory
@"
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
NEWS_API_KEY=your-newsapi-key
DATABASE_URL=sqlite:///database.db
FLASK_DEBUG=1
"@ | Out-File -FilePath .env -Encoding utf8
```

**Note:** The project has a default NEWS_API_KEY in config.py, but you should get your own from https://newsapi.org/

### 1.7 Initialize database
```powershell
python -c "from app import app; from models import init_db; init_db(app)"
```

### 1.8 Run backend server
```powershell
python app.py
```

**Backend will run on:** `http://localhost:5000`

---

## Step 2: Frontend Setup (in a NEW terminal)

### 2.1 Open a new terminal/PowerShell window
Keep the backend running in the first terminal.

### 2.2 Navigate to frontend directory
```powershell
cd frontend
```

### 2.3 Install Node.js dependencies
```powershell
npm install
```

### 2.4 Run frontend development server
```powershell
npm start
```

**Frontend will run on:** `http://localhost:3000`

---

## Step 3: Access the Application

1. Open your browser
2. Go to: `http://localhost:3000`
3. The frontend will automatically connect to the backend API

---

## Quick Commands Summary

### Backend (Terminal 1)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
python -c "from app import app; from models import init_db; init_db(app)"
python app.py
```

### Frontend (Terminal 2)
```powershell
cd frontend
npm install
npm start
```

---

## Troubleshooting

### If virtual environment activation fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If port 5000 is already in use:
Edit `backend/app.py` and change the port:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

### If port 3000 is already in use:
Webpack will automatically use the next available port.

### If NLTK download fails:
```powershell
python -c "import nltk; nltk.download('vader_lexicon', download_dir='C:/nltk_data')"
```

### To reset database:
```powershell
cd backend
Remove-Item database.db -ErrorAction SilentlyContinue
python -c "from app import app; from models import init_db; init_db(app)"
```

---

## Getting News API Key (Optional but Recommended)

1. Go to https://newsapi.org/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add it to `backend/.env` file:
   ```
   NEWS_API_KEY=your-actual-key-here
   ```

---

## Testing the Setup

Once both servers are running:

1. **Backend API Test:**
   - Open: http://localhost:5000/api/news
   - Should return JSON with news articles

2. **Frontend Test:**
   - Open: http://localhost:3000
   - Should show the News Portal homepage

3. **Create Account:**
   - Click Sign Up
   - Create a user account
   - Login to access personalized features

---

## Stopping the Servers

- **Backend:** Press `Ctrl+C` in the backend terminal
- **Frontend:** Press `Ctrl+C` in the frontend terminal


