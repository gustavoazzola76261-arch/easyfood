"""Rotas do módulo de autenticação."""

from flask import Blueprint

from src.modules.auth import auth_controller
from src.modules.auth.auth_middleware import authenticate

auth_bp = Blueprint("auth", __name__)

auth_bp.post("/register")(auth_controller.register)
auth_bp.post("/login")(auth_controller.login)
auth_bp.get("/me")(authenticate(auth_controller.me))
