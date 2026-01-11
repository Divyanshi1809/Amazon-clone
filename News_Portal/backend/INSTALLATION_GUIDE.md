# Installation Guide

## Quick Start

### Backend Setup

1. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Download NLTK data (for VADER Sentiment)**
```python
python -c "import nltk; nltk.download('vader_lexicon')"
```

Or in Python shell:
```python
import nltk
nltk.download('vader_lexicon')
```

3. **Set up environment variables**
Create `.env` file with your API keys:
```env
NEWS_API_KEY=your-key-here
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

4. **Initialize database**
```bash
python -c "from app import app; from models import init_db; init_db(app)"
```

5. **Run server**
```bash
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Getting News API Key

1. Go to https://newsapi.org/
2. Sign up for free account
3. Get your API key from dashboard
4. Add to `.env` file as `NEWS_API_KEY`

## Training Fake News Model (Optional)

The fake news detector works out of the box with default behavior. To train on your own dataset:

```python
from services.fake_news_service import fake_news_detector

# Your training data
texts = ["Article 1...", "Article 2...", ...]
labels = [0, 1, 0, ...]  # 0 = real, 1 = fake

# Train
metrics = fake_news_detector.train_model(texts, labels, model_type='logistic_regression')
print(metrics)
```

## Common Issues

### VADER Sentiment Import Error
```bash
pip install vaderSentiment
python -c "import nltk; nltk.download('vader_lexicon')"
```

### Database Migration Issues
Delete `database.db` and `instance/` folder, then reinitialize:
```bash
rm database.db
rm -rf instance/
python -c "from app import app; from models import init_db; init_db(app)"
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

