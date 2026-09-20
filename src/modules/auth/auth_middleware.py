"""Middleware de autenticação JWT."""

import os
from functools import wraps

import jwt
from flask import jsonify, request

JWT_SECRET = os.getenv("JWT_SECRET", "troque-por-uma-chave-longa-e-aleatoria")


def authenticate(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token não fornecido"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            subject = payload.get("sub")
            request.user = {
                "id": int(subject) if subject is not None else None,
                "email": payload.get("email"),
            }
        except jwt.PyJWTError:
            return jsonify({"error": "Token inválido ou expirado"}), 401

        return view_func(*args, **kwargs)

    return wrapper
