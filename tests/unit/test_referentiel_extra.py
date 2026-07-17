from sport_ingestion.ingestors import CoachIngestor, PlayerSquadIngestor, VenueIngestor


def test_coach_to_rows(fake_client):
    payload = {
        "response": [
            {"id": 1, "name": "Pep Guardiola", "nationality": "Spain", "photo": "p.png", "team": {"id": 50, "name": "Man City"}}
        ]
    }
    ingestor = CoachIngestor(fake_client, session_factory=None, team=50)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "coach_id": 1,
            "name": "Pep Guardiola",
            "nationality": "Spain",
            "team_id": 50,
            "photo": "p.png",
            "raw": payload["response"][0],
        }
    ]


def test_venue_to_rows(fake_client):
    payload = {
        "response": [
            {"id": 556, "name": "Old Trafford", "city": "Manchester", "country": "England", "capacity": 76212}
        ]
    }
    ingestor = VenueIngestor(fake_client, session_factory=None, search="Old Trafford")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "venue_id": 556,
            "name": "Old Trafford",
            "city": "Manchester",
            "country": "England",
            "capacity": 76212,
            "raw": payload["response"][0],
        }
    ]


def test_player_squad_to_rows_flattens_players(fake_client):
    payload = {
        "response": [
            {
                "team": {"id": 33, "name": "Manchester United"},
                "players": [
                    {"id": 909, "name": "A. Onana", "number": 24, "position": "Goalkeeper", "photo": "a.png"},
                    {"id": 910, "name": "H. Maguire", "number": 5, "position": "Defender", "photo": "h.png"},
                ],
            }
        ]
    }
    ingestor = PlayerSquadIngestor(fake_client, session_factory=None, team=33)

    rows = ingestor.to_rows(payload)

    assert len(rows) == 2
    assert rows[0]["team_id"] == 33
    assert rows[0]["player_id"] == 909
    assert rows[0]["position"] == "Goalkeeper"
    assert rows[1]["player_id"] == 910
