import json
import subprocess
from pathlib import Path

import pytest

_FIXTURES = Path(__file__).parent / "fixtures"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["knxray", *args], capture_output=True, text=True)


@pytest.mark.parametrize(
    ("args", "status", "stdout", "stderr"),
    [
        ([], 1, True, False),
        (["--help"], 0, True, False),
        (["unknown"], 2, False, True),
        (["show"], 2, False, True),
        (["show", "missing.knxproj"], 1, False, True),
    ],
)
def test_cli_errors(
    args: list[str], status: int, stdout: bool, stderr: bool
) -> None:
    result = _run(*args)
    assert result.returncode == status
    assert bool(result.stdout) == stdout
    assert bool(result.stderr) == stderr


def test_cli_show() -> None:
    result = _run("show", str(_FIXTURES / "example.knxproj"))
    assert result.returncode == 0
    assert not result.stderr
    data = json.loads(result.stdout)
    assert data["_notice"]
    assert "last_modified" not in data["info"]
    assert result.stdout == json.dumps(data, indent=2, sort_keys=True) + "\n"


@pytest.mark.parametrize(
    ("filename", "stdout", "stderr"),
    [
        ("example-copy.knxproj", False, False),
        ("example-resaved.knxproj", False, False),
        ("example-ga-removed.knxproj", True, False),
        ("example-device-param-changed.knxproj", False, True),
    ],
)
def test_cli_diff(filename: str, stdout: bool, stderr: bool) -> None:
    result = _run(
        "diff",
        str(_FIXTURES / "example.knxproj"),
        str(_FIXTURES / filename),
    )
    assert result.returncode == 0
    assert bool(result.stdout) == stdout
    assert bool(result.stderr) == stderr


@pytest.fixture
def git_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "0")
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.parametrize("global_flag", [False, True])
def test_cli_setup(git_repo: Path, global_flag: bool) -> None:
    args = ["setup", "--global"] if global_flag else ["setup"]
    scope = "--global" if global_flag else "--local"
    attributes = git_repo / ".gitattributes"
    if not global_flag:
        attributes.write_text("*.txt text\n")

    result = _run(*args)
    assert result.returncode == 0
    assert result.stdout
    assert not result.stderr
    for key, expected in [
        ("diff.knxray.textconv", "knxray show"),
        ("diff.knxray.cachetextconv", "true"),
    ]:
        value = subprocess.check_output(
            ["git", "config", scope, key], text=True
        ).strip()
        assert value == expected

    repeated = _run(*args)
    assert repeated.returncode == 0
    assert not repeated.stderr
    if global_flag:
        assert not attributes.exists()
    else:
        assert attributes.read_text() == "*.txt text\n*.knxproj diff=knxray\n"
        assert not repeated.stdout
