"""Relie manuellement l'equipe d'une source a un master_team_id deja connu.

Usage:
    uv run python scripts/link_team.py <provider> <sport> <team_id> <master_team_id>

Pour trouver le master_team_id d'une equipe deja en base (ex. cote api_sports):
    SELECT master_team_id FROM teams WHERE provider='api_sports' AND team_id=33;

C'est une action volontairement manuelle: identifier que deux ids de sources
differentes designent la meme equipe reelle (par nom/pays/stade) n'est pas
automatise ici -- a faire au cas par cas, ou via un futur script de
rapprochement une fois qu'une 2e source existe reellement.
"""

from __future__ import annotations

import sys

from sport_ingestion.db.session import build_session_factory
from sport_ingestion.identity import TeamResolver


def main() -> None:
    if len(sys.argv) != 5:
        print("Usage: link_team.py <provider> <sport> <team_id> <master_team_id>")
        raise SystemExit(1)

    provider, sport, team_id, master_team_id = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

    session_factory = build_session_factory()
    with session_factory() as session:
        TeamResolver.link(session, provider, sport, team_id, master_team_id)
        session.commit()

    print(f"OK: ({provider}, {sport}, {team_id}) -> master_team_id={master_team_id}")


if __name__ == "__main__":
    main()
