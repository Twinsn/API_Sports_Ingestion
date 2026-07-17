from __future__ import annotations

from ..models.match_player_rating import MatchPlayerRating
from .base import BaseIngestor


def _parse_rating(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class MatchPlayerRatingIngestor(BaseIngestor):
    """Necessite le filtre fixture=<id> (l'API ne le renvoie pas dans chaque item)."""

    table = MatchPlayerRating.__table__
    conflict_columns = ("provider", "sport", "fixture_id", "team_id", "player_id")

    def fetch(self) -> dict:
        return self.client.game_players(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        fixture_id = self.filters.get("fixture")
        rows = []
        for item in payload.get("response", []):
            team = item.get("team") or {}
            team_id = team.get("id")
            for entry in item.get("players", []):
                player = entry["player"]
                stats_list = entry.get("statistics") or [{}]
                games = stats_list[0].get("games") or {}
                rows.append(
                    {
                        "provider": self.provider,
                        "sport": self.sport.value,
                        "fixture_id": fixture_id,
                        "team_id": team_id,
                        "player_id": player["id"],
                        "name": player.get("name"),
                        "rating": _parse_rating(games.get("rating")),
                        "raw": entry,
                    }
                )
        return rows
