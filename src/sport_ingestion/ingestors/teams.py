from __future__ import annotations

from ..identity import TeamResolver
from ..models.team import Team
from .base import BaseIngestor


class TeamIngestor(BaseIngestor):
    table = Team.__table__
    conflict_columns = ("provider", "sport", "team_id")

    def fetch(self) -> dict:
        return self.client.teams(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        rows = []
        for item in payload.get("response", []):
            team = item["team"]
            venue = item.get("venue") or {}
            rows.append(
                {
                    "provider": self.provider,
                    "sport": self.sport.value,
                    "team_id": team["id"],
                    "name": team["name"],
                    "code": team.get("code"),
                    "country_name": team.get("country"),
                    "founded": team.get("founded"),
                    "logo": team.get("logo"),
                    "venue_id": venue.get("id"),
                    "raw": item,
                }
            )
        return rows

    def upsert(self, rows: list[dict]) -> None:
        # Resolution d'identite avant l'upsert bulk: chaque ligne recoit son
        # master_team_id (nouveau ou deja connu pour ce provider/sport/team_id).
        with self.session_factory.begin() as session:
            for row in rows:
                row["master_team_id"] = TeamResolver.resolve(session, row["provider"], row["sport"], row["team_id"])
        super().upsert(rows)
