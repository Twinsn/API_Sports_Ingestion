# sport-ingestion

Constructeurs d'injection BDD : récupère les données via la librairie
[`api_sports`](../Sport_API) et les upsert dans PostgreSQL. Repo séparé de la librairie
cliente : celle-ci reste un client HTTP pur, réutilisable indépendamment (middleware, WS,
scripts) ; ce repo est un consommateur parmi d'autres.

Portée v1 : des **ingestors** (constructeurs) par domaine — `LeagueIngestor`,
`TeamIngestor`, `StandingIngestor`, `FixtureIngestor` — pas encore de scheduler, de CLI ni
de migrations Alembic (reporté à plus tard, une fois le schéma stabilisé).

## Installation

```bash
docker compose up -d          # Postgres local (ou pointez DATABASE_URL vers un Postgres existant)
cp .env.example .env          # renseignez API_SPORTS_KEY et DATABASE_URL
uv sync --extra dev
uv run python scripts/init_db.py   # cree les tables (create_all, pas de migration en v1)
```

## Utilisation

```python
from api_sports import Sport, SportsClient
from sport_ingestion.db.session import build_session_factory
from sport_ingestion.ingestors import LeagueIngestor, TeamIngestor, StandingIngestor, FixtureIngestor

session_factory = build_session_factory()
football = SportsClient(Sport.FOOTBALL)

LeagueIngestor(football, session_factory, id=61).run()
TeamIngestor(football, session_factory, league=61, season=2023).run()
StandingIngestor(football, session_factory, league=61, season=2023).run()
FixtureIngestor(football, session_factory, date="2026-07-14").run()
```

Chaque `.run()` fetch via `SportsClient`, mappe la réponse et **upsert** (idempotent, clé
composite incluant `sport`) — rejouable sans créer de doublons.

## Schéma

Chaque table a quelques colonnes indexées/utiles (ids, noms, dates, scores) + une colonne
`raw JSONB` gardant l'objet API verbatim, pour absorber l'évolution des champs imbriqués
sans migration. `sport` est une simple `String` (pas d'enum Postgres) pour ajouter un sport
sans migration ; `season` est une `String` pour absorber la variance entre sports
(`season=2023` en football vs `season="2023-2024"` en basketball).

Clés composites (toutes incluent `sport`, les IDs API n'étant uniques que par sport) :

| Table | Clé |
|---|---|
| `leagues` | `(sport, league_id)` |
| `teams` | `(sport, team_id)` |
| `standings` | `(sport, league_id, season, team_id, group_name)` |
| `fixtures` | `(sport, fixture_id)` |

## Tests

```bash
uv run pytest                    # unitaires (to_rows, sans DB) -- rapide, par defaut
uv run pytest -m integration      # necessite TEST_DATABASE_URL (docker compose up -d)
```

Les tests unitaires vérifient le mapping `to_rows()` avec des extraits JSON figés
(`tests/unit/fixtures/`), y compris la variance de forme entre sports (football imbrique
sous `"fixture"`, basketball est plat — voir `FixtureIngestor`). Les tests d'intégration
exercent le véritable `INSERT ... ON CONFLICT` Postgres (non émulable par SQLite), en
particulier l'idempotence : deux `run()` successifs avec un payload modifié ne doivent
produire qu'une ligne, mise à jour.

## Vérification bout-en-bout (vraie API, plan Free)

```bash
uv run python scripts/verify_football_e2e.py
```

Ingeste Ligue 1 (id=61) + saison 2023 (le plan Free est bridé à 2022-2024) + les matchs du
jour, affiche le nombre de lignes par ingestor et le quota restant, puis fait un check léger
Basketball (chemin saison-string). Relancer le script une 2e fois doit laisser les comptes
inchangés (idempotence sur données réelles).
