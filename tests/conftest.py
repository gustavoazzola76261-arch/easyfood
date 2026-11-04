"""Configuração dos testes: SQLite em memória, isolado do Postgres local."""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-easyfood"
os.environ.pop("EMAIL_API_KEY", None)

import pytest

from src.app import create_app
from src.database.db import Base, engine


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    Base.metadata.create_all(engine)
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    yield flask_app
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_login(client, name="Ana", email="ana@easyfood.com", password="senha123"):
    client.post("/auth/register", json={"name": name, "email": email, "password": password})
    login = client.post("/auth/login", json={"email": email, "password": password})
    body = login.get_json()
    return body["token"], body["user"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
