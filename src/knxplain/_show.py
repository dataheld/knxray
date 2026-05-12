import sys
from pathlib import Path

from knxplain._parse import parse, to_json


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: knxshow <file.knxproj>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    print(to_json(parse(path)))
