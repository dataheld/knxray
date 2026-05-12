import json
from pathlib import Path

from xknxproject import XKNXProj

_NOTICE = (
    "Partial view — device parameters and some ETS settings are NOT shown. "
    "A clean diff here does not mean the .knxproj files are identical."
)


def parse(path: Path) -> dict:
    project = XKNXProj(path=str(path), language="en-US").parse()
    # last_modified changes on every ETS save regardless of user intent — omit to keep diffs clean
    project.get("info", {}).pop("last_modified", None)
    return {"_notice": _NOTICE, **project}


def to_json(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)
