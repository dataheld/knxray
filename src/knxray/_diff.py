import difflib
import sys
import zipfile
from pathlib import Path

from knxray._parse import parse, to_json

# ETS rewrites these files on every save regardless of project changes.
_ETS_METADATA = {".validation", ".certificate", ".signature"}

_WARN_BLIND = (
    "The project XML differs but xknxproject cannot surface the change.\n"
    "There may be differences such as device parameters that are not shown above."
)


def _bytes_identical(path1: Path, path2: Path) -> bool:
    """Level 1: full byte comparison (fastest exit)."""
    return path1.read_bytes() == path2.read_bytes()


def _xml_identical(path1: Path, path2: Path) -> bool:
    """Level 2: compare only .xml entries, ignoring non-deterministic ETS metadata."""
    with zipfile.ZipFile(path1) as z1, zipfile.ZipFile(path2) as z2:
        names1 = {n for n in z1.namelist() if n.endswith(".xml")}
        names2 = {n for n in z2.namelist() if n.endswith(".xml")}
        if names1 != names2:
            return False
        return all(z1.read(n) == z2.read(n) for n in names1)


# Level 3: XML-semantic diff — planned. Would produce a human-readable summary
# of XML-element-level changes (catching device parameters, etc.) and make the
# level-4 warning below unnecessary.


def _json_diff(path1: Path, path2: Path) -> list[str]:
    """Level 4: xknxproject-parsed JSON diff."""
    json1 = to_json(parse(path1))
    json2 = to_json(parse(path2))
    return list(
        difflib.unified_diff(
            json1.splitlines(keepends=True),
            json2.splitlines(keepends=True),
            fromfile=str(path1),
            tofile=str(path2),
        )
    )


def diff(path1: Path, path2: Path) -> None:
    if _bytes_identical(path1, path2):      # level 1
        return
    if _xml_identical(path1, path2):        # level 2
        return
    # level 3 (planned): XML-semantic diff would go here
    lines = _json_diff(path1, path2)        # level 4
    if lines:
        sys.stdout.writelines(lines)
    else:
        print(_WARN_BLIND, file=sys.stderr)
