import copy

import pytest
from api_sports import Sport
from sqlalchemy import text

from sport_ingestion.ingestors import LeagueIngestor

pytestmark = pytest.mark.integration


class FakeSportsClient:
    """Stand-in minimal: seule `.sport` et la methode de fetch utilisee comptent."""

    def __init__(self, sport, payload):
        self.sport = sport
        self.payload = payload

    def leagues(self, **params):
        return self.payload


def test_league_upsert_is_idempotent_and_updates_changed_fields(session_factory):
    payload_v1 = {
        "response": [
            {
                "league": {"id": 999, "name": "Test League", "type": "League", "logo": "logo-v1.png"},
                "country": {"name": "Testland"},
            }
        ]
    }
    client = FakeSportsClient(Sport.FOOTBALL, payload_v1)
    ingestor = LeagueIngestor(client, session_factory, id=999)

    assert ingestor.run() == 1

    with session_factory() as session:
        count = session.execute(
            text("select count(*) from leagues where sport='football' and league_id=999")
        ).scalar_one()
    assert count == 1

    payload_v2 = copy.deepcopy(payload_v1)
    payload_v2["response"][0]["league"]["logo"] = "logo-v2.png"
    client.payload = payload_v2

    assert ingestor.run() == 1

    with session_factory() as session:
        row = session.execute(
            text(
                "select logo, (select count(*) from leagues where sport='football' and league_id=999) as cnt "
                "from leagues where sport='football' and league_id=999"
            )
        ).one()
    assert row.logo == "logo-v2.png"
    assert row.cnt == 1
