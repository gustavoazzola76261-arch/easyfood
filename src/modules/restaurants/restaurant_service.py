"""Operações e regras de domínio de restaurantes (sem HTTP)."""

import os

from sqlalchemy import or_, select

from src.database.db import get_session
from src.database.models import (
    ROLE_OWNER,
    STAFF_ROLES,
    Order,
    Restaurant,
    RestaurantStaff,
    User,
)
from src.modules.auth.authz import membership_for
from src.modules.shared.email_service import escape_text, notify_safely
from src.modules.shared.errors import AppError
from src.modules.shared.image_service import optimize_image


def list_restaurants(query: str | None = None) -> list[dict]:
    with get_session() as session:
        stmt = select(Restaurant).order_by(Restaurant.id)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(Restaurant.name.ilike(like), Restaurant.category.ilike(like))
            )
        rows = session.scalars(stmt).all()
        return [r.to_dict() for r in rows]


def get_restaurant(restaurant_id: int) -> dict:
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        return restaurant.to_dict()


def create_restaurant(data: dict, owner: dict) -> dict:
    with get_session() as session:
        restaurant = Restaurant(
            name=data["name"],
            category=data["category"],
            rating=float(data.get("rating") or 0),
            owner_id=owner["id"],
        )
        session.add(restaurant)
        session.commit()
        session.refresh(restaurant)
        created = restaurant.to_dict(role=ROLE_OWNER)
        session.add_all(
            [
                Order(
                    restaurant_id=restaurant.id,
                    customer_name="Cliente demonstração",
                    items_summary="Pedido de exemplo aguardando atendimento",
                    status="recebido",
                ),
                Order(
                    restaurant_id=restaurant.id,
                    customer_name="Maria Silva",
                    items_summary="2x item do cardápio",
                    status="em_preparo",
                ),
            ]
        )
        session.commit()

    notify_safely(
        to=owner["email"],
        to_name=owner["name"],
        subject=f"Bem-vindo à EasyFood, {created['name']}!",
        header=f"Olá, {escape_text(created['name'])}!",
        body=(
            "Seu restaurante foi cadastrado com sucesso na EasyFood.<br/>"
            f"Categoria: {escape_text(created['category'])}."
        ),
        footer="Equipe EasyFood",
    )
    notify_safely(
        to=os.getenv("EMAIL_COMMERCIAL", owner["email"]),
        to_name="Comercial EasyFood",
        subject=f"Novo restaurante cadastrado: {created['name']}",
        header="Novo restaurante na plataforma",
        body=(
            f"Nome: {escape_text(created['name'])}<br/>"
            f"Categoria: {escape_text(created['category'])}<br/>"
            f"Avaliação: {created['rating']}"
        ),
        footer="Notificação automática - EasyFood",
    )
    return created


def update_restaurant(restaurant_id: int, data: dict) -> dict:
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        if "name" in data and data["name"]:
            restaurant.name = data["name"]
        if "category" in data and data["category"]:
            restaurant.category = data["category"]
        if "rating" in data and data["rating"] is not None:
            restaurant.rating = float(data["rating"])
        session.commit()
        session.refresh(restaurant)
        return restaurant.to_dict()


def upload_restaurant_image(restaurant_id: int, buffer: bytes) -> dict:
    image_url = optimize_image(buffer, "restaurants")
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        restaurant.image_url = image_url
        session.commit()
        session.refresh(restaurant)
        return restaurant.to_dict()


def list_memberships(user_id: int) -> list[dict]:
    with get_session() as session:
        owned = session.scalars(select(Restaurant).where(Restaurant.owner_id == user_id)).all()
        staff_rows = session.scalars(
            select(RestaurantStaff).where(RestaurantStaff.user_id == user_id)
        ).all()
        staff_ids = {row.restaurant_id: row.role for row in staff_rows}
        staff_restaurants = session.scalars(
            select(Restaurant).where(Restaurant.id.in_(staff_ids.keys()))
        ).all() if staff_ids else []

        result = [r.to_dict(role=ROLE_OWNER) for r in owned]
        for restaurant in staff_restaurants:
            result.append(restaurant.to_dict(role=staff_ids[restaurant.id]))
        return result


def list_staff(restaurant_id: int) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(RestaurantStaff).where(RestaurantStaff.restaurant_id == restaurant_id)
        ).all()
        if not rows:
            return []
        users = {
            user.id: user
            for user in session.scalars(
                select(User).where(User.id.in_([row.user_id for row in rows]))
            ).all()
        }
        return [row.to_dict(users.get(row.user_id)) for row in rows]


def add_staff(restaurant_id: int, email: str, role: str) -> dict:
    if role not in STAFF_ROLES:
        raise AppError("Papel inválido. Use gerente ou atendente.", 400)
    with get_session() as session:
        restaurant = session.get(Restaurant, restaurant_id)
        if restaurant is None:
            raise AppError("Restaurante não encontrado", 404)
        user = session.scalar(select(User).where(User.email == email.strip().lower()))
        if user is None:
            user = session.scalar(select(User).where(User.email == email.strip()))
        if user is None:
            raise AppError("Usuário não encontrado com este e-mail", 404)
        if user.id == restaurant.owner_id:
            raise AppError("O dono já possui acesso total ao restaurante", 409)
        existing = session.scalar(
            select(RestaurantStaff).where(
                RestaurantStaff.restaurant_id == restaurant_id,
                RestaurantStaff.user_id == user.id,
            )
        )
        if existing:
            raise AppError("Este usuário já faz parte da equipe", 409)
        staff = RestaurantStaff(restaurant_id=restaurant_id, user_id=user.id, role=role)
        session.add(staff)
        session.commit()
        session.refresh(staff)
        return staff.to_dict(user)


def remove_staff(restaurant_id: int, user_id: int) -> None:
    with get_session() as session:
        staff = session.scalar(
            select(RestaurantStaff).where(
                RestaurantStaff.restaurant_id == restaurant_id,
                RestaurantStaff.user_id == user_id,
            )
        )
        if staff is None:
            raise AppError("Funcionário não encontrado", 404)
        session.delete(staff)
        session.commit()


def list_orders(restaurant_id: int) -> list[dict]:
    with get_session() as session:
        rows = session.scalars(
            select(Order).where(Order.restaurant_id == restaurant_id).order_by(Order.id.desc())
        ).all()
        return [row.to_dict() for row in rows]


def assert_can_manage_image(user_id: int, restaurant_id: int) -> None:
    role = membership_for(user_id, restaurant_id)
    if role != ROLE_OWNER:
        raise AppError("Apenas o dono pode alterar a imagem do restaurante", 403)
