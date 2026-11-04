"""Regras de autenticação: registro, login e emissão de JWT."""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.database.db import get_session
from src.database.models import User
from src.modules.shared.email_service import escape_text, notify_safely

JWT_SECRET = os.getenv("JWT_SECRET", "troque-por-uma-chave-longa-e-aleatoria")
JWT_EXPIRES_HOURS = 24


class EmailAlreadyExistsError(Exception):
    pass


def register(*, name: str, email: str, password: str) -> dict:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with get_session() as session:
            user = User(name=name, email=email, password=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            public = user.to_public_dict()
    except IntegrityError as exc:
        raise EmailAlreadyExistsError from exc

    notify_safely(
        to=email,
        to_name=name,
        subject="Conta criada na EasyFood",
        header=f"Olá, {escape_text(name)}!",
        body="Sua conta foi criada com sucesso. Agora você pode explorar restaurantes e, se quiser, cadastrar o seu.",
        footer="Equipe EasyFood",
    )
    return public


def login(*, email: str, password: str) -> dict | None:
    with get_session() as session:
        user = session.scalar(select(User).where(User.email == email))
        if user is None:
            return None

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return None

        token = jwt.encode(
            {
                "sub": str(user.id),
                "email": user.email,
                "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRES_HOURS),
            },
            JWT_SECRET,
            algorithm="HS256",
        )
        return {
            "token": token,
            "user": user.to_public_dict(),
        }


def get_user(user_id: int) -> dict | None:
    with get_session() as session:
        user = session.get(User, user_id)
        return user.to_public_dict() if user else None
