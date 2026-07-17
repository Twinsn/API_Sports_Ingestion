# sport-ingestion

Constructeurs d'injection BDD : récupère les données via la librairie
[`api_sports`](../Sport_API) et les upsert dans PostgreSQL. Repo séparé de la librairie
cliente : celle-ci reste un client HTTP pur, réutilisable indépendamment (middleware, WS,
scripts) ; ce repo est un consommateur parmi d'autres.

18 **ingestors** (constructeurs), un par domaine du catalogue API-Sports (référentiel,
classements, matchs, détail de match, cotes, prédictions, blessures, transferts...) — pas
encore de scheduler, de CLI ni de migrations Alembic (reporté à plus tard, une fois le
schéma stabilisé).

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
composite incluant `provider` + `sport`) — rejouable sans créer de doublons.

## Schéma

Chaque table a quelques colonnes indexées/utiles (ids, noms, dates, scores) + une colonne
`raw JSONB` gardant l'objet API verbatim, pour absorber l'évolution des champs imbriqués
sans migration. `sport` est une simple `String` (pas d'enum Postgres) pour ajouter un sport
sans migration ; `season` est une `String` pour absorber la variance entre sports
(`season=2023` en football vs `season="2023-2024"` en basketball).

Clés composites (toutes incluent `provider` **et** `sport` — les IDs numériques ne sont
uniques ni entre sports ni entre fournisseurs de données) :

| Table | Clé |
|---|---|
| `leagues` | `(provider, sport, league_id)` |
| `teams` | `(provider, sport, team_id)` |
| `standings` | `(provider, sport, league_id, season, team_id, group_name)` |
| `fixtures` | `(provider, sport, fixture_id)` |
| ... les 14 autres domaines suivent le même principe | |

### Multi-fournisseur : `provider` et `team_identity_map`

`provider` (par défaut `"api_sports"`, passé au constructeur de chaque ingestor) identifie
la **source** des données — à ne pas confondre avec le `provider` de `SportsClient`
(`"apisports"` vs `"rapidapi"`, un détail de transport interne à la lib API-Sports). Il
existe pour permettre de brancher une 2e source (TheSportsDB, ESPN...) sans collision : deux
fournisseurs peuvent très bien attribuer le même id numérique à deux entités différentes.

Le fait que `provider` évite les collisions ne résout pas la déduplication *sémantique* :
si deux sources décrivent la même équipe réelle avec des ids différents, ce sont deux lignes
distinctes dans `teams`. C'est le rôle de `team_identity_map` (+ `TeamResolver` dans
`identity.py`) : une table de correspondance qui attribue à chaque équipe réelle un
`master_team_id` stable, partagé entre toutes les sources qui la décrivent.

- `TeamIngestor.upsert()` appelle `TeamResolver.resolve(session, provider, sport, team_id)`
  avant l'upsert : il crée un nouveau `master_team_id` si cette source ne l'a jamais vue,
  ou renvoie l'existant sinon. Chaque ligne de `teams` porte donc son `master_team_id`.
- `TeamResolver.link(session, provider, sport, team_id, master_team_id)` rattache
  explicitement une équipe d'une nouvelle source à un `master_team_id` déjà connu — c'est le
  point d'entrée pour brancher un 2e fournisseur : une fois qu'on a identifié (manuellement
  ou via un script de rapprochement, hors scope d'ici) que `thesportsdb` team `42` est la
  même équipe réelle que `api_sports` team `33`, un seul appel à `link()` les unifie.

Le rapprochement automatique (fuzzy-matching par nom/pays/stade) n'est volontairement pas
construit : sans 2e source réelle à tester dessus, ce serait de la logique spéculative et
invérifiable. Le mécanisme (table + resolver) est prêt ; l'algorithme de rapprochement
viendra le jour où une 2e source existe réellement.

## Tests

```bash
uv run pytest                    # unitaires (to_rows, sans DB) -- rapide, par defaut
uv run pytest -m integration      # necessite TEST_DATABASE_URL (docker compose up -d)
```

⚠️ `TEST_DATABASE_URL` doit pointer sur une base **differente** de `DATABASE_URL` (ex.
`sport_ingestion_test` vs `sport_ingestion`) : la fixture d'integration fait un
`TRUNCATE`-like sur toutes les tables apres chaque test. Pointer les deux sur la meme base
efface les vraies donnees ingerees (arrive en pratique en écrivant ceci — voir
`.env.example`, `CREATE DATABASE sport_ingestion_test;` une fois avant de lancer les tests).

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
