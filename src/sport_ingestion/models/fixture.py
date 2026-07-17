from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Fixture(Base):
    __tablename__ = "fixtures"
    __table_args__ = (
        Index("ix_fixtures_sport_league_season", "sport", "league_id", "season"),
        Index("ix_fixtures_sport_date", "sport", "date"),
    )

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    fixture_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    league_id: Mapped[int | None] = mapped_column(Integer)
    season: Mapped[str | None] = mapped_column(String(16))
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status_short: Mapped[str | None] = mapped_column(String(8))
    status_long: Mapped[str | None] = mapped_column(String(64))
    home_team_id: Mapped[int | None] = mapped_column(Integer)
    away_team_id: Mapped[int | None] = mapped_column(Integer)
    home_goals: Mapped[int | None] = mapped_column(Integer)
    away_goals: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict] = mapped_column(JSONB)
