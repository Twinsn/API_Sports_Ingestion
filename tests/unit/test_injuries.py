from sport_ingestion.ingestors import InjuryIngestor


def test_to_rows_maps_player_team_fixture(fake_client):
    payload = {
        "response": [
            {
                "player": {"id": 909, "name": "L. Martinez", "photo": "l.png"},
                "team": {"id": 33, "name": "Manchester United"},
                "fixture": {"id": 1498633, "date": "2026-07-14T19:00:00+00:00"},
                "league": {"id": 39, "season": 2023},
                "type": "Missing Fixture",
                "reason": "Injury",
            }
        ]
    }
    ingestor = InjuryIngestor(fake_client, session_factory=None, league=39, season=2023)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "fixture_id": 1498633,
            "player_id": 909,
            "team_id": 33,
            "type": "Missing Fixture",
            "reason": "Injury",
            "raw": payload["response"][0],
        }
    ]


def test_to_rows_defaults_fixture_id_when_missing(fake_client):
    payload = {"response": [{"player": {"id": 909}, "team": {"id": 33}, "type": "Missing Fixture"}]}
    ingestor = InjuryIngestor(fake_client, session_factory=None, league=39, season=2023)

    rows = ingestor.to_rows(payload)

    assert rows[0]["fixture_id"] == 0
