"""EasyFood — API com persistência (Missão 3).

GET e POST /restaurants via SQLAlchemy + SQLite.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///easyfood.db")

app = Flask(__name__)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


class Base(DeclarativeBase):
    pass


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


def init_db() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.scalar(select(Restaurant).limit(1)) is None:
            session.add_all(
                [
                    Restaurant(name="Pizzaria Napoli", category="Pizza", rating=4.8),
                    Restaurant(name="Burger House", category="Burger", rating=4.7),
                    Restaurant(name="Sushi House", category="Sushi", rating=4.9),
                ]
            )
            session.commit()


@app.get("/restaurants")
def list_restaurants():
    try:
        with Session(engine) as session:
            rows = session.scalars(select(Restaurant).order_by(Restaurant.id)).all()
            return jsonify([r.to_dict() for r in rows])
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@app.post("/restaurants")
def create_restaurant():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    category = data.get("category")
    rating = data.get("rating", 0)

    if not name or not category:
        return jsonify({"error": "Nome e categoria são obrigatórios"}), 400

    try:
        with Session(engine) as session:
            restaurant = Restaurant(
                name=name,
                category=category,
                rating=float(rating) if rating is not None else 0.0,
            )
            session.add(restaurant)
            session.commit()
            session.refresh(restaurant)
            return jsonify(restaurant.to_dict()), 201
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    init_db()
    print("EasyFood rodando na porta 3000")
    app.run(host="0.0.0.0", port=3000, debug=True)
