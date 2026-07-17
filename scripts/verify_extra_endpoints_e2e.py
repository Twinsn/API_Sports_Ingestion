"""Verification bout-en-bout des ingestors ajoutes pour completer le catalogue.

Usage: uv run python scripts/verify_extra_endpoints_e2e.py
Necessite DATABASE_URL et API_SPORTS_KEY dans l'environnement (.env).
Reutilise Premier League (39), Man United (33) et un fixture deja connu comme
"termine" (1498633, confirme lors d'une session precedente avoir des events reels).
"""

from __future__ import annotations

import time

from api_sports import Sport, SportsClient

from sport_ingestion.db.session import build_session_factory
from sport_ingestion.ingestors import (
    CoachIngestor,
    HeadToHeadIngestor,
    InjuryIngestor,
    LineupIngestor,
    MatchEventIngestor,
    MatchPlayerRatingIngestor,
    MatchStatisticIngestor,
    OddIngestor,
    PlayerSquadIngestor,
    PredictionIngestor,
    TeamStatisticIngestor,
    TopscorerIngestor,
    TransferIngestor,
    VenueIngestor,
)

LEAGUE_ID = 39  # Premier League
TEAM_ID = 33  # Manchester United
OPPONENT_ID = 40  # Liverpool
SEASON = 2023
FIXTURE_ID = 1498633  # match termine, deja confirme avec des events reels


def run(label: str, ingestor) -> None:
    try:
        n = ingestor.run()
        print(f"[ok] {label}: {n} ligne(s)")
    except Exception as exc:  # noqa: BLE001 -- verification manuelle, on veut voir chaque echec sans stopper le reste
        print(f"[erreur] {label}: {exc!r}")
    time.sleep(7)  # reste sous la limite 10 req/min du plan Free


def main() -> None:
    session_factory = build_session_factory()
    football = SportsClient(Sport.FOOTBALL)

    run("coachs", CoachIngestor(football, session_factory, team=TEAM_ID))
    run("venues", VenueIngestor(football, session_factory, search="Old Trafford"))
    run("player_squads", PlayerSquadIngestor(football, session_factory, team=TEAM_ID))
    run("team_statistics", TeamStatisticIngestor(football, session_factory, team=TEAM_ID, league=LEAGUE_ID, season=SEASON))
    run("topscorers", TopscorerIngestor(football, session_factory, league=LEAGUE_ID, season=SEASON))
    run("injuries", InjuryIngestor(football, session_factory, league=LEAGUE_ID, season=SEASON))
    run("transfers", TransferIngestor(football, session_factory, team=TEAM_ID))
    run("head_to_head", HeadToHeadIngestor(football, session_factory, TEAM_ID, OPPONENT_ID))

    run("lineups", LineupIngestor(football, session_factory, fixture=FIXTURE_ID))
    run("match_statistics", MatchStatisticIngestor(football, session_factory, fixture=FIXTURE_ID))
    run("match_player_ratings", MatchPlayerRatingIngestor(football, session_factory, fixture=FIXTURE_ID))
    run("match_events", MatchEventIngestor(football, session_factory, fixture=FIXTURE_ID))
    run("odds", OddIngestor(football, session_factory, fixture=FIXTURE_ID))
    run("predictions", PredictionIngestor(football, session_factory, fixture=FIXTURE_ID))

    print(f"\nquota restant: {football.last_rate_limit}")


if __name__ == "__main__":
    main()
