from sport_ingestion.ingestors import TeamIngestor


def test_upsert_resolves_master_team_id_before_delegating(fake_client, monkeypatch):
    """Verifie le branchement (sans DB reelle): upsert() doit attribuer un
    master_team_id a chaque ligne avant d'appeler la logique d'upsert generique."""
    rows = [
        {"provider": "api_sports", "sport": "football", "team_id": 33, "name": "Man United"},
        {"provider": "api_sports", "sport": "football", "team_id": 40, "name": "Liverpool"},
    ]

    resolved_calls = []

    def fake_resolve(session, provider, sport, team_id):
        resolved_calls.append((provider, sport, team_id))
        return 1000 + team_id

    monkeypatch.setattr("sport_ingestion.ingestors.teams.TeamResolver.resolve", staticmethod(fake_resolve))

    class FakeSession:
        def begin(self):
            return self

        def __enter__(self):
            return "fake-session"

        def __exit__(self, *exc):
            return False

    ingestor = TeamIngestor(fake_client, session_factory=FakeSession())

    delegated = []
    from sport_ingestion.ingestors.base import BaseIngestor

    monkeypatch.setattr(BaseIngestor, "upsert", lambda self, rows: delegated.append(rows))

    ingestor.upsert(rows)

    assert resolved_calls == [("api_sports", "football", 33), ("api_sports", "football", 40)]
    assert delegated[0][0]["master_team_id"] == 1033
    assert delegated[0][1]["master_team_id"] == 1040
