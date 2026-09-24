"""Configuração dos testes: SQLite em memória, isolado do Postgres local."""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-easyfood"

import pytest

from src.app import create_app
from src.database.db import Base, engine


@pytest.fixture()
def app():
    Base.metadata.create_all(engine)
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    yield flask_app
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(app):
    return app.test_client()
