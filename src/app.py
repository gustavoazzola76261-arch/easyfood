"""Factory da aplicação Flask — middlewares e rotas."""

from flask import Flask
from flask_cors import CORS

from src.modules.restaurants.restaurant_routes import restaurant_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app)
    app.register_blueprint(restaurant_bp, url_prefix="/restaurants")
    return app
