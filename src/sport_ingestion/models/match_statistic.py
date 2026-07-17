from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class MatchStatistic(Base):
    """Une ligne = les stats d'une equipe pour un match (/fixtures/statistics).

    Le detail (tir au but, possession, corners...) reste dans `raw` -- la liste de
    types de stats varie selon le sport/la competition, pas de colonne dediee par stat.
    """

    __tablename__ = "match_statistics"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw: Mapped[dict] = mapped_column(JSONB)
