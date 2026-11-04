"""Modelos de persistência."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.db import Base

ROLE_OWNER = "owner"
ROLE_GERENTE = "gerente"
ROLE_ATENDENTE = "atendente"
STAFF_ROLES = (ROLE_GERENTE, ROLE_ATENDENTE)
DISH_KINDS = ("prato", "bebida", "sobremesa")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(default=0.0)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def to_dict(self, role: str | None = None) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "rating": self.rating,
            "ownerId": self.owner_id,
            "imageUrl": self.image_url,
        }
        if role is not None:
            data["role"] = role
        return data


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    portion: Mapped[str | None] = mapped_column(String(40), nullable=True)
    kind: Mapped[str] = mapped_column(String(20), default="prato")
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "portion": self.portion,
            "kind": self.kind,
            "imageUrl": self.image_url,
            "restaurantId": self.restaurant_id,
        }


class RestaurantStaff(Base):
    __tablename__ = "restaurant_staff"
    __table_args__ = (UniqueConstraint("restaurant_id", "user_id", name="uq_restaurant_staff"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    def to_dict(self, user: User | None = None) -> dict:
        data = {
            "id": self.id,
            "restaurantId": self.restaurant_id,
            "userId": self.user_id,
            "role": self.role,
        }
        if user is not None:
            data["user"] = user.to_public_dict()
        return data


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    customer_name: Mapped[str] = mapped_column(nullable=False)
    items_summary: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="recebido")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "restaurantId": self.restaurant_id,
            "customerName": self.customer_name,
            "itemsSummary": self.items_summary,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
