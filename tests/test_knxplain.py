import json
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

_FIXTURES = Path(__file__).parent / "fixtures"
_DEMO = _FIXTURES / "demo.knxproj"
_DEMO_GA_ADDED = _FIXTURES / "demo-ga-added.knxproj"
_DEMO_DEVICE_PARAM = _FIXTURES / "demo-device-param.knxproj"


def _knxshow(path):
    from knxplain._show import main
    buf = StringIO()
    with patch("sys.argv", ["knxshow", str(path)]), redirect_stdout(buf):
        main()
    return buf.getvalue()


def _knxdiff(path1, path2):
    from knxplain._diff import main
    out, err = StringIO(), StringIO()
    with patch("sys.argv", ["knxdiff", str(path1), str(path2)]):
        with redirect_stdout(out), patch("sys.stderr", err):
            main()
    return out.getvalue(), err.getvalue()


def test_smoke():
    json.loads(_knxshow(_DEMO))


def test_notice_field():
    data = json.loads(_knxshow(_DEMO))
    assert "_notice" in data and data["_notice"]


def test_detectable_diff():
    stdout, _ = _knxdiff(_DEMO, _DEMO_GA_ADDED)
    assert stdout.strip()


def test_invisible_diff():
    stdout, stderr = _knxdiff(_DEMO, _DEMO_DEVICE_PARAM)
    assert not stdout.strip()
    assert "WARNING" in stderr
