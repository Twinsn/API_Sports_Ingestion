from sport_ingestion.ingestors import TeamStatisticIngestor


def test_to_rows_handles_single_object_response(fake_client):
    payload = {
        "response": {
            "team": {"id": 33, "name": "Manchester United"},
            "league": {"id": 39, "name": "Premier League", "season": 2023},
            "form": "WWDLW",
            "fixtures": {
                "played": {"home": 19, "away": 19, "total": 38},
                "wins": {"home": 12, "away": 8, "total": 20},
                "draws": {"home": 3, "away": 3, "total": 6},
                "loses": {"home": 4, "away": 8, "total": 12},
            },
        }
    }
    ingestor = TeamStatisticIngestor(fake_client, session_factory=None, team=33, league=39, season=2023)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "team_id": 33,
            "league_id": 39,
            "season": "2023",
            "form": "WWDLW",
            "played_total": 38,
            "wins_total": 20,
            "draws_total": 6,
            "loses_total": 12,
            "raw": payload["response"],
        }
    ]


def test_to_rows_empty_when_response_is_falsy(fake_client):
    ingestor = TeamStatisticIngestor(fake_client, session_factory=None, team=33, league=39, season=2023)
    assert ingestor.to_rows({"response": {}}) == []
    assert ingestor.to_rows({"response": None}) == []
