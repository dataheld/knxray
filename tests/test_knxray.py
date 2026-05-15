import json
import shutil
import subprocess
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Fixture provenance
# ------------------
# A simple kitchen lighting project: one MDT switch actuator (1.1.1) and two
# ABB push-button sensors (1.1.2, 1.1.3), with two group addresses:
# "Direct Lighting" (0/0/1) and "Indirect Lighting" (0/0/2).
#
# Fixtures are designed to exercise each level of the diff cascade
# (see README "How diffing works"):
#
#   example.knxproj                  — baseline
#   example-copy.knxproj             — byte-for-byte copy of example → level 1 exit
#   example-resaved.knxproj          — independently saved in ETS without changes; ETS
#                                      rewrites .validation/.certificate so bytes differ,
#                                      but XML is identical → level 2 exit
#   example-ga-changed.knxproj       — one group address changed; XML and JSON differ
#                                      → level 4: visible JSON diff
#   example-device-param-changed.knxproj — one device parameter changed; XML differs but
#                                      xknxproject does not parse device parameters
#                                      → level 4: XML differs, parser is blind, warn

_FIXTURES = Path("tests/fixtures")
_EXAMPLE = _FIXTURES / "example.knxproj"
_EXAMPLE_COPY = _FIXTURES / "example-copy.knxproj"
_EXAMPLE_RESAVED = _FIXTURES / "example-resaved.knxproj"
_EXAMPLE_GA_CHANGED = _FIXTURES / "example-ga-removed.knxproj"
_EXAMPLE_DEVICE_PARAM = _FIXTURES / "example-device-param-changed.knxproj"


def _show(path):
    from knxray._show import show
    buf = StringIO()
    with redirect_stdout(buf):
        show(path)
    return buf.getvalue()


def _diff(path1, path2):
    from knxray._diff import diff
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), patch("sys.stderr", err):
        diff(path1, path2)
    return out.getvalue(), err.getvalue()


# --- show ---

def test_show_valid_json():
    json.loads(_show(_EXAMPLE))


def test_show_notice_field():
    data = json.loads(_show(_EXAMPLE))
    assert "_notice" in data and data["_notice"]


# --- level 1: byte comparison ---

def test_diff_level1_byte_identical():
    from knxray._diff import _bytes_identical
    assert _bytes_identical(_EXAMPLE, _EXAMPLE_COPY)


def test_diff_level1_bytes_differ():
    from knxray._diff import _bytes_identical
    assert not _bytes_identical(_EXAMPLE, _EXAMPLE_RESAVED)


# --- level 2: XML comparison (excl. ETS metadata) ---

def test_diff_level2_xml_identical():
    from knxray._diff import _xml_identical
    assert _xml_identical(_EXAMPLE, _EXAMPLE_RESAVED)


def test_diff_level2_xml_differs():
    from knxray._diff import _xml_identical
    assert not _xml_identical(_EXAMPLE, _EXAMPLE_GA_CHANGED)


# --- level 4: xknxproject JSON diff ---

def test_diff_level4_json_diff_found():
    from knxray._diff import _json_diff
    assert _json_diff(_EXAMPLE, _EXAMPLE_GA_CHANGED)


def test_diff_level4_json_diff_empty():
    from knxray._diff import _json_diff
    assert not _json_diff(_EXAMPLE, _EXAMPLE_DEVICE_PARAM)


# --- integration: full diff() cascade ---

def test_diff_cascade_exits_silently():
    # Byte-identical → cascade exits at level 1, no output of any kind.
    stdout, stderr = _diff(_EXAMPLE, _EXAMPLE_COPY)
    assert not stdout.strip() and not stderr.strip()


def test_diff_cascade_outputs_json_diff():
    # GA changed → XML and JSON differ → stdout diff at level 4.
    stdout, _ = _diff(_EXAMPLE, _EXAMPLE_GA_CHANGED)
    assert stdout.strip()


def test_diff_cascade_warns_when_parser_blind():
    # Device param changed → XML differs, JSON identical → stderr warning at level 4.
    stdout, stderr = _diff(_EXAMPLE, _EXAMPLE_DEVICE_PARAM)
    assert not stdout.strip() and stderr.strip()


def test_diff_cascade_json_diff_snapshot(snapshot):
    stdout, _ = _diff(_EXAMPLE, _EXAMPLE_GA_CHANGED)
    assert stdout == snapshot


# --- git textconv integration ---

@pytest.fixture
def git_repo_with_knxproj(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "diff.knxray.textconv", "knxray show"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitattributes").write_text("*.knxproj diff=knxray\n")
    shutil.copyfile(_EXAMPLE, tmp_path / "my-installation.knxproj")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial project"], cwd=tmp_path, check=True, capture_output=True)
    shutil.copyfile(_EXAMPLE_GA_CHANGED, tmp_path / "my-installation.knxproj")
    yield tmp_path


def _git_diff(repo):
    return subprocess.run(
        ["git", "diff", "HEAD", "--", "my-installation.knxproj"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_git_diff_textconv_snapshot(snapshot, git_repo_with_knxproj):
    assert _git_diff(git_repo_with_knxproj) == snapshot


def test_readme_shows_current_git_diff(git_repo_with_knxproj):
    readme = Path("README.md").read_text(encoding="utf-8")
    assert _git_diff(git_repo_with_knxproj) in readme
