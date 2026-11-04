"""Factory da aplicação Flask — middlewares, estáticos e rotas."""

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from src.modules.auth.auth_routes import auth_bp
from src.modules.dishes.dish_routes import dish_bp
from src.modules.restaurants.restaurant_routes import restaurant_bp
from src.modules.shared.image_service import MAX_IMAGE_BYTES, uploads_root
from src.modules.shared.upload_middleware import payload_too_large

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")
    app.url_map.strict_slashes = False
    app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_BYTES
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(restaurant_bp, url_prefix="/restaurants")
    app.register_blueprint(dish_bp)

    app.register_error_handler(RequestEntityTooLarge, payload_too_large)

    @app.get("/")
    def index():
        return send_from_directory(PUBLIC_DIR, "index.html")

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(uploads_root(), filename)

    return app
