from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class PlayerImport(Base):
    """Import bulk d'un joueur pour une equipe/ligue/saison (/players, pagine).

    Une ligne par (joueur, equipe, ligue, saison): un joueur transfere en cours de
    saison a plusieurs entrees "statistics" (une par equipe), d'ou cette cle.
    """

    __tablename__ = "player_imports"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    league_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    season: Mapped[str] = mapped_column(String(16), primary_key=True, server_default="")
    name: Mapped[str | None] = mapped_column(String(255))
    nationality: Mapped[str | None] = mapped_column(String(255))
    goals: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict] = mapped_column(JSONB)
