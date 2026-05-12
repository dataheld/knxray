import json
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

# Fixture provenance
# ------------------
# All files derive from the official KNX demo project
# (https://support.knx.org/hc/en-us/articles/9571360929810), opened and saved
# once in ETS 6.4.1 to normalise the format.
#
# Fixtures are designed to exercise each level of the diff cascade
# (see README "How diffing works"):
#
#   demo.knxproj              — baseline
#   demo-copy.knxproj         — byte-for-byte copy of demo → level 1 exit
#   demo-resaved.knxproj      — independently saved in ETS without changes; ETS
#                               rewrites .validation/.certificate so bytes differ,
#                               but XML is identical → level 2 exit
#   demo-ga-removed.knxproj   — one group address removed; XML and JSON differ
#                               → level 4: visible JSON diff
#   demo-device-param.knxproj — one device parameter changed; XML differs but
#                               xknxproject does not parse device parameters
#                               → level 4: XML differs, parser is blind, warn

_FIXTURES = Path("tests/fixtures")
_DEMO = _FIXTURES / "demo.knxproj"
_DEMO_COPY = _FIXTURES / "demo-copy.knxproj"
_DEMO_RESAVED = _FIXTURES / "demo-resaved.knxproj"
_DEMO_GA_REMOVED = _FIXTURES / "demo-ga-removed.knxproj"
_DEMO_DEVICE_PARAM = _FIXTURES / "demo-device-param.knxproj"


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
    json.loads(_show(_DEMO))


def test_show_notice_field():
    data = json.loads(_show(_DEMO))
    assert "_notice" in data and data["_notice"]


# --- level 1: byte comparison ---

def test_diff_level1_byte_identical():
    from knxray._diff import _bytes_identical
    assert _bytes_identical(_DEMO, _DEMO_COPY)


def test_diff_level1_bytes_differ():
    from knxray._diff import _bytes_identical
    assert not _bytes_identical(_DEMO, _DEMO_RESAVED)


# --- level 2: XML comparison (excl. ETS metadata) ---

def test_diff_level2_xml_identical():
    from knxray._diff import _xml_identical
    assert _xml_identical(_DEMO, _DEMO_RESAVED)


def test_diff_level2_xml_differs():
    from knxray._diff import _xml_identical
    assert not _xml_identical(_DEMO, _DEMO_GA_REMOVED)


# --- level 4: xknxproject JSON diff ---

def test_diff_level4_json_diff_found():
    from knxray._diff import _json_diff
    assert _json_diff(_DEMO, _DEMO_GA_REMOVED)


def test_diff_level4_json_diff_empty():
    from knxray._diff import _json_diff
    assert not _json_diff(_DEMO, _DEMO_DEVICE_PARAM)


# --- integration: full diff() cascade ---

def test_diff_cascade_exits_silently():
    # Byte-identical → cascade exits at level 1, no output of any kind.
    stdout, stderr = _diff(_DEMO, _DEMO_COPY)
    assert not stdout.strip() and not stderr.strip()


def test_diff_cascade_outputs_json_diff():
    # GA removed → XML and JSON differ → stdout diff at level 4.
    stdout, _ = _diff(_DEMO, _DEMO_GA_REMOVED)
    assert stdout.strip()


def test_diff_cascade_warns_when_parser_blind():
    # Device param changed → XML differs, JSON identical → stderr warning at level 4.
    stdout, stderr = _diff(_DEMO, _DEMO_DEVICE_PARAM)
    assert not stdout.strip() and stderr.strip()


def test_diff_cascade_json_diff_snapshot(snapshot):
    stdout, _ = _diff(_DEMO, _DEMO_GA_REMOVED)
    assert stdout == snapshot
