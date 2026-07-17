"""Cree les tables en base a partir des modeles SQLAlchemy.

Tient lieu de "migration" pour la v1: pas d'Alembic tant que le schema n'est
pas stabilise (cf. plan). Idempotent: create_all() ne touche pas aux tables
deja existantes.
"""

from sport_ingestion import models  # noqa: F401  (enregistre les modeles sur Base.metadata)
from sport_ingestion.db.base import Base
from sport_ingestion.db.session import build_engine

if __name__ == "__main__":
    engine = build_engine()
    Base.metadata.create_all(engine)
    print(f"Tables creees: {sorted(Base.metadata.tables.keys())}")
