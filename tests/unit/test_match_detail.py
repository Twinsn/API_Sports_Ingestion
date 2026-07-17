from sport_ingestion.ingestors import (
    LineupIngestor,
    MatchEventIngestor,
    MatchPlayerRatingIngestor,
    MatchStatisticIngestor,
)


def test_lineup_to_rows_reads_fixture_id_from_filters(fake_client):
    payload = {
        "response": [
            {"team": {"id": 33, "name": "Man United"}, "coach": {"id": 1, "name": "E. ten Hag"}, "formation": "4-2-3-1"}
        ]
    }
    ingestor = LineupIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "fixture_id": 1498633,
            "team_id": 33,
            "formation": "4-2-3-1",
            "coach_id": 1,
            "raw": payload["response"][0],
        }
    ]


def test_match_statistic_to_rows_keeps_stats_in_raw(fake_client):
    payload = {
        "response": [
            {"team": {"id": 33}, "statistics": [{"type": "Shots on Goal", "value": 5}]}
        ]
    }
    ingestor = MatchStatisticIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows == [{"sport": "football", "fixture_id": 1498633, "team_id": 33, "raw": payload["response"][0]}]


def test_match_player_rating_parses_string_rating(fake_client):
    payload = {
        "response": [
            {
                "team": {"id": 33},
                "players": [
                    {"player": {"id": 909, "name": "A. Onana"}, "statistics": [{"games": {"rating": "7.2"}}]},
                    {"player": {"id": 910, "name": "H. Maguire"}, "statistics": [{"games": {"rating": None}}]},
                ],
            }
        ]
    }
    ingestor = MatchPlayerRatingIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows[0]["rating"] == 7.2
    assert rows[1]["rating"] is None


def test_match_event_to_rows_defaults_missing_fields_for_composite_key(fake_client):
    payload = {
        "response": [
            {
                "time": {"elapsed": 34, "extra": None},
                "team": {"id": 33},
                "player": {"id": 909, "name": "Goal scorer"},
                "type": "Goal",
                "detail": "Normal Goal",
            },
            # Evenement sans joueur (ex: VAR) -- ne doit pas crasher, retombe sur la sentinelle 0.
            {"time": {"elapsed": 45}, "team": {"id": 33}, "type": "Var", "detail": "Goal cancelled"},
        ]
    }
    ingestor = MatchEventIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows[0]["elapsed_extra"] == 0
    assert rows[0]["player_id"] == 909
    assert rows[1]["player_id"] == 0
    assert rows[1]["elapsed"] == 45
