from __future__ import annotations

from ..models.odd import Odd
from .base import BaseIngestor


class OddIngestor(BaseIngestor):
    """Cotes pre-match (/odds) ou live (/odds/live) selon `is_live`.

    Forme pre-match: un item par match, avec une liste "bookmakers" (un bookmaker =
    une ligne). Forme live observee: pas toujours de decoupage par bookmaker -- dans
    ce cas bookmaker_id retombe sur la sentinelle 0 (voir Odd).
    """

    table = Odd.__table__
    conflict_columns = ("provider", "sport", "fixture_id", "bookmaker_id", "is_live")

    def __init__(
        self, client, session_factory, *, is_live: bool = False, provider: str = "api_sports", **filters
    ) -> None:
        super().__init__(client, session_factory, provider=provider, **filters)
        self.is_live = is_live

    def fetch(self) -> dict:
        if self.is_live:
            return self.client.odds_live(**self.filters)
        return self.client.odds(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            fixture = item.get("fixture") or {}
            fixture_id = fixture.get("id") or self.filters.get("fixture")
            bookmakers = item.get("bookmakers")

            if bookmakers:
                for bookmaker in bookmakers:
                    rows.append(
                        {
                            "provider": self.provider,
                            "sport": self.sport.value,
                            "fixture_id": fixture_id,
                            "bookmaker_id": bookmaker.get("id") or 0,
                            "is_live": self.is_live,
                            "bookmaker_name": bookmaker.get("name"),
                            "raw": bookmaker,
                        }
                    )
            else:
                rows.append(
                    {
                        "provider": self.provider,
                        "sport": self.sport.value,
                        "fixture_id": fixture_id,
                        "bookmaker_id": 0,
                        "is_live": self.is_live,
                        "bookmaker_name": None,
                        "raw": item,
                    }
                )
        return rows
