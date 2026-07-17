from sport_ingestion.ingestors import LeagueIngestor


def test_to_rows_maps_league_fields(fake_client, load_fixture):
    ingestor = LeagueIngestor(fake_client, session_factory=None, id=39)
    payload = load_fixture("leagues_response.json")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "provider": "api_sports",
            "sport": "football",
            "league_id": 39,
            "name": "Premier League",
            "type": "League",
            "country_name": "England",
            "logo": "https://media.api-sports.io/football/leagues/39.png",
            "raw": payload["response"][0],
        }
    ]


def test_to_rows_empty_response(fake_client):
    ingestor = LeagueIngestor(fake_client, session_factory=None)
    assert ingestor.to_rows({"response": []}) == []
