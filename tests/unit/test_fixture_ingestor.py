from datetime import datetime, timezone

from api_sports import Sport

from sport_ingestion.ingestors import FixtureIngestor


def test_to_rows_maps_football_fixture_shape(fake_client, load_fixture):
    ingestor = FixtureIngestor(fake_client, session_factory=None, date="2026-07-14")
    payload = load_fixture("fixtures_response.json")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "fixture_id": 1498633,
            "league_id": 39,
            "season": "2026",
            "date": datetime(2026, 7, 14, 19, 0, 0, tzinfo=timezone.utc),
            "status_short": "FT",
            "status_long": "Match Finished",
            "home_team_id": 33,
            "away_team_id": 40,
            "home_goals": 2,
            "away_goals": 1,
            "raw": payload["response"][0],
        }
    ]


def test_to_rows_maps_flat_games_shape_eg_basketball(load_fixture):
    client = type("FakeClient", (), {"sport": Sport.BASKETBALL})()
    ingestor = FixtureIngestor(client, session_factory=None, date="2026-07-14")
    payload = load_fixture("basketball_games_response.json")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "basketball",
            "fixture_id": 336745,
            "league_id": 12,
            "season": "2025-2026",
            "date": datetime(2026, 7, 14, 19, 0, 0, tzinfo=timezone.utc),
            "status_short": "FT",
            "status_long": "Finished",
            "home_team_id": 145,
            "away_team_id": 139,
            "home_goals": 102,
            "away_goals": 98,
            "raw": payload["response"][0],
        }
    ]
