from importlib.metadata import distribution


def test_distribution_metadata() -> None:
    package = distribution("knxray")
    metadata = package.metadata
    assert metadata["Name"] == "knxray"
    assert metadata["Version"] == "0.1.0"
    assert metadata["Requires-Python"] == ">=3.10"
    assert metadata["Summary"] == "Readable JSON diffs for KNX ETS project files"
    assert metadata["License-Expression"] == "MIT"
    assert metadata.get_all("License-File") == ["LICENSE"]
    assert metadata["Description-Content-Type"] == "text/markdown"
    assert "# knxray" in metadata.get_payload()
    assert "Repository, https://github.com/dataheld/knxray" in metadata.get_all(
        "Project-URL", []
    )
    assert any(
        entry.name == "knxray" and entry.value == "knxray._cli:main"
        for entry in package.entry_points
        if entry.group == "console_scripts"
    )
