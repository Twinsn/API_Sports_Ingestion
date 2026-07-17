from sport_ingestion.ingestors import OddIngestor


def test_prematch_odds_one_row_per_bookmaker(fake_client):
    payload = {
        "response": [
            {
                "fixture": {"id": 1498633},
                "bookmakers": [
                    {"id": 6, "name": "Bwin", "bets": [{"id": 1, "name": "Match Winner"}]},
                    {"id": 8, "name": "Betfair", "bets": [{"id": 1, "name": "Match Winner"}]},
                ],
            }
        ]
    }
    ingestor = OddIngestor(fake_client, session_factory=None, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert len(rows) == 2
    assert rows[0] == {
        "provider": "api_sports",
        "sport": "football",
        "fixture_id": 1498633,
        "bookmaker_id": 6,
        "is_live": False,
        "bookmaker_name": "Bwin",
        "raw": payload["response"][0]["bookmakers"][0],
    }
    assert rows[1]["bookmaker_id"] == 8


def test_live_odds_without_bookmaker_breakdown_falls_back_to_sentinel(fake_client):
    payload = {"response": [{"fixture": {"id": 1498633}, "odds": [{"id": 1, "name": "Match Winner"}]}]}
    ingestor = OddIngestor(fake_client, session_factory=None, is_live=True, fixture=1498633)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "provider": "api_sports",
            "sport": "football",
            "fixture_id": 1498633,
            "bookmaker_id": 0,
            "is_live": True,
            "bookmaker_name": None,
            "raw": payload["response"][0],
        }
    ]


def test_is_live_flag_selects_the_right_client_method():
    calls = []

    class FakeClient:
        sport = None

        def odds(self, **params):
            calls.append(("odds", params))
            return {"response": []}

        def odds_live(self, **params):
            calls.append(("odds_live", params))
            return {"response": []}

    from api_sports import Sport

    client = FakeClient()
    client.sport = Sport.FOOTBALL

    OddIngestor(client, session_factory=None, fixture=1).fetch()
    OddIngestor(client, session_factory=None, is_live=True, fixture=1).fetch()

    assert calls == [("odds", {"fixture": 1}), ("odds_live", {"fixture": 1})]
