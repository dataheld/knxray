#!/usr/bin/env python3
"""Inject the git-diff textconv snapshot into README.md."""
import re
import sys
from pathlib import Path

_SNAPSHOTS = Path("tests/__snapshots__/test_knxray.ambr")
_README = Path("README.md")
_SNAPSHOT_NAME = "test_git_diff_textconv_snapshot"
_BEGIN = "<!-- BEGIN git-diff-example -->"
_END = "<!-- END git-diff-example -->"


def _extract_snapshot(name: str) -> str:
    text = _SNAPSHOTS.read_text(encoding="utf-8")
    match = re.search(
        rf"# name: {re.escape(name)}\n  '''(.*?)\n  '''",
        text,
        re.DOTALL,
    )
    if not match:
        sys.exit(f"Snapshot '{name}' not found in {_SNAPSHOTS}")
    raw = match.group(1)
    # syrupy indents every content line with 2 spaces
    return "\n".join(
        line[2:] if line.startswith("  ") else line
        for line in raw.split("\n")
    ).strip("\n")


def main() -> None:
    snapshot = _extract_snapshot(_SNAPSHOT_NAME)
    block = (
        f"{_BEGIN}\n"
        f"```diff\n"
        f"{snapshot}\n"
        f"```\n"
        f"{_END}"
    )
    readme = _README.read_text(encoding="utf-8")
    updated = re.sub(
        rf"{re.escape(_BEGIN)}.*?{re.escape(_END)}",
        lambda _: block,
        readme,
        flags=re.DOTALL,
    )
    _README.write_text(updated, encoding="utf-8")
    print(f"Updated {_README}")


if __name__ == "__main__":
    main()
