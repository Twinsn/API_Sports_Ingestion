from __future__ import annotations

from ..models.match_event import MatchEvent
from .base import BaseIngestor


class MatchEventIngestor(BaseIngestor):
    """Necessite le filtre fixture=<id> (l'API ne le renvoie pas dans chaque item).

    Voir MatchEvent pour la limite connue sur la cle composite (pas d'id stable
    fourni par l'API pour un evenement).
    """

    table = MatchEvent.__table__
    conflict_columns = ("sport", "fixture_id", "team_id", "elapsed", "elapsed_extra", "type", "detail", "player_id")

    def fetch(self) -> dict:
        return self.client.game_events(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        fixture_id = self.filters.get("fixture")
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            player = item.get("player") or {}
            time = item.get("time") or {}
            rows.append(
                {
                    "sport": self.sport.value,
                    "fixture_id": fixture_id,
                    "team_id": team.get("id"),
                    "elapsed": time.get("elapsed") or 0,
                    "elapsed_extra": time.get("extra") or 0,
                    "type": item.get("type") or "",
                    "detail": item.get("detail") or "",
                    "player_id": player.get("id") or 0,
                    "raw": item,
                }
            )
        return rows
