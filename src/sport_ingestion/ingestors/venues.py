from __future__ import annotations

from ..models.venue import Venue
from .base import BaseIngestor


class VenueIngestor(BaseIngestor):
    table = Venue.__table__
    conflict_columns = ("provider", "sport", "venue_id")

    def fetch(self) -> dict:
        return self.client.venues(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "venue_id": item["id"],
                    "name": item.get("name"),
                    "city": item.get("city"),
                    "country": item.get("country"),
                    "capacity": item.get("capacity"),
                    "raw": item,
                }
            )
        return rows
