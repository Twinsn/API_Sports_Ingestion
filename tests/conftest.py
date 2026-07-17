import json
from pathlib import Path

import pytest
from api_sports import Sport

FIXTURES_DIR = Path(__file__).parent / "unit" / "fixtures"


class FakeClient:
    """Stand-in pour SportsClient: les ingestors n'utilisent que `.sport` dans
    to_rows(); fetch() n'est jamais appele dans les tests unitaires."""

    def __init__(self, sport: Sport = Sport.FOOTBALL):
        self.sport = sport


@pytest.fixture
def fake_client():
    return FakeClient()


@pytest.fixture
def load_fixture():
    def _load(name: str) -> dict:
        return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))

    return _load
