import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def _chdir_project_root(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent.parent)
