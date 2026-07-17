from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class League(Base):
    __tablename__ = "leagues"

    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    league_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(32))
    country_name: Mapped[str | None] = mapped_column(String(255))
    logo: Mapped[str | None] = mapped_column(String(512))
    raw: Mapped[dict] = mapped_column(JSONB)
