"""Regras de cardápio: pratos, bebidas e sobremesas."""

from sqlalchemy import select

from src.database.db import get_session
from src.database.models import DISH_KINDS, ROLE_GERENTE, ROLE_OWNER, Dish, Restaurant, User
from src.modules.auth.authz import membership_for
from src.modules.shared.email_service import escape_text, notify_safely
from src.modules.shared.errors import AppError
from src.modules.shared.image_service import optimize_image

MENU_ROLES = (ROLE_OWNER, ROLE_GERENTE)


def _require_menu_role(user_id: int, restaurant_id: int) -> str:
    role = membership_for(user_id, restaurant_id)
    if role not in MENU_ROLES:
        raise AppError("Apenas o dono ou o gerente podem alterar o cardápio", 403)
    return role


def list_dishes(restaurant_id: int) -> list[dict]:
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        rows = session.scalars(
            select(Dish).where(Dish.restaurant_id == restaurant_id).order_by(Dish.id)
        ).all()
        return [row.to_dict() for row in rows]


def create_dish(restaurant_id: int, data: dict, owner_notify: dict | None = None) -> dict:
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    price = data.get("price")
    kind = (data.get("kind") or "prato").strip().lower()
    portion = (data.get("portion") or "").strip() or None

    if not name or not description or price is None:
        raise AppError("Nome, descrição e preço são obrigatórios", 400)
    if kind not in DISH_KINDS:
        raise AppError("Tipo inválido. Use prato, bebida ou sobremesa.", 400)
    try:
        price_value = float(price)
    except (TypeError, ValueError) as exc:
        raise AppError("Preço inválido", 400) from exc
    if price_value < 0:
        raise AppError("Preço inválido", 400)

    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        dish = Dish(
            name=name,
            description=description,
            price=price_value,
            portion=portion,
            kind=kind,
            restaurant_id=restaurant_id,
        )
        session.add(dish)
        session.commit()
        session.refresh(dish)
        created = dish.to_dict()
        restaurant_name = restaurant.name
        owner_id = restaurant.owner_id

    if owner_notify:
        notify_safely(
            to=owner_notify["email"],
            to_name=owner_notify["name"],
            subject=f"Novo item no cardápio de {restaurant_name}",
            header="Item cadastrado",
            body=(
                f"{escape_text(created['name'])} foi adicionado ao cardápio "
                f"de {escape_text(restaurant_name)}."
            ),
            footer="Equipe EasyFood",
        )
    elif owner_id:
        with get_session() as session:
            owner = session.get(User, owner_id)
        if owner:
            notify_safely(
                to=owner.email,
                to_name=owner.name,
                subject=f"Novo item no cardápio de {restaurant_name}",
                header="Item cadastrado",
                body=(
                    f"{escape_text(created['name'])} foi adicionado ao cardápio "
                    f"de {escape_text(restaurant_name)}."
                ),
                footer="Equipe EasyFood",
            )
    return created


def delete_dish(restaurant_id: int, dish_id: int) -> None:
    with get_session() as session:
        dish = session.get(Dish, dish_id)
        if dish is None or dish.restaurant_id != restaurant_id:
            raise AppError("Prato não encontrado", 404)
        session.delete(dish)
        session.commit()


def upload_dish_image(dish_id: int, buffer: bytes, user_id: int) -> dict:
    with get_session() as session:
        dish = session.get(Dish, dish_id)
        if dish is None:
            raise AppError("Prato não encontrado", 404)
        restaurant_id = dish.restaurant_id

    _require_menu_role(user_id, restaurant_id)
    image_url = optimize_image(buffer, "dishes")

    with get_session() as session:
        dish = session.get(Dish, dish_id)
        dish.image_url = image_url
        session.commit()
        session.refresh(dish)
        return dish.to_dict()
