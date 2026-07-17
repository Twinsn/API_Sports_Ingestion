from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from api_sports import Sport, SportsClient
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, sessionmaker


class BaseIngestor(ABC):
    """Fetch une ressource API-Sports pour un sport/jeu de filtres et l'upsert en base.

    Les sous-classes declarent `table` et `conflict_columns` (la cle naturelle,
    incluant "sport") et implementent `fetch()` + `to_rows()`. `to_rows()` est pure
    (pas d'I/O), ce qui la rend testable sans base de donnees.
    """

    table: Table
    conflict_columns: tuple[str, ...]

    def __init__(self, client: SportsClient, session_factory: sessionmaker[Session], **filters: Any) -> None:
        self.client = client
        self.session_factory = session_factory
        self.sport: Sport = client.sport
        self.filters = filters

    @abstractmethod
    def fetch(self) -> dict:
        """Appelle la bonne methode de SportsClient avec self.filters; renvoie l'enveloppe brute."""

    @abstractmethod
    def to_rows(self, payload: dict) -> list[dict]:
        """Mappe les items de payload['response'] vers des dicts de colonnes de `table`."""

    def run(self) -> int:
        rows = self.to_rows(self.fetch())
        if rows:
            self.upsert(rows)
        return len(rows)

    def upsert(self, rows: list[dict]) -> None:
        stmt = pg_insert(self.table).values(rows)
        update_cols = {
            c.name: stmt.excluded[c.name]
            for c in self.table.columns
            if c.name not in self.conflict_columns
        }
        stmt = stmt.on_conflict_do_update(index_elements=list(self.conflict_columns), set_=update_cols)
        with self.session_factory.begin() as session:
            session.execute(stmt)
