"""Controller HTTP de cardápio."""

from flask import jsonify, request

from src.modules.dishes import dish_service
from src.modules.shared.errors import AppError
from src.modules.shared.upload_middleware import read_image_file


def _handle(action):
    try:
        return action()
    except AppError as exc:
        return jsonify({"error": exc.message}), exc.status_code
    except Exception:
        return jsonify({"error": "Erro interno ao processar cardápio"}), 500


def list_dishes(restaurant_id: int):
    return _handle(lambda: (jsonify(dish_service.list_dishes(restaurant_id)), 200))


def create_dish(restaurant_id: int):
    data = request.get_json(silent=True) or {}

    def action():
        dish_service._require_menu_role(request.user["id"], restaurant_id)
        return jsonify(dish_service.create_dish(restaurant_id, data, request.user)), 201

    return _handle(action)


def delete_dish(restaurant_id: int, dish_id: int):
    def action():
        dish_service._require_menu_role(request.user["id"], restaurant_id)
        dish_service.delete_dish(restaurant_id, dish_id)
        return jsonify({"ok": True}), 200

    return _handle(action)


def upload_image(dish_id: int):
    def action():
        buffer = read_image_file()
        dish = dish_service.upload_dish_image(dish_id, buffer, request.user["id"])
        return jsonify(dish), 200

    return _handle(action)
