import pytest
from api_sports import Sport

from sport_ingestion.identity import TeamResolver
from sport_ingestion.ingestors import TeamIngestor

pytestmark = pytest.mark.integration


class FakeSportsClient:
    def __init__(self, sport, payload):
        self.sport = sport
        self.payload = payload

    def teams(self, **params):
        return self.payload


def _team_payload(team_id: int, name: str) -> dict:
    return {
        "response": [
            {
                "team": {"id": team_id, "name": name, "code": None, "country": "England", "founded": 1900},
                "venue": {"id": 1},
            }
        ]
    }


def test_resolve_is_idempotent_and_creates_distinct_ids_per_source(session_factory):
    with session_factory() as session:
        first = TeamResolver.resolve(session, "api_sports", "football", 33)
        again = TeamResolver.resolve(session, "api_sports", "football", 33)
        other_provider = TeamResolver.resolve(session, "thesportsdb", "football", 999)
        session.commit()

    assert again == first  # meme source, meme id -> meme master_team_id
    assert other_provider != first  # sources differentes -> pas de collision


def test_link_reattaches_a_source_to_an_existing_master_id(session_factory):
    with session_factory() as session:
        master_id = TeamResolver.resolve(session, "api_sports", "football", 33)
        TeamResolver.link(session, "thesportsdb", "football", 42, master_id)
        session.commit()

    with session_factory() as session:
        resolved = TeamResolver.resolve(session, "thesportsdb", "football", 42)
    assert resolved == master_id


def test_two_providers_ingesting_the_same_real_team_do_not_collide_in_teams_table(session_factory):
    """Manchester United vu par deux fournisseurs fictifs avec des ids differents:
    2 lignes distinctes dans `teams` (cle incluant provider), pas de collision, et
    on peut les relier au meme master_team_id via TeamResolver.link()."""
    api_sports_client = FakeSportsClient(Sport.FOOTBALL, _team_payload(33, "Manchester United"))
    other_client = FakeSportsClient(Sport.FOOTBALL, _team_payload(9001, "Man Utd (autre source)"))

    n1 = TeamIngestor(api_sports_client, session_factory, provider="api_sports").run()
    n2 = TeamIngestor(other_client, session_factory, provider="thesportsdb").run()

    assert n1 == 1
    assert n2 == 1

    from sqlalchemy import text

    with session_factory() as session:
        rows = session.execute(
            text(
                "select provider, team_id, master_team_id from teams "
                "where (provider, team_id) in (('api_sports', 33), ('thesportsdb', 9001))"
            )
        ).all()

    assert len(rows) == 2
    master_ids = {row.master_team_id for row in rows}
    assert len(master_ids) == 2  # pas encore relies -> deux master_team_id distincts

    with session_factory() as session:
        shared_master = session.execute(
            text("select master_team_id from teams where provider='api_sports' and team_id=33")
        ).scalar_one()
        TeamResolver.link(session, "thesportsdb", "football", 9001, shared_master)
        session.commit()

    with session_factory() as session:
        assert TeamResolver.resolve(session, "thesportsdb", "football", 9001) == shared_master
