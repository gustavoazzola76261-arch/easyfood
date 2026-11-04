"""Autorização por papel no restaurante: dono, gerente ou atendente."""

from functools import wraps

from flask import jsonify, request
from sqlalchemy import select

from src.database.db import get_session
from src.database.models import ROLE_OWNER, Restaurant, RestaurantStaff
from src.modules.shared.errors import AppError


def membership_for(user_id: int, restaurant_id: int) -> str | None:
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        if restaurant.owner_id == user_id:
            return ROLE_OWNER
        staff = session.scalar(
            select(RestaurantStaff).where(
                RestaurantStaff.restaurant_id == restaurant_id,
                RestaurantStaff.user_id == user_id,
            )
        )
        return staff.role if staff else None


def require_restaurant_roles(*roles: str):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(restaurant_id: int, *args, **kwargs):
            user = getattr(request, "user", None) or {}
            user_id = user.get("id")
            if not user_id:
                return jsonify({"error": "Token não fornecido"}), 401
            try:
                role = membership_for(user_id, restaurant_id)
            except AppError as exc:
                return jsonify({"error": exc.message}), exc.status_code
            if role not in roles:
                return jsonify({"error": "Você não tem permissão para esta ação"}), 403
            request.membership_role = role
            return view_func(restaurant_id, *args, **kwargs)

        return wrapper

    return decorator
