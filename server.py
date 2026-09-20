"""EasyFood — ponto de entrada do servidor.

Responsabilidade única: carregar ambiente, inicializar o banco e ligar o servidor.
"""

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import select

from src.app import create_app
from src.database.db import Base, engine, get_session
from src.database.models import Restaurant


def init_db() -> None:
    Base.metadata.create_all(engine)
    with get_session() as session:
        if session.scalar(select(Restaurant).limit(1)) is None:
            session.add_all(
                [
                    Restaurant(name="Pizzaria Napoli", category="Pizza", rating=4.8),
                    Restaurant(name="Burger House", category="Burger", rating=4.7),
                    Restaurant(name="Sushi House", category="Sushi", rating=4.9),
                ]
            )
            session.commit()


app = create_app()


if __name__ == "__main__":
    init_db()
    print("EasyFood rodando na porta 3000")
    app.run(host="0.0.0.0", port=3000, debug=True)
