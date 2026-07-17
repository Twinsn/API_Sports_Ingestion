from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class TeamStatistic(Base):
    """Stats agregees d'une equipe sur une ligue/saison (/teams/statistics).

    Contrairement aux autres endpoints, /teams/statistics renvoie un OBJET unique
    dans "response" (pas une liste) -- un seul appel = une seule ligne.
    """

    __tablename__ = "team_statistics"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    league_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season: Mapped[str] = mapped_column(String(16), primary_key=True)
    form: Mapped[str | None] = mapped_column(String(64))
    played_total: Mapped[int | None] = mapped_column(Integer)
    wins_total: Mapped[int | None] = mapped_column(Integer)
    draws_total: Mapped[int | None] = mapped_column(Integer)
    loses_total: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict] = mapped_column(JSONB)
