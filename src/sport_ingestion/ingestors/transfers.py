from __future__ import annotations

from ..models.transfer import Transfer
from .base import BaseIngestor


class TransferIngestor(BaseIngestor):
    """Aplati player.transfers[] (l'API groupe l'historique par joueur)."""

    table = Transfer.__table__
    conflict_columns = ("sport", "player_id", "date", "team_in_id")

    def fetch(self) -> dict:
        return self.client.transfers(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            player = item["player"]
            for transfer in item.get("transfers", []):
                teams = transfer.get("teams") or {}
                team_in = teams.get("in") or {}
                team_out = teams.get("out") or {}
                rows.append(
                    {
                        "sport": self.sport.value,
                        "player_id": player["id"],
                        "date": transfer.get("date") or "",
                        "team_in_id": team_in.get("id") or 0,
                        "team_out_id": team_out.get("id"),
                        "type": transfer.get("type"),
                        "raw": transfer,
                    }
                )
        return rows
