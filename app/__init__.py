from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from app.config import Config
import os

mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))  # Set template folder path
    app.config.from_object(Config)
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Add logging to check MongoDB connection
    with app.app_context():
        try:
            mongo.db.command('ping')
            app.logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            app.logger.error(f"Failed to connect to MongoDB: {e}")

    from app.routes import main  # Import your routes
    app.register_blueprint(main)  # Register the blueprint

    return app