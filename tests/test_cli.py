import json
import subprocess
from pathlib import Path

import pytest

_FIXTURES = Path(__file__).parent / "fixtures"
_DRIVER = {"diff.knxray.textconv": "knxray show", "diff.knxray.cachetextconv": "true"}


def _knxray(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["knxray", *args], capture_output=True, text=True)


def _driver_config(scope: str) -> dict[str, str]:
    return {
        key: subprocess.check_output(["git", "config", scope, key], text=True).strip()
        for key in _DRIVER
    }


def test_no_command_prints_help_and_fails() -> None:
    result = _knxray()
    assert result.returncode == 1
    assert "usage: knxray" in result.stdout


def test_show_output_is_stable() -> None:
    result = _knxray("show", str(_FIXTURES / "example.knxproj"))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "last_modified" not in data["info"]
    assert result.stdout == json.dumps(data, indent=2, sort_keys=True) + "\n"


def test_diff_reports_changes_with_status_zero() -> None:
    result = _knxray(
        "diff",
        str(_FIXTURES / "example.knxproj"),
        str(_FIXTURES / "example-ga-removed.knxproj"),
    )
    assert result.returncode == 0
    assert result.stdout


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_setup_appends_the_attribute_once(git_repo: Path) -> None:
    attributes = git_repo / ".gitattributes"
    attributes.write_text("*.txt text\n")
    for _ in range(2):
        assert _knxray("setup").returncode == 0
    assert attributes.read_text() == "*.txt text\n*.knxproj diff=knxray\n"
    assert _driver_config("--local") == _DRIVER


def test_setup_global_leaves_the_repository_alone(git_repo: Path) -> None:
    assert _knxray("setup", "--global").returncode == 0
    assert not (git_repo / ".gitattributes").exists()
    assert _driver_config("--global") == _DRIVER
