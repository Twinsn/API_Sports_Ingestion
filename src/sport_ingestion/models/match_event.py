from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class MatchEvent(Base):
    """Un evenement de match (but, carton, remplacement) -- /fixtures/events.

    L'API ne fournit AUCUN identifiant stable par evenement: la cle d'upsert est
    donc une combinaison de champs qui identifie l'evenement en pratique (minute,
    minute additionnelle, type, detail, joueur). Limite connue et acceptee: deux
    evenements strictement identiques sur ces 5 champs (meme equipe, meme minute
    exacte y compris temps additionnel, meme type/detail, meme joueur) ecraseraient
    l'un l'autre -- cas extremement rare en pratique.
    """

    __tablename__ = "match_events"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    elapsed: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    elapsed_extra: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    type: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="")
    detail: Mapped[str] = mapped_column(String(64), primary_key=True, server_default="")
    player_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    raw: Mapped[dict] = mapped_column(JSONB)
