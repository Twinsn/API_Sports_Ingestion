from sport_ingestion.ingestors import TransferIngestor


def test_to_rows_flattens_transfer_history_per_player(fake_client):
    payload = {
        "response": [
            {
                "player": {"id": 909, "name": "J. Sancho"},
                "update": "2024-01-01T00:00:00+00:00",
                "transfers": [
                    {"date": "2021-07-01", "type": "Transfer", "teams": {"in": {"id": 33}, "out": {"id": 165}}},
                    {"date": "2023-08-31", "type": "Loan", "teams": {"in": {"id": 165}, "out": {"id": 33}}},
                ],
            }
        ]
    }
    ingestor = TransferIngestor(fake_client, session_factory=None, player=909)

    rows = ingestor.to_rows(payload)

    assert len(rows) == 2
    assert rows[0] == {
        "provider": "api_sports",
        "sport": "football",
        "player_id": 909,
        "date": "2021-07-01",
        "team_in_id": 33,
        "team_out_id": 165,
        "type": "Transfer",
        "raw": payload["response"][0]["transfers"][0],
    }
    assert rows[1]["date"] == "2023-08-31"
    assert rows[1]["team_in_id"] == 165
