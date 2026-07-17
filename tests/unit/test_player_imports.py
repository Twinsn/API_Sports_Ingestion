from api_sports import Sport

from sport_ingestion.ingestors import PlayerImportIngestor


class FakeClient:
    def __init__(self, pages: dict[int, dict]):
        self.sport = Sport.FOOTBALL
        self._pages = pages
        self.calls: list[int] = []

    def players(self, page: int = 1, **params):
        self.calls.append(page)
        return self._pages[page]


def _player_payload(player_id: int, total_pages: int, page: int) -> dict:
    return {
        "response": [
            {
                "player": {"id": player_id, "name": f"Player {player_id}", "nationality": "England"},
                "statistics": [{"team": {"id": 33}, "league": {"id": 39, "season": 2023}, "goals": {"total": 3}}],
            }
        ],
        "paging": {"current": page, "total": total_pages},
    }


def test_run_paginates_until_last_page_and_upserts_each_page():
    pages = {1: _player_payload(1, 3, 1), 2: _player_payload(2, 3, 2), 3: _player_payload(3, 3, 3)}
    client = FakeClient(pages)
    ingestor = PlayerImportIngestor(client, session_factory=None, league=39, season=2023)

    upserted_batches: list[list[dict]] = []
    ingestor.upsert = lambda rows: upserted_batches.append(rows)  # court-circuite la DB

    total = ingestor.run()

    assert client.calls == [1, 2, 3]
    assert total == 3
    assert len(upserted_batches) == 3
    assert upserted_batches[0][0]["player_id"] == 1
    assert upserted_batches[2][0]["player_id"] == 3


def test_run_stops_after_a_single_page():
    client = FakeClient({1: _player_payload(1, 1, 1)})
    ingestor = PlayerImportIngestor(client, session_factory=None, league=39, season=2023)
    ingestor.upsert = lambda rows: None

    total = ingestor.run()

    assert client.calls == [1]
    assert total == 1


def test_to_rows_maps_nested_statistics():
    payload = _player_payload(909, 1, 1)
    ingestor = PlayerImportIngestor(FakeClient({}), session_factory=None)

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "sport": "football",
            "player_id": 909,
            "team_id": 33,
            "league_id": 39,
            "season": "2023",
            "name": "Player 909",
            "nationality": "England",
            "goals": 3,
            "raw": payload["response"][0],
        }
    ]
