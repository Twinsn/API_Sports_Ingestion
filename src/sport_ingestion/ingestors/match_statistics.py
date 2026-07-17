from __future__ import annotations

from ..models.match_statistic import MatchStatistic
from .base import BaseIngestor


class MatchStatisticIngestor(BaseIngestor):
    """Necessite le filtre fixture=<id> (l'API ne le renvoie pas dans chaque item)."""

    table = MatchStatistic.__table__
    conflict_columns = ("sport", "fixture_id", "team_id")

    def fetch(self) -> dict:
        return self.client.game_statistics(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        fixture_id = self.filters.get("fixture")
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            rows.append(
                {
                    "sport": self.sport.value,
                    "fixture_id": fixture_id,
                    "team_id": team.get("id"),
                    "raw": item,
                }
            )
        return rows
