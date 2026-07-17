from __future__ import annotations

from ..models.coach import Coach
from .base import BaseIngestor


class CoachIngestor(BaseIngestor):
    table = Coach.__table__
    conflict_columns = ("sport", "coach_id")

    def fetch(self) -> dict:
        return self.client.coachs(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            rows.append(
                {
                    "sport": self.sport.value,
                    "coach_id": item["id"],
                    "name": item.get("name"),
                    "nationality": item.get("nationality"),
                    "team_id": team.get("id"),
                    "photo": item.get("photo"),
                    "raw": item,
                }
            )
        return rows
