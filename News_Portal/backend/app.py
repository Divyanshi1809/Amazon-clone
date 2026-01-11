from flask import Flask
from flask_cors import CORS

from config import Config
from models import db, init_db
from routes import news_bp, user_bp, auth_bp, analytics_bp


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(Config)

	# Initialize database
	init_db(app)

	# Enable CORS for all routes; adjust origins if needed
	CORS(app, resources={r"/*": {"origins": "*"}})

	# Register blueprints
	app.register_blueprint(news_bp, url_prefix="/api")
	app.register_blueprint(user_bp, url_prefix="/api")
	app.register_blueprint(auth_bp, url_prefix="/api")
	app.register_blueprint(analytics_bp, url_prefix="/api")

	return app


app = create_app()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)


