from pathlib import Path

from knxray._parse import parse, to_json


def show(path: Path) -> None:
    print(to_json(parse(path)))
