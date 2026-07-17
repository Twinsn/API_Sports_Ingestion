from __future__ import annotations

from ..models.league import League
from .base import BaseIngestor


class LeagueIngestor(BaseIngestor):
    table = League.__table__
    conflict_columns = ("sport", "league_id")

    def fetch(self) -> dict:
        return self.client.leagues(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            league = item["league"]
            country = item.get("country") or {}
            rows.append(
                {
                    "sport": self.sport.value,
                    "league_id": league["id"],
                    "name": league["name"],
                    "type": league.get("type"),
                    "country_name": country.get("name"),
                    "logo": league.get("logo"),
                    "raw": item,
                }
            )
        return rows
