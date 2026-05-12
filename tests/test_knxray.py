import json
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

_FIXTURES = Path("tests/fixtures")
_DEMO = _FIXTURES / "demo.knxproj"
_DEMO_GA_ADDED = _FIXTURES / "demo-ga-added.knxproj"
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


def test_smoke():
    json.loads(_show(_DEMO))


def test_notice_field():
    data = json.loads(_show(_DEMO))
    assert "_notice" in data and data["_notice"]


def test_detectable_diff():
    stdout, _ = _diff(_DEMO, _DEMO_GA_ADDED)
    assert stdout.strip()


def test_invisible_diff():
    stdout, stderr = _diff(_DEMO, _DEMO_DEVICE_PARAM)
    assert not stdout.strip()
    assert "WARNING" in stderr


def test_diff_snapshot(snapshot):
    stdout, _ = _diff(_DEMO, _DEMO_GA_ADDED)
    assert stdout == snapshot
