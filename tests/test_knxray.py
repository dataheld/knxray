import json
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

# Fixture provenance
# ------------------
# All files were created from the official KNX demo project
# (https://support.knx.org/hc/en-us/articles/9571360929810) by opening and
# saving once in ETS 6.4.1 to normalise the file format.
#
# demo.knxproj            — baseline; opened/saved in ETS once, no changes
# demo2.knxproj           — same procedure as demo.knxproj; must be byte-
#                           identical after parsing (no spurious diff)
# demo-ga-removed.knxproj — one group address removed; must produce a short,
#                           human-readable diff vs demo.knxproj
# demo-device-param.knxproj — one device parameter changed; xknxproject does
#                           not capture device parameters so no diff is visible,
#                           but the files are not byte-identical

_FIXTURES = Path("tests/fixtures")
_DEMO = _FIXTURES / "demo.knxproj"
_DEMO2 = _FIXTURES / "demo2.knxproj"
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


def test_smoke():
    json.loads(_show(_DEMO))


def test_notice_field():
    data = json.loads(_show(_DEMO))
    assert "_notice" in data and data["_notice"]


def test_no_spurious_diff():
    # Two independently opened/saved copies of the same project must look
    # identical to the parser — guards against ETS write-order non-determinism.
    stdout, _ = _diff(_DEMO, _DEMO2)
    assert not stdout.strip()


def test_detectable_diff():
    stdout, _ = _diff(_DEMO, _DEMO_GA_REMOVED)
    assert stdout.strip()


def test_invisible_diff():
    # Device-parameter changes are not captured by xknxproject; expect no diff
    # output but a warning so the user knows the clean diff may be misleading.
    stdout, stderr = _diff(_DEMO, _DEMO_DEVICE_PARAM)
    assert not stdout.strip()
    assert "WARNING" in stderr


def test_diff_snapshot(snapshot):
    stdout, _ = _diff(_DEMO, _DEMO_GA_REMOVED)
    assert stdout == snapshot
