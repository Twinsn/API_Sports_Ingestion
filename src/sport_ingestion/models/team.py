from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class Team(Base):
    __tablename__ = "teams"

    provider: Mapped[str] = mapped_column(String(32), primary_key=True, server_default="api_sports")
    sport: Mapped[str] = mapped_column(String(32), primary_key=True)
    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str | None] = mapped_column(String(16))
    country_name: Mapped[str | None] = mapped_column(String(255))
    founded: Mapped[int | None] = mapped_column(Integer)
    logo: Mapped[str | None] = mapped_column(String(512))
    venue_id: Mapped[int | None] = mapped_column(Integer)
    # Pointe vers team_identity_map.master_team_id: meme equipe reelle, quelle que
    # soit la source qui l'a decrite. Alimente par TeamIngestor.upsert().
    master_team_id: Mapped[int | None] = mapped_column(Integer)
    raw: Mapped[dict] = mapped_column(JSONB)
