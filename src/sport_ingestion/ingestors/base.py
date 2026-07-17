from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from api_sports import Sport, SportsClient
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, sessionmaker


class BaseIngestor(ABC):
    """Fetch une ressource pour un sport/jeu de filtres et l'upsert en base.

    Les sous-classes declarent `table` et `conflict_columns` (la cle naturelle,
    incluant "provider" et "sport") et implementent `fetch()` + `to_rows()`.
    `to_rows()` est pure (pas d'I/O), ce qui la rend testable sans base de donnees.

    `provider` identifie la source de donnees (ex. "api_sports") -- a ne pas
    confondre avec le `provider` de `SportsClient` (qui choisit entre l'API
    directe api-sports.io et RapidAPI, un detail de transport interne a la lib).
    Ici, c'est ce qui permet de brancher demain une 2e source (TheSportsDB, ESPN...)
    sans collision: deux fournisseurs peuvent tres bien attribuer le meme id
    numerique a deux entites differentes.
    """

    table: Table
    conflict_columns: tuple[str, ...]

    def __init__(
        self,
        client: SportsClient,
        session_factory: sessionmaker[Session],
        *,
        provider: str = "api_sports",
        **filters: Any,
    ) -> None:
        self.client = client
        self.session_factory = session_factory
        self.sport: Sport = client.sport
        self.provider = provider
        self.filters = filters

    @abstractmethod
    def fetch(self) -> dict:
        """Appelle la bonne methode de SportsClient avec self.filters; renvoie l'enveloppe brute."""

    @abstractmethod
    def to_rows(self, payload: dict) -> list[dict]:
        """Mappe les items de payload['response'] vers des dicts de colonnes de `table`."""

    def run(self) -> int:
        rows = self.to_rows(self.fetch())
        if not rows:
            return 0
        rows = self._dedupe(rows)
        self.upsert(rows)
        return len(rows)

    def _dedupe(self, rows: list[dict]) -> list[dict]:
        """Postgres refuse qu'un ON CONFLICT touche deux fois la meme ligne dans une
        seule requete ("CardinalityViolation"). Certains endpoints peuvent renvoyer
        plusieurs entrees qui retombent sur la meme cle naturelle (observe sur
        /transfers) -- on ne garde que la derniere occurrence par cle."""
        deduped: dict[tuple, dict] = {}
        for row in rows:
            key = tuple(row[c] for c in self.conflict_columns)
            deduped[key] = row
        return list(deduped.values())

    def upsert(self, rows: list[dict]) -> None:
        rows = self._dedupe(rows)  # defense en profondeur si upsert() est appele directement
        stmt = pg_insert(self.table).values(rows)
        update_cols = {
            c.name: stmt.excluded[c.name]
            for c in self.table.columns
            if c.name not in self.conflict_columns
        }
        stmt = stmt.on_conflict_do_update(index_elements=list(self.conflict_columns), set_=update_cols)
        with self.session_factory.begin() as session:
            session.execute(stmt)
