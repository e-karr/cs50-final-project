from flask import Flask
from config import Config

from app.extensions import db
from app.main import bp as main_bp
from app.auth import bp as auth_bp
from app.user import bp as user_bp
from app.teams import bp as team_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(team_bp)
    
    return app
