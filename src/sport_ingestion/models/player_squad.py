from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class PlayerSquad(Base):
    """Une ligne = un joueur dans l'effectif d'une equipe (/players/squads)."""

    __tablename__ = "player_squads"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[str | None] = mapped_column(String(32))
    number: Mapped[int | None] = mapped_column(Integer)
    photo: Mapped[str | None] = mapped_column(String(512))
    raw: Mapped[dict] = mapped_column(JSONB)
