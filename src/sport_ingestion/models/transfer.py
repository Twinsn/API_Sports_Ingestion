from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Transfer(Base):
    """Un transfert = un evenement de l'historique d'un joueur (/transfers).

    La reponse groupe les transferts par joueur (`player.transfers: [...]`); on
    aplati en une ligne par evenement de transfert.
    """

    __tablename__ = "transfers"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(String(16), primary_key=True)
    team_in_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    team_out_id: Mapped[int | None] = mapped_column(Integer)
    type: Mapped[str | None] = mapped_column(String(64))
    raw: Mapped[dict] = mapped_column(JSONB)
