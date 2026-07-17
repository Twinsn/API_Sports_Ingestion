from __future__ import annotations

from ..models.lineup import Lineup
from .base import BaseIngestor


class LineupIngestor(BaseIngestor):
    """Necessite le filtre fixture=<id> (l'API ne le renvoie pas dans chaque item)."""

    table = Lineup.__table__
    conflict_columns = ("provider", "sport", "fixture_id", "team_id")

    def fetch(self) -> dict:
        return self.client.game_lineups(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        fixture_id = self.filters.get("fixture")
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            coach = item.get("coach") or {}
            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "fixture_id": fixture_id,
                    "team_id": team.get("id"),
                    "formation": item.get("formation"),
                    "coach_id": coach.get("id"),
                    "raw": item,
                }
            )
        return rows
