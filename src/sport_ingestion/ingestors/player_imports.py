from __future__ import annotations

from ..models.player_import import PlayerImport
from .base import BaseIngestor


class PlayerImportIngestor(BaseIngestor):
    """Import bulk de /players, endpoint PAGINE (~20/page cote API-Sports).

    `run()` est surcharge pour parcourir toutes les pages (payload["paging"]) et
    upsert page par page, plutot que de faire une seule requete comme les autres
    ingestors -- c'est le seul endpoint du catalogue qui pagine.
    """

    table = PlayerImport.__table__
    conflict_columns = ("provider", "sport", "player_id", "team_id", "league_id", "season")

    def fetch(self, page: int = 1) -> dict:
        return self.client.players(page=page, **self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            player = item["player"]
            for stats in item.get("statistics", []):
                team = stats.get("team") or {}
                league = stats.get("league") or {}
                goals = stats.get("goals") or {}
                season = league.get("season")
                rows.append(
                    {
                        "provider": self.provider,
                        "sport": self.sport.value,
                        "player_id": player["id"],
                        "team_id": team.get("id") or 0,
                        "league_id": league.get("id") or 0,
                        "season": str(season) if season is not None else "",
                        "name": player.get("name"),
                        "nationality": player.get("nationality"),
                        "goals": goals.get("total"),
                        "raw": item,
                    }
                )
        return rows

    def run(self) -> int:
        total_rows = 0
        page = 1
        while True:
            payload = self.fetch(page=page)
            rows = self.to_rows(payload)
            if rows:
                rows = self._dedupe(rows)
                self.upsert(rows)
                total_rows += len(rows)
            paging = payload.get("paging") or {}
            if page >= paging.get("total", 1):
                break
            page += 1
        return total_rows
