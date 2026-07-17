from __future__ import annotations

from ..models.prediction import Prediction
from .base import BaseIngestor


class PredictionIngestor(BaseIngestor):
    """Necessite le filtre fixture=<id> (l'API ne le renvoie pas dans l'item)."""

    table = Prediction.__table__
    conflict_columns = ("provider", "sport", "fixture_id")

    def fetch(self) -> dict:
        return self.client.predictions(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        fixture_id = self.filters.get("fixture")
        rows = []
        for item in payload.get("response", []):
            predictions = item.get("predictions") or {}
            winner = predictions.get("winner") or {}
            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "fixture_id": fixture_id,
                    "winner_team_id": winner.get("id"),
                    "advice": predictions.get("advice"),
                    "raw": item,
                }
            )
        return rows
