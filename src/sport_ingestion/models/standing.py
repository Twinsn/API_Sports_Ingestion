from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Standing(Base):
    __tablename__ = "standings"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    league_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[str] = mapped_column(String(16), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Non-nullable avec defaut "": une valeur NULL casserait l'unicite Postgres
    # (NULL != NULL), ce qui autoriserait des doublons pour les ligues sans groupe.
    group_name: Mapped[str] = mapped_column(String(64), primary_key=True, server_default="")

    rank: Mapped[int | None] = mapped_column(Integer)
    points: Mapped[int | None] = mapped_column(Integer)
    goals_diff: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict] = mapped_column(JSONB)
