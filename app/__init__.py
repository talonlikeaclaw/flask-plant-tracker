from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Intialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    # Create and configure the app
    app = Flask(__name__, template_folder="../templates/")
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes import main_bp, auth_bp, plants_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(plants_bp)

    import os

    os.makedirs(
        os.path.join(app.root_path, "static", "uploads", "plants"), exist_ok=True
    )

    return app


from app import models
