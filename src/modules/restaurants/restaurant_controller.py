"""Controller HTTP de restaurantes."""

from flask import jsonify, request

from src.modules.restaurants import restaurant_service


def list_restaurants():
    try:
        restaurants = restaurant_service.list_restaurants()
        return jsonify(restaurants)
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


def create_restaurant():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    category = data.get("category")
    rating = data.get("rating", 0)

    if not name or not category:
        return jsonify({"error": "Nome e categoria são obrigatórios"}), 400

    try:
        restaurant = restaurant_service.create_restaurant(
            {"name": name, "category": category, "rating": rating}
        )
        return jsonify(restaurant), 201
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
