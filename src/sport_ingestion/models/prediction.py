from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    winner_team_id: Mapped[int | None] = mapped_column(Integer)
    advice: Mapped[str | None] = mapped_column(String(255))
    raw: Mapped[dict] = mapped_column(JSONB)
