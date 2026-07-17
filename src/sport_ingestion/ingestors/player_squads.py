from __future__ import annotations

from ..models.player_squad import PlayerSquad
from .base import BaseIngestor


class PlayerSquadIngestor(BaseIngestor):
    table = PlayerSquad.__table__
    conflict_columns = ("sport", "team_id", "player_id")

    def fetch(self) -> dict:
        return self.client.players_squads(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            team_id = team.get("id")
            for player in item.get("players", []):
                rows.append(
                    {
                        "sport": self.sport.value,
                        "team_id": team_id,
                        "player_id": player["id"],
                        "name": player.get("name"),
                        "position": player.get("position"),
                        "number": player.get("number"),
                        "photo": player.get("photo"),
                        "raw": player,
                    }
                )
        return rows
