from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL_ENV_VAR = "DATABASE_URL"


def build_engine(database_url: str | None = None) -> Engine:
    url = database_url or os.environ.get(DATABASE_URL_ENV_VAR)
    if not url:
        raise RuntimeError(f"{DATABASE_URL_ENV_VAR} non defini (variable d'env ou argument).")
    return create_engine(url, pool_pre_ping=True, future=True)


def build_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=build_engine(database_url), expire_on_commit=False)
