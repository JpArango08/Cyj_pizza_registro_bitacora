
from flask import Flask

from config import Config
from app.routes.api import api_bp


def create_app():
    Config.validate()

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    app.register_blueprint(api_bp)

    return app
