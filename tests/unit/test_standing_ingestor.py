from api_sports import Sport

from sport_ingestion.ingestors import StandingIngestor


def test_to_rows_flattens_groups_and_stringifies_season(fake_client, load_fixture):
    ingestor = StandingIngestor(fake_client, session_factory=None, league=39, season=2023)
    payload = load_fixture("standings_response.json")

    rows = ingestor.to_rows(payload)

    assert len(rows) == 2
    assert rows[0]["season"] == "2023"
    assert rows[0]["team_id"] == 50
    assert rows[0]["rank"] == 1
    assert rows[0]["points"] == 89
    assert rows[0]["group_name"] == "Premier League"
    assert rows[1]["team_id"] == 42
    assert rows[1]["rank"] == 2


def test_to_rows_defaults_group_name_when_missing(fake_client):
    payload = {
        "response": [
            {
                "league": {
                    "id": 1,
                    "season": 2023,
                    "standings": [[{"rank": 1, "team": {"id": 10}, "points": 5, "goalsDiff": 2}]],
                }
            }
        ]
    }
    ingestor = StandingIngestor(fake_client, session_factory=None, league=1, season=2023)

    rows = ingestor.to_rows(payload)

    assert rows[0]["group_name"] == ""


def test_to_rows_maps_flat_basketball_shape(load_fixture):
    client = type("FakeClient", (), {"sport": Sport.BASKETBALL})()
    ingestor = StandingIngestor(client, session_factory=None, league=12, season="2023-2024")
    payload = load_fixture("basketball_standings_response.json")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "provider": "api_sports",
            "sport": "basketball",
            "league_id": 12,
            "season": "2023-2024",
            "team_id": 152,
            "group_name": "Western Conference",
            "rank": 1,
            "points": 9847,
            "goals_diff": None,
            "raw": payload["response"][0][0],
        }
    ]
