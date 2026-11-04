"""Rotas do módulo de cardápio."""

from flask import Blueprint

from src.modules.auth.auth_middleware import authenticate
from src.modules.dishes import dish_controller

dish_bp = Blueprint("dishes", __name__)

dish_bp.get("/restaurants/<int:restaurant_id>/dishes")(dish_controller.list_dishes)
dish_bp.post("/restaurants/<int:restaurant_id>/dishes")(
    authenticate(dish_controller.create_dish)
)
dish_bp.delete("/restaurants/<int:restaurant_id>/dishes/<int:dish_id>")(
    authenticate(dish_controller.delete_dish)
)
dish_bp.post("/dishes/<int:dish_id>/image")(authenticate(dish_controller.upload_image))
