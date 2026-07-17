from sport_ingestion.ingestors import TeamIngestor


def test_to_rows_maps_team_and_venue_fields(fake_client, load_fixture):
    ingestor = TeamIngestor(fake_client, session_factory=None, league=39, season=2023)
    payload = load_fixture("teams_response.json")

    rows = ingestor.to_rows(payload)

    assert rows == [
        {
            "provider": "api_sports",
            "sport": "football",
            "team_id": 33,
            "name": "Manchester United",
            "code": "MUN",
            "country_name": "England",
            "founded": 1878,
            "logo": "https://media.api-sports.io/football/teams/33.png",
            "venue_id": 556,
            "raw": payload["response"][0],
        }
    ]
