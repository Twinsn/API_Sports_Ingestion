from __future__ import annotations

from .fixtures import FixtureIngestor


class HeadToHeadIngestor(FixtureIngestor):
    """/fixtures/headtohead renvoie la meme forme que /fixtures: on reutilise
    entierement le mapping et la table de FixtureIngestor, seul fetch() change."""

    def __init__(
        self, client, session_factory, team1: int, team2: int, *, provider: str = "api_sports", **filters
    ) -> None:
        super().__init__(client, session_factory, provider=provider, **filters)
        self.team1 = team1
        self.team2 = team2

    def fetch(self) -> dict:
        return self.client.head_to_head(self.team1, self.team2, **self.filters)
