import os
from pathlib import Path

class Config:
	SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
	DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
	# Allow frontend dev server by default; adjust for production
	CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
	
	# Database
	basedir = Path(__file__).parent
	SQLALCHEMY_DATABASE_URI = os.getenv(
		"DATABASE_URL",
		f"sqlite:///{basedir / 'database.db'}"
	)
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
	# News API
	NEWS_API_KEY = os.getenv("NEWS_API_KEY", "200f99f69b3546ca9ab65d9291e43f4f")
	
	# JWT
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
	JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
	
	# Model paths
	MODEL_DIR = basedir / "models"
	MODEL_DIR.mkdir(exist_ok=True)
	FAKE_NEWS_MODEL_PATH = MODEL_DIR / "fake_news_model.pkl"
	RECOMMENDATION_VECTORIZER_PATH = MODEL_DIR / "recommendation_vectorizer.pkl"
