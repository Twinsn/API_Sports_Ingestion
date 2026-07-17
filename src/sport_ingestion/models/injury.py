from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Injury(Base):
    __tablename__ = "injuries"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    # sentinelle 0 si l'API renvoie une entree sans contexte de match precis
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int | None] = mapped_column(Integer)
    type: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str | None] = mapped_column(String(255))
    raw: Mapped[dict] = mapped_column(JSONB)
