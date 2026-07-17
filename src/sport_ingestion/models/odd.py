from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Odd(Base):
    """Cotes d'un bookmaker pour un match, pre-match ou live (/odds, /odds/live).

    bookmaker_id a un defaut (0) car le flux live n'a pas toujours de decoupage par
    bookmaker -- cette valeur sentinelle permet quand meme une cle composite NOT NULL.
    """

    __tablename__ = "odds"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bookmaker_id: Mapped[int] = mapped_column(Integer, primary_key=True, server_default="0")
    is_live: Mapped[bool] = mapped_column(Boolean, primary_key=True, server_default="false")
    bookmaker_name: Mapped[str | None] = mapped_column(String(255))
    raw: Mapped[dict] = mapped_column(JSONB)
