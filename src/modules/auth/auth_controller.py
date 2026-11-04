"""Controller HTTP de autenticação."""

from flask import jsonify, request

from src.modules.auth import auth_service
from src.modules.auth.auth_service import EmailAlreadyExistsError
from src.modules.restaurants import restaurant_service


def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Nome, e-mail e senha são obrigatórios"}), 400

    try:
        user = auth_service.register(name=name, email=email, password=password)
        return jsonify(user), 201
    except EmailAlreadyExistsError:
        return jsonify({"error": "E-mail já cadastrado"}), 409
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "E-mail e senha são obrigatórios"}), 400

    try:
        result = auth_service.login(email=email, password=password)
        if result is None:
            return jsonify({"error": "Credenciais inválidas"}), 401
        return jsonify(result)
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


def me():
    user = getattr(request, "user", None)
    memberships = restaurant_service.list_memberships(user["id"]) if user else []
    return jsonify(
        {
            "message": "Você está autenticado!",
            "user": user,
            "memberships": memberships,
        }
    )
