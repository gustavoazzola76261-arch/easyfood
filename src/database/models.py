"""Modelos de persistência."""

from sqlalchemy.orm import Mapped, mapped_column

from src.database.db import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(default=0.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "rating": self.rating,
        }
