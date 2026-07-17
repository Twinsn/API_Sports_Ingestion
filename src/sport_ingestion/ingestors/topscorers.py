from __future__ import annotations

from ..models.topscorer import Topscorer
from .base import BaseIngestor


class TopscorerIngestor(BaseIngestor):
    table = Topscorer.__table__
    conflict_columns = ("provider", "sport", "league_id", "season", "player_id")

    def fetch(self) -> dict:
        return self.client.topscorers(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            player = item["player"]
            stats_list = item.get("statistics") or [{}]
            stats = stats_list[0]
            team = stats.get("team") or {}
            league = stats.get("league") or {}
            goals = stats.get("goals") or {}
            season = league.get("season")

            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "league_id": league.get("id"),
                    "season": str(season) if season is not None else None,
                    "player_id": player["id"],
                    "name": player.get("name"),
                    "team_id": team.get("id"),
                    "goals": goals.get("total"),
                    "assists": goals.get("assists"),
                    "raw": item,
                }
            )
        return rows
