import os

import pytest
from sqlalchemy.orm import sessionmaker

from sport_ingestion import models  # noqa: F401  (enregistre les modeles sur Base.metadata)
from sport_ingestion.db.base import Base
from sport_ingestion.db.session import build_engine

TEST_DATABASE_URL_ENV_VAR = "TEST_DATABASE_URL"
DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://sport_ingestion:sport_ingestion@localhost:5432/sport_ingestion"


@pytest.fixture(scope="session")
def engine():
    url = os.environ.get(TEST_DATABASE_URL_ENV_VAR, DEFAULT_TEST_DATABASE_URL)
    eng = build_engine(url)
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session_factory(engine):
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
