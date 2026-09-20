"""Rotas do módulo de restaurantes."""

from flask import Blueprint

from src.modules.restaurants import restaurant_controller

restaurant_bp = Blueprint("restaurants", __name__)

restaurant_bp.get("/")(restaurant_controller.list_restaurants)
restaurant_bp.post("/")(restaurant_controller.create_restaurant)
