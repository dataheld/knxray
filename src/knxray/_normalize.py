import xml.etree.ElementTree as ET
from collections.abc import Callable

# Normalization strips content we know to be non-deterministic ETS noise.
# Be conservative: only strip what is fully understood and demonstrably
# irrelevant to project content. When in doubt, leave it in and let the diff
# surface it.

_Normalizer = Callable[[ET.Element], None]


def _strip_last_modified_timestamps(root: ET.Element) -> None:
    # ETS updates LastModified on DeviceInstance and ProjectInformation on every save.
    for elem in root.iter():
        elem.attrib.pop("LastModified", None)


def _strip_project_tracing_audit_entries(root: ET.Element) -> None:
    # ETS Project Tracing app appends a new ProjectTrace child on every save.
    for elem in root.iter():
        for child in [c for c in elem if c.tag.split("}")[-1] == "ProjectTrace"]:
            elem.remove(child)


# List, not a set: current normalizers commute (non-overlapping targets), but
# future ones may depend on earlier steps having run first.
_NORMALIZERS: list[_Normalizer] = [
    _strip_last_modified_timestamps,
    _strip_project_tracing_audit_entries,
]


def normalize(content: bytes) -> str:
    root = ET.fromstring(content)
    for step in _NORMALIZERS:
        step(root)
    return ET.tostring(root, encoding="unicode")


def is_ignorable_filetype(filename: str) -> bool:
    # ETS rewrites these on every save regardless of project changes.
    return filename.endswith((".validation", ".certificate", ".signature"))
