from api_sports import Sport

from sport_ingestion.ingestors import LeagueIngestor


def test_run_dedupes_rows_colliding_on_the_conflict_key(fake_client):
    """Postgres refuse qu'un ON CONFLICT touche deux fois la meme ligne dans une
    seule requete -- to_rows() peut renvoyer des doublons de cle naturelle (observe
    en conditions reelles sur /transfers). run() ne doit jamais planter dessus."""
    payload = {
        "response": [
            {"league": {"id": 39, "name": "Premier League v1"}, "country": {}},
            {"league": {"id": 39, "name": "Premier League v2"}, "country": {}},
        ]
    }
    ingestor = LeagueIngestor(fake_client, session_factory=None)
    ingestor.fetch = lambda: payload

    upserted = []
    ingestor.upsert = lambda rows: upserted.append(rows)

    total = ingestor.run()

    assert total == 1
    assert len(upserted[0]) == 1
    assert upserted[0][0]["name"] == "Premier League v2"
