from sport_ingestion.ingestors import PredictionIngestor


def test_to_rows_reads_fixture_id_from_filters(fake_client):
    payload = {
        "response": [
            {
                "predictions": {
                    "winner": {"id": 33, "name": "Manchester United", "comment": None},
                    "advice": "Combo double chance : Manchester United or draw and -3.5 goals",
                }
            }
        ]
    }
    ingestor = PredictionIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "fixture_id": 1498633,
            "winner_team_id": 33,
            "advice": "Combo double chance : Manchester United or draw and -3.5 goals",
            "raw": payload["response"][0],
        }
    ]
