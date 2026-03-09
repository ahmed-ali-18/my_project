import os

from flask import Flask
from flask_login import LoginManager

from config import DevelopmentConfig, ProductionConfig
from models import User, db
from ai.complaint_classifier import init_model


login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)

    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    init_model(app)

    from routes.auth_routes import auth_bp
    from routes.complaint_routes import complaint_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(admin_bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    application = create_app()
    application.run()

