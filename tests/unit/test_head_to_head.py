from api_sports import Sport

from sport_ingestion.ingestors import HeadToHeadIngestor


class FakeClient:
    def __init__(self):
        self.sport = Sport.FOOTBALL
        self.calls = []

    def head_to_head(self, team1, team2, **params):
        self.calls.append((team1, team2, params))
        return {"response": []}


def test_fetch_delegates_to_client_head_to_head_with_team_ids():
    client = FakeClient()
    ingestor = HeadToHeadIngestor(client, None, 33, 40, last=10)

    ingestor.fetch()

    assert client.calls == [(33, 40, {"last": 10})]


def test_reuses_fixture_mapping():
    payload = {
        "response": [
            {
                "fixture": {"id": 1, "date": "2024-01-01T00:00:00+00:00", "status": {"short": "FT", "long": "Match Finished"}},
                "league": {"id": 39, "season": 2023},
                "teams": {"home": {"id": 33}, "away": {"id": 40}},
                "goals": {"home": 1, "away": 0},
            }
        ]
    }
    ingestor = HeadToHeadIngestor(FakeClient(), None, 33, 40)

    rows = ingestor.to_rows(payload)

    assert rows[0]["fixture_id"] == 1
    assert rows[0]["home_team_id"] == 33
    assert rows[0]["away_team_id"] == 40
