"""Operações e regras de domínio de restaurantes (sem HTTP)."""

from sqlalchemy import select

from src.database.db import get_session
from src.database.models import Restaurant


def list_restaurants() -> list[dict]:
    with get_session() as session:
        rows = session.scalars(select(Restaurant).order_by(Restaurant.id)).all()
        return [r.to_dict() for r in rows]


def create_restaurant(data: dict) -> dict:
    with get_session() as session:
        restaurant = Restaurant(
            name=data["name"],
            category=data["category"],
            rating=float(data.get("rating") or 0),
        )
        session.add(restaurant)
        session.commit()
        session.refresh(restaurant)
        return restaurant.to_dict()
