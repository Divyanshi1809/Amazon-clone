import os

class Config:
    SECRET_KEY = os.environ.get("ed66741fd82468a6baaa1e2c31271db5") 
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///finance.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
