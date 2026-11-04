"""Controller HTTP de restaurantes."""

from flask import jsonify, request

from src.modules.restaurants import restaurant_service
from src.modules.shared.errors import AppError
from src.modules.shared.upload_middleware import read_image_file


def _handle(action):
    try:
        return action()
    except AppError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


def list_restaurants():
    query = request.args.get("q")
    return _handle(lambda: (jsonify(restaurant_service.list_restaurants(query)), 200))


def get_restaurant(restaurant_id: int):
    return _handle(lambda: (jsonify(restaurant_service.get_restaurant(restaurant_id)), 200))


def mine():
    user = request.user
    return _handle(lambda: (jsonify(restaurant_service.list_memberships(user["id"])), 200))


def create_restaurant():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    category = data.get("category")
    rating = data.get("rating", 0)
    if not name or not category:
        return jsonify({"error": "Nome e categoria são obrigatórios"}), 400

    def action():
        restaurant = restaurant_service.create_restaurant(
            {"name": name, "category": category, "rating": rating},
            request.user,
        )
        return jsonify(restaurant), 201

    return _handle(action)


def update_restaurant(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    return _handle(lambda: (jsonify(restaurant_service.update_restaurant(restaurant_id, data)), 200))


def upload_image(restaurant_id: int):
    def action():
        restaurant_service.assert_can_manage_image(request.user["id"], restaurant_id)
        buffer = read_image_file()
        return jsonify(restaurant_service.upload_restaurant_image(restaurant_id, buffer)), 200

    return _handle(action)


def list_staff(restaurant_id: int):
    return _handle(lambda: (jsonify(restaurant_service.list_staff(restaurant_id)), 200))


def add_staff(restaurant_id: int):
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    role = data.get("role")
    if not email or not role:
        return jsonify({"error": "E-mail e papel são obrigatórios"}), 400
    return _handle(lambda: (jsonify(restaurant_service.add_staff(restaurant_id, email, role)), 201))


def remove_staff(restaurant_id: int, user_id: int):
    def action():
        restaurant_service.remove_staff(restaurant_id, user_id)
        return jsonify({"ok": True}), 200

    return _handle(action)


def list_orders(restaurant_id: int):
    return _handle(lambda: (jsonify(restaurant_service.list_orders(restaurant_id)), 200))
