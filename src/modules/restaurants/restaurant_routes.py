"""Rotas do módulo de restaurantes."""

from flask import Blueprint

from src.database.models import ROLE_ATENDENTE, ROLE_GERENTE, ROLE_OWNER
from src.modules.auth.auth_middleware import authenticate
from src.modules.auth.authz import require_restaurant_roles
from src.modules.restaurants import restaurant_controller

restaurant_bp = Blueprint("restaurants", __name__)

restaurant_bp.get("/")(restaurant_controller.list_restaurants)
restaurant_bp.get("/mine")(authenticate(restaurant_controller.mine))
restaurant_bp.post("/")(authenticate(restaurant_controller.create_restaurant))
restaurant_bp.get("/<int:restaurant_id>")(restaurant_controller.get_restaurant)
restaurant_bp.patch("/<int:restaurant_id>")(
    authenticate(require_restaurant_roles(ROLE_OWNER)(restaurant_controller.update_restaurant))
)
restaurant_bp.post("/<int:restaurant_id>/image")(
    authenticate(require_restaurant_roles(ROLE_OWNER)(restaurant_controller.upload_image))
)
restaurant_bp.get("/<int:restaurant_id>/staff")(
    authenticate(require_restaurant_roles(ROLE_OWNER)(restaurant_controller.list_staff))
)
restaurant_bp.post("/<int:restaurant_id>/staff")(
    authenticate(require_restaurant_roles(ROLE_OWNER)(restaurant_controller.add_staff))
)
restaurant_bp.delete("/<int:restaurant_id>/staff/<int:user_id>")(
    authenticate(require_restaurant_roles(ROLE_OWNER)(restaurant_controller.remove_staff))
)
restaurant_bp.get("/<int:restaurant_id>/orders")(
    authenticate(
        require_restaurant_roles(ROLE_OWNER, ROLE_GERENTE, ROLE_ATENDENTE)(
            restaurant_controller.list_orders
        )
    )
)
