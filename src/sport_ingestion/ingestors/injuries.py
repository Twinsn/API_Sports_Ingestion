from __future__ import annotations

from ..models.injury import Injury
from .base import BaseIngestor


class InjuryIngestor(BaseIngestor):
    table = Injury.__table__
    conflict_columns = ("provider", "sport", "fixture_id", "player_id")

    def fetch(self) -> dict:
        return self.client.injuries(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            player = item["player"]
            team = item.get("team") or {}
            fixture = item.get("fixture") or {}
            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "fixture_id": fixture.get("id") or 0,
                    "player_id": player["id"],
                    "team_id": team.get("id"),
                    "type": item.get("type"),
                    "reason": item.get("reason"),
                    "raw": item,
                }
            )
        return rows
