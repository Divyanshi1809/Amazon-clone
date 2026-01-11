import requests
import os

# Example public API key (replace with your own from NewsAPI.org or GNews)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "200f99f69b3546ca9ab65d9291e43f4f")

# Base URL for the news API
BASE_URL = "https://newsapi.org/v2/top-headlines"

# ✅ Fetch latest news from API
def fetch_latest_news(category="general", country="in"):
    """
    Fetch latest news articles from API based on category and country.
    Returns list of articles.
    """
    try:
        params = {
            "country": country,
            "category": category,
            "apiKey": NEWS_API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code != 200 or "articles" not in data:
            return []

        return data["articles"]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# ✅ Categorize news into politics, tech, sports, etc.
def categorize_news(articles):
    """
    Categorizes fetched articles based on keyword matching.
    """
    categories = {
        "politics": [],
        "technology": [],
        "sports": [],
        "others": []
    }

    for article in articles:
        title = (article.get("title") or "").lower()
        description = (article.get("description") or "").lower()

        if any(word in title for word in ["election", "government", "minister", "politics"]):
            categories["politics"].append(article)
        elif any(word in title for word in ["tech", "startup", "software", "ai", "robot"]):
            categories["technology"].append(article)
        elif any(word in title for word in ["match", "player", "goal", "tournament", "cricket", "football"]):
            categories["sports"].append(article)
        else:
            categories["others"].append(article)

    return categories
