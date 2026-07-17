from __future__ import annotations

from ..models.standing import Standing
from .base import BaseIngestor


class StandingIngestor(BaseIngestor):
    table = Standing.__table__
    conflict_columns = ("sport", "league_id", "season", "team_id", "group_name")

    def fetch(self) -> dict:
        return self.client.standings(**self.filters)

    def to_rows(self, payload: dict) -> list[dict]:
        # Deux formes reelles co-existent selon le sport:
        # - football: response = [{"league": {id, season, "standings": [[entry, ...], ...]}}]
        #   (groupes imbriques sous un seul objet league partage)
        # - basketball (et probablement d'autres): response = [[entry, ...]] -- chaque
        #   entree porte deja son propre "league" (id/season) et un "group" imbrique
        #   ({"name": ...}) plutot qu'une simple chaine, et "position"/"points" au lieu
        #   de "rank"/points-entier ("points" est un dict {"for","against"}).
        entries: list[dict] = []
        for item in payload.get("response", []):
            if isinstance(item, list):
                entries.extend(item)
                continue
            league = item.get("league") or {}
            for group in league.get("standings") or []:
                for entry in group:
                    entry = dict(entry)
                    entry.setdefault("league", {"id": league.get("id"), "season": league.get("season")})
                    entries.append(entry)

        rows = []
        for entry in entries:
            team = entry["team"]
            league = entry.get("league") or {}
            season = league.get("season")

            group_name = entry.get("group")
            if isinstance(group_name, dict):
                group_name = group_name.get("name")

            points = entry.get("points")
            if isinstance(points, dict):
                points = points.get("for")

            rows.append(
                {
                    "sport": self.sport.value,
                    "league_id": league.get("id"),
                    "season": str(season) if season is not None else None,
                    "team_id": team["id"],
                    "group_name": group_name or "",
                    "rank": entry.get("rank", entry.get("position")),
                    "points": points,
                    "goals_diff": entry.get("goalsDiff"),
                    "raw": entry,
                }
            )
        return rows
