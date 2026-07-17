from __future__ import annotations

from ..models.team_statistic import TeamStatistic
from .base import BaseIngestor


class TeamStatisticIngestor(BaseIngestor):
    """/teams/statistics renvoie un objet unique dans "response" (pas une liste)."""

    table = TeamStatistic.__table__
    conflict_columns = ("provider", "sport", "team_id", "league_id", "season")

    def fetch(self) -> dict:
        return self.client.team_statistics(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        data = payload.get("response")
        if not data:
            return []

        team = data.get("team") or {}
        league = data.get("league") or {}
        fixtures = data.get("fixtures") or {}
        season = league.get("season")

        def total(key: str) -> int | None:
            return (fixtures.get(key) or {}).get("total")

        return [
            {
                "provider": self.provider,
                "sport": self.sport.value,
                "team_id": team.get("id"),
                "league_id": league.get("id"),
                "season": str(season) if season is not None else None,
                "form": data.get("form"),
                "played_total": total("played"),
                "wins_total": total("wins"),
                "draws_total": total("draws"),
                "loses_total": total("loses"),
                "raw": data,
            }
        ]
