"""Factory da aplicação Flask — middlewares, estáticos e rotas."""

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from src.modules.auth.auth_routes import auth_bp
from src.modules.restaurants.restaurant_routes import restaurant_bp

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")
    app.url_map.strict_slashes = False
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(restaurant_bp, url_prefix="/restaurants")

    @app.get("/")
    def index():
        return send_from_directory(PUBLIC_DIR, "index.html")

    return app
