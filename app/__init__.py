from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
import os
import logging

from app.routes import setup_routes

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["DEBUG"] = True

    app.logger.setLevel(logging.DEBUG)

    db.init_app(app)
    migrate.init_app(app, db)

    setup_routes(app)

    return app
