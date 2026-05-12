import difflib
import sys
from pathlib import Path

from knxplain._parse import parse, to_json

_EMPTY_DIFF_WARNING = (
    "WARNING: No differences visible to the xknxproj parser were found, but the .knxproj files are not byte-identical.\n"
    "There may be other differences between the two projects, such as device parameters."
)

def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: knxdiff <file1.knxproj> <file2.knxproj>", file=sys.stderr)
        sys.exit(1)

    path1, path2 = Path(sys.argv[1]), Path(sys.argv[2])
    json1 = to_json(parse(path1))
    json2 = to_json(parse(path2))

    diff = list(
        difflib.unified_diff(
            json1.splitlines(keepends=True),
            json2.splitlines(keepends=True),
            fromfile=str(path1),
            tofile=str(path2),
        )
    )

    if diff:
        sys.stdout.writelines(diff)
    elif path1.read_bytes() != path2.read_bytes():
        print(_EMPTY_DIFF_WARNING, file=sys.stderr)
