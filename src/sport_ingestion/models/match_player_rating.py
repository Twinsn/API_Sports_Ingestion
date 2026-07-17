from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class MatchPlayerRating(Base):
    __tablename__ = "match_player_ratings"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    rating: Mapped[float | None] = mapped_column(Float)
    raw: Mapped[dict] = mapped_column(JSONB)
