from pathlib import Path

from knxray._parse import parse, to_json

_LEVELS = {
    "json": lambda path: print(to_json(parse(path))),
    # "xml":          _show_xml,          # future: list XML files in the zip
    # "xml-semantic": _show_xml_semantic, # future: parsed XML element tree
}

DEFAULT_LEVEL = "json"


def show(path: Path, level: str = DEFAULT_LEVEL) -> None:
    if level not in _LEVELS:
        raise ValueError(f"Unknown level '{level}'; choices: {list(_LEVELS)}")
    _LEVELS[level](path)
