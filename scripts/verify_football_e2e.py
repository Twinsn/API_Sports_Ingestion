"""Verification bout-en-bout avec la vraie API (plan Free, saison=2023).

Usage: uv run python scripts/verify_football_e2e.py
Necessite DATABASE_URL et API_SPORTS_KEY dans l'environnement (.env).
"""

from __future__ import annotations

import datetime

from api_sports import Sport, SportsClient

from sport_ingestion.db.session import build_session_factory
from sport_ingestion.ingestors import FixtureIngestor, LeagueIngestor, StandingIngestor, TeamIngestor

LEAGUE_ID = 61  # Ligue 1 -- deja confirmee accessible avec la cle en place
SEASON = 2023  # plan Free: historique limite a 2022-2024
TODAY = datetime.date.today().isoformat()


def main() -> None:
    session_factory = build_session_factory()

    football = SportsClient(Sport.FOOTBALL)
    n_leagues = LeagueIngestor(football, session_factory, id=LEAGUE_ID).run()
    print(f"[football] leagues: {n_leagues} ligne(s)")

    n_teams = TeamIngestor(football, session_factory, league=LEAGUE_ID, season=SEASON).run()
    print(f"[football] teams: {n_teams} ligne(s)")

    n_standings = StandingIngestor(football, session_factory, league=LEAGUE_ID, season=SEASON).run()
    print(f"[football] standings: {n_standings} ligne(s)")

    n_fixtures = FixtureIngestor(football, session_factory, date=TODAY).run()
    print(f"[football] fixtures ({TODAY}): {n_fixtures} ligne(s)")
    print(f"[football] quota restant: {football.last_rate_limit}")

    # Check leger basketball: confirme le chemin saison-string et la non-collision
    # des cles composites (sport inclus) avec les donnees football deja en base.
    basketball = SportsClient(Sport.BASKETBALL)
    n_bb_standings = StandingIngestor(basketball, session_factory, league=12, season="2023-2024").run()
    print(f"[basketball] standings: {n_bb_standings} ligne(s)")
    print(f"[basketball] quota restant: {basketball.last_rate_limit}")


if __name__ == "__main__":
    main()
