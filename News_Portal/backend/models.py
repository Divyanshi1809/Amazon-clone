from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Create the SQLAlchemy instance; initialize with the Flask app in app factory
db = SQLAlchemy()


def init_db(app) -> None:
	"""
	Attach db to the Flask app and create tables if they don't exist.
	Make sure app.config['SQLALCHEMY_DATABASE_URI'] is set before calling.
	"""
	db.init_app(app)
	with app.app_context():
		db.create_all()


class User(db.Model):
	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False, index=True)
	password_hash = db.Column(db.String(255), nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=True)
	is_admin = db.Column(db.Boolean, default=False, nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	# relationships
	bookmarks = db.relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
	interactions = db.relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
	reading_history = db.relationship("ReadingHistory", back_populates="user", cascade="all, delete-orphan")

	def set_password(self, raw_password: str) -> None:
		self.password_hash = generate_password_hash(raw_password)

	def check_password(self, raw_password: str) -> bool:
		return check_password_hash(self.password_hash, raw_password)

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"username": self.username,
			"email": self.email,
			"is_admin": self.is_admin,
			"created_at": self.created_at.isoformat() if self.created_at else None
		}

	def __repr__(self) -> str:
		return f"<User id={self.id} username={self.username!r}>"


class Bookmark(db.Model):
	__tablename__ = "bookmarks"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

	# store the external news/article id or URL
	news_id = db.Column(db.String(255), nullable=False, index=True)
	title = db.Column(db.String(512))
	url = db.Column(db.String(1024))
	image_url = db.Column(db.String(1024))
	source = db.Column(db.String(255))
	sentiment = db.Column(db.String(32))
	category = db.Column(db.String(100))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	# relationship back to user
	user = db.relationship("User", back_populates="bookmarks")

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"news_id": self.news_id,
			"title": self.title,
			"url": self.url,
			"image_url": self.image_url,
			"source": self.source,
			"sentiment": self.sentiment,
			"category": self.category,
			"created_at": self.created_at.isoformat() if self.created_at else None
		}

	def __repr__(self) -> str:
		return f"<Bookmark id={self.id} user_id={self.user_id} news_id={self.news_id!r}>"


class NewsArticle(db.Model):
	"""Stored news articles from scraping pipeline"""
	__tablename__ = "news_articles"

	id = db.Column(db.Integer, primary_key=True)
	news_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
	title = db.Column(db.String(512), nullable=False)
	description = db.Column(db.Text)
	content = db.Column(db.Text)
	url = db.Column(db.String(1024), nullable=False)
	image_url = db.Column(db.String(1024))
	source = db.Column(db.String(255))
	author = db.Column(db.String(255))
	category = db.Column(db.String(100), index=True)
	sentiment = db.Column(db.String(32))
	published_at = db.Column(db.DateTime, nullable=False, index=True)
	scraped_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	
	# Fake news detection fields
	fake_news_score = db.Column(db.Float)  # 0.0 to 1.0, higher = more likely fake
	fake_news_prediction = db.Column(db.String(20))  # "real" or "fake"
	
	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"news_id": self.news_id,
			"title": self.title,
			"description": self.description,
			"content": self.content,
			"url": self.url,
			"image_url": self.image_url,
			"source": self.source,
			"author": self.author,
			"category": self.category,
			"sentiment": self.sentiment,
			"published_at": self.published_at.isoformat() if self.published_at else None,
			"scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
			"fake_news_score": self.fake_news_score,
			"fake_news_prediction": self.fake_news_prediction
		}

	def __repr__(self) -> str:
		return f"<NewsArticle id={self.id} title={self.title[:50]!r}>"


class UserInteraction(db.Model):
	"""Track user interactions with news articles"""
	__tablename__ = "user_interactions"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	news_id = db.Column(db.String(255), nullable=False, index=True)
	interaction_type = db.Column(db.String(50), nullable=False)  # "click", "view", "like", "share"
	category = db.Column(db.String(100), index=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

	user = db.relationship("User", back_populates="interactions")

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"user_id": self.user_id,
			"news_id": self.news_id,
			"interaction_type": self.interaction_type,
			"category": self.category,
			"created_at": self.created_at.isoformat() if self.created_at else None
		}


class ReadingHistory(db.Model):
	"""Track time spent reading articles"""
	__tablename__ = "reading_history"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
	news_id = db.Column(db.String(255), nullable=False, index=True)
	time_spent_seconds = db.Column(db.Integer, default=0)  # Time spent in seconds
	category = db.Column(db.String(100), index=True)
	started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	completed_at = db.Column(db.DateTime)

	user = db.relationship("User", back_populates="reading_history")

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"user_id": self.user_id,
			"news_id": self.news_id,
			"time_spent_seconds": self.time_spent_seconds,
			"category": self.category,
			"started_at": self.started_at.isoformat() if self.started_at else None,
			"completed_at": self.completed_at.isoformat() if self.completed_at else None
		}