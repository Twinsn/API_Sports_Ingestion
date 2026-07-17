from __future__ import annotations

from datetime import datetime

from ..models.fixture import Fixture
from .base import BaseIngestor


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class FixtureIngestor(BaseIngestor):
    """Ingestor generique pour l'endpoint "matchs" (fixtures/games selon le sport).

    Football imbrique les infos sous une cle "fixture" (`item["fixture"]["id"]`, ...)
    et expose les scores sous "goals". Les autres sports (basketball, etc.) exposent
    l'id/la date/le statut directement au niveau racine et les scores sous "scores".
    On absorbe cette variance sans code specifique par sport.
    """

    table = Fixture.__table__
    conflict_columns = ("provider", "sport", "fixture_id")

    def fetch(self) -> dict:
        return self.client.games(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            fixture = item.get("fixture", item)
            league = item.get("league") or {}
            teams = item.get("teams") or {}
            home = teams.get("home") or {}
            away = teams.get("away") or {}
            status = fixture.get("status") or {}
            goals = item.get("goals") or {}
            scores = item.get("scores") or {}
            home_goals = goals.get("home", (scores.get("home") or {}).get("total"))
            away_goals = goals.get("away", (scores.get("away") or {}).get("total"))
            season = league.get("season")

            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "fixture_id": fixture["id"],
                    "league_id": league.get("id"),
                    "season": str(season) if season is not None else None,
                    "date": _parse_date(fixture.get("date")),
                    "status_short": status.get("short"),
                    "status_long": status.get("long"),
                    "home_team_id": home.get("id"),
                    "away_team_id": away.get("id"),
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "raw": item,
                }
            )
        return rows
