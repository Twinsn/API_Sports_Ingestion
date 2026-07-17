from sport_ingestion.ingestors import TopscorerIngestor


def test_to_rows_maps_player_and_first_statistics_entry(fake_client):
    payload = {
        "response": [
            {
                "player": {"id": 909, "name": "E. Haaland", "photo": "e.png"},
                "statistics": [
                    {
                        "team": {"id": 50, "name": "Manchester City"},
                        "league": {"id": 39, "season": 2023},
                        "goals": {"total": 27, "assists": 5},
                    }
                ],
            }
        ]
    }
    ingestor = TopscorerIngestor(fake_client, session_factory=None, league=39, season=2023)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "league_id": 39,
            "season": "2023",
            "player_id": 909,
            "name": "E. Haaland",
            "team_id": 50,
            "goals": 27,
            "assists": 5,
            "raw": payload["response"][0],
        }
    ]
