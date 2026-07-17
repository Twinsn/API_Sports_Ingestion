from __future__ import annotations

from ..models.team import Team
from .base import BaseIngestor


class TeamIngestor(BaseIngestor):
    table = Team.__table__
    conflict_columns = ("sport", "team_id")

    def fetch(self) -> dict:
        return self.client.teams(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            team = item["team"]
            venue = item.get("venue") or {}
            rows.append(
                {
                    "sport": self.sport.value,
                    "team_id": team["id"],
                    "name": team["name"],
                    "code": team.get("code"),
                    "country_name": team.get("country"),
                    "founded": team.get("founded"),
                    "logo": team.get("logo"),
                    "venue_id": venue.get("id"),
                    "raw": item,
                }
            )
        return rows
