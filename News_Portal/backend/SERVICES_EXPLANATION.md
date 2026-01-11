# Backend Services Explanation

This document explains each service file in the News Portal backend, including their purpose, technologies used, and how they work.

---

## 📁 File Structure Overview

All service files are written in **Python** and located in `backend/services/` directory.

---

## 1. 🔍 `scraping_service.py` - Real-Time News Scraping Pipeline

### **Purpose:**
Automatically collects news articles from multiple sources (NewsAPI, RSS feeds) and stores them in the database.

### **Language & Technologies:**
- **Language:** Python 3
- **Libraries Used:**
  - `requests` - HTTP requests to fetch news from APIs
  - `feedparser` - Parse RSS/XML feeds
  - `BeautifulSoup` (bs4) - Parse HTML content
  - `datetime` - Date/time handling
  - SQLAlchemy (via models) - Database operations

### **Key Functions:**

1. **`fetch_from_newsapi()`**
   - Fetches news from NewsAPI.org
   - Parameters: category, country, page_size
   - Returns: List of normalized articles

2. **`fetch_from_rss()`**
   - Fetches news from RSS feeds
   - Parses XML/feed data
   - Extracts images from content

3. **`store_articles()`**
   - Saves articles to database
   - Analyzes sentiment automatically
   - Runs fake news detection
   - Prevents duplicates

4. **`scrape_and_store()`**
   - Main method that orchestrates everything
   - Scrapes from all sources
   - Stores in database

### **Real-World Use:**
- Run as a scheduled job (cron) every hour
- Keeps database fresh with latest news
- Can scrape multiple categories simultaneously

---

## 2. 🤖 `recommendation_service.py` - Smart News Recommendation System

### **Purpose:**
Recommends personalized news articles to users based on their reading history, interactions, and content similarity.

### **Language & Technologies:**
- **Language:** Python 3
- **Libraries Used:**
  - `scikit-learn` (sklearn) - Machine Learning library
    - `TfidfVectorizer` - Convert text to numerical features
    - `cosine_similarity` - Calculate similarity between articles
  - `numpy` - Numerical computations
  - `pandas` - Data manipulation
  - `pickle` - Save/load trained models

### **How It Works:**

1. **TF-IDF Vectorization**
   - Converts article text (title + description) into numerical vectors
   - TF-IDF = Term Frequency × Inverse Document Frequency
   - Identifies important words in each article

2. **User Profile Building**
   - Analyzes user's reading history
   - Tracks time spent on articles
   - Identifies preferred categories
   - Creates a "profile vector" representing user interests

3. **Content-Based Filtering**
   - Compares user profile with new articles using cosine similarity
   - Cosine similarity measures angle between vectors (0-1 scale)
   - Higher similarity = better recommendation

4. **Recommendation Scoring**
   - 70% weight on content similarity
   - 30% weight on category preferences
   - Returns top N articles sorted by score

### **Key Functions:**

- `build_user_profile()` - Creates user's interest vector
- `get_category_preferences()` - Finds user's favorite categories
- `recommend()` - Main recommendation engine
- `get_trending_articles()` - Finds popular articles

### **Example:**
If user reads many "technology" articles and spends 5+ minutes on AI-related news, 
the system will recommend similar tech/AI articles.

---

## 3. 🛑 `fake_news_service.py` - Fake News Detection System

### **Purpose:**
Uses Machine Learning to classify news articles as "real" or "fake".

### **Language & Technologies:**
- **Language:** Python 3
- **ML Libraries:**
  - `scikit-learn`:
    - `LogisticRegression` - Linear classification model
    - `MultinomialNB` - Naive Bayes classifier
    - `RandomForestClassifier` - Ensemble tree-based model
    - `TfidfVectorizer` - Text feature extraction
    - Metrics: accuracy, precision, recall, F1-score
  - `pandas` - Data handling
  - `numpy` - Numerical operations
  - `pickle` - Model persistence
  - `re` - Text preprocessing (regex)

### **ML Models Explained:**

1. **Logistic Regression** (Default)
   - Linear model that finds decision boundary
   - Fast, interpretable
   - Good baseline model

2. **Naive Bayes**
   - Probabilistic classifier
   - Assumes feature independence
   - Works well with text data

3. **Random Forest**
   - Ensemble of decision trees
   - More complex, often more accurate
   - Takes longer to train

### **How It Works:**

1. **Text Preprocessing**
   - Converts to lowercase
   - Removes URLs, special characters
   - Cleans whitespace

2. **Feature Extraction**
   - Uses TF-IDF to convert text → numbers
   - Creates 5000-dimensional feature vectors

3. **Training** (if dataset available)
   - Trains on labeled data (0=real, 1=fake)
   - Evaluates with metrics (accuracy, precision, recall)
   - Saves trained model to disk

4. **Prediction**
   - Takes article text
   - Preprocesses and vectorizes
   - Predicts: "real" or "fake"
   - Returns confidence score (0.0 to 1.0)

### **Key Functions:**

- `train_model()` - Trains ML model on dataset
- `predict()` - Predicts if article is fake
- `predict_batch()` - Predicts multiple articles
- `save_model()` / `load_model()` - Model persistence

### **Note:**
For production, you need a labeled dataset (e.g., from Kaggle Fake News Dataset).
The code includes sample data for demonstration.

---

## 4. 📊 `analytics_service.py` - User Analytics Dashboard

### **Purpose:**
Tracks and analyzes user behavior, reading patterns, and content statistics for insights.

### **Language & Technologies:**
- **Language:** Python 3
- **Libraries Used:**
  - SQLAlchemy - Database queries
  - `datetime`, `timedelta` - Date calculations
  - `collections.defaultdict` - Counting aggregations
  - `func`, `desc` from SQLAlchemy - SQL aggregations

### **Key Metrics Tracked:**

1. **User Reading Stats**
   - Total reading time (seconds/minutes)
   - Articles read count
   - Average reading time
   - Category breakdown
   - Top categories

2. **User Interaction Stats**
   - Clicks, views, likes, shares
   - Interactions by category
   - Most interacted categories

3. **Trending Topics**
   - Most popular categories
   - Based on interaction counts
   - Time-based filtering (last 7 days, etc.)

4. **Sentiment Analysis**
   - Distribution: Positive, Negative, Neutral
   - Percentages of each sentiment
   - Tracks over time

5. **Click-Through Rate (CTR)**
   - Clicks / Views × 100
   - Measures engagement
   - Per user or overall

6. **Fake News Stats**
   - Count of fake vs real articles
   - Average fake news score
   - Percentage breakdown

### **Key Functions:**

- `get_user_reading_stats()` - User reading analytics
- `get_user_interaction_stats()` - User interaction analytics
- `get_trending_topics()` - Popular topics
- `get_sentiment_analysis()` - Sentiment distribution
- `get_click_through_rate()` - CTR calculation
- `get_fake_news_stats()` - Fake news statistics
- `get_comprehensive_analytics()` - All metrics combined

### **Use Cases:**
- Admin dashboard to see user behavior
- Content optimization based on popular categories
- Identify trending topics
- Measure engagement

---

## 5. 💭 `sentiment_service.py` - Sentiment Analysis Service

### **Purpose:**
Analyzes the emotional tone of news articles (Positive, Negative, Neutral).

### **Language & Technologies:**
- **Language:** Python 3
- **Libraries Used:**
  - `textblob` - Simple sentiment analysis
  - `vaderSentiment` - Advanced sentiment analyzer (better for news)
  - Both return polarity scores (-1 to +1)

### **How It Works:**

1. **VADER (Default - Better for News)**
   - Valence Aware Dictionary and sEntiment Reasoner
   - Designed for social media/news
   - Returns compound score (-1 to +1)
   - > 0.05 = Positive
   - < -0.05 = Negative
   - Otherwise = Neutral

2. **TextBlob (Fallback)**
   - Simpler sentiment analysis
   - Uses pattern library
   - Returns polarity (-1 to +1)

### **Key Functions:**

- `analyze_sentiment()` - Returns "Positive", "Negative", or "Neutral"
- `analyze_sentiment_detailed()` - Returns detailed scores and metrics
- `analyze_articles_sentiment()` - Analyzes list of articles

### **Example:**
- "Great news! Economy is growing!" → Positive
- "Tragic accident kills 5 people" → Negative
- "Stock market opens at 9 AM" → Neutral

---

## 🔄 How Services Work Together

```
1. Scraping Service fetches news
   ↓
2. Sentiment Service analyzes emotion
   ↓
3. Fake News Service checks if real/fake
   ↓
4. Articles stored in database
   ↓
5. User reads articles (tracked by Analytics)
   ↓
6. Recommendation Service suggests similar articles
   ↓
7. Analytics Service generates insights
```

---

## 📦 Dependencies Summary

All services require:
- **Python 3.7+**
- Core libraries installed via `requirements.txt`:
  - Flask (web framework)
  - SQLAlchemy (database)
  - scikit-learn (machine learning)
  - pandas, numpy (data processing)
  - requests, feedparser, beautifulsoup4 (web scraping)
  - textblob, vaderSentiment (sentiment analysis)

---

## 🚀 Interview Talking Points

When explaining these services in interviews:

1. **Scraping Service**: "I built an automated data pipeline using Python and web scraping libraries to collect real-time news from multiple sources."

2. **Recommendation Service**: "I implemented a content-based recommendation system using TF-IDF vectorization and cosine similarity to personalize news suggestions."

3. **Fake News Detection**: "I created a fake news classifier using scikit-learn, training multiple ML models (Logistic Regression, Naive Bayes, Random Forest) with NLP preprocessing."

4. **Analytics Service**: "I developed analytics tools to track user behavior, reading patterns, and generate insights using SQL queries and data aggregation."

5. **Sentiment Analysis**: "I integrated NLP sentiment analysis using VADER to classify news emotions and track public opinion trends."

---

## 💡 Learning Resources

- **TF-IDF**: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- **Cosine Similarity**: https://en.wikipedia.org/wiki/Cosine_similarity
- **scikit-learn Docs**: https://scikit-learn.org/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **VADER Sentiment**: https://github.com/cjhutto/vaderSentiment

