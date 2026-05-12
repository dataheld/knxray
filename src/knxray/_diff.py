import difflib
import sys
from pathlib import Path

from knxray._parse import parse, to_json

_EMPTY_DIFF_WARNING = (
    "WARNING: No differences visible to the xknxproj parser were found, but the .knxproj files are not byte-identical.\n"
    "There may be other differences between the two projects, such as device parameters."
)


def diff(path1: Path, path2: Path) -> None:
    json1 = to_json(parse(path1))
    json2 = to_json(parse(path2))

    lines = list(
        difflib.unified_diff(
            json1.splitlines(keepends=True),
            json2.splitlines(keepends=True),
            fromfile=str(path1),
            tofile=str(path2),
        )
    )

    if lines:
        sys.stdout.writelines(lines)
    elif path1.read_bytes() != path2.read_bytes():
        print(_EMPTY_DIFF_WARNING, file=sys.stderr)
