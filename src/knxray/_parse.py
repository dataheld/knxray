import json
from pathlib import Path

from xknxproject import XKNXProj

_NOTICE = (
    "Partial view — device parameters and some ETS settings are NOT shown. "
    "A clean diff here does not mean the .knxproj files are identical."
)


def parse(path: Path) -> dict:
    project = XKNXProj(path=str(path), language="en-US").parse()
    normalized: dict[str, object] = {"_notice": _NOTICE, **project}
    # Ignore ETS save timestamps for stable diffs.
    if "info" in project:
        normalized["info"] = {
            key: value
            for key, value in project["info"].items()
            if key != "last_modified"
        }
    return normalized


def to_json(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True, default=str)
