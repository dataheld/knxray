# knxray: Parse-Level Architecture

## Context

`knxray show` and `knxray diff` both implicitly operate at a single extraction depth
(xknxproject's JSON parse, which we call "level 4" in the diff cascade).
This is not declared anywhere in the API, making the commands harder to understand and extend.

The goal of this plan is to make the extraction depth explicit in the code,
and design the API to be open for future levels without committing prematurely to a CLI flag.

## Two-Dimensional Design

Every `show` and `diff` operation has two independent concerns:

1. **Parse level** (`--level`): what data is extracted from the `.knxproj` zip.
2. **Translation** (`--format`, future): how the extracted data is formatted for output.

These are orthogonal.
Today we only have one value for each dimension, so neither flag is exposed in the CLI yet.

### Parse levels (dimension 1)

| Level name | What it extracts | Status |
| --- | --- | --- |
| `json` | xknxproject structured parse: group addresses, devices, comm. objects | implemented |
| `xml` | Raw listing of XML files inside the zip | planned |
| `xml-semantic` | Parsed XML element tree (human-readable, catches device params) | planned |

`json` is the default and the current git `textconv` driver.

### Translation (dimension 2)

| Format name | Output | Status |
| --- | --- | --- |
| *(implicit)* | Pretty-printed JSON (for `--level json`) | implemented |
| `yaml` | YAML representation of the same structured parse | possible future |
| `csv` | CSV of group addresses only | possible future |

Translation is deferred entirely.
No `--format` flag will be added until there is a concrete second format to justify it.

## Diff cascade relationship

The diff cascade (levels 1-4 in the README) and the `--level` flag are related but distinct:

- The **cascade** is an automatic multi-level comparison strategy used by `knxray diff`.
  It starts at the cheapest check (bytes) and stops as soon as the files are equivalent.
- The **`--level` flag** selects which extraction to use for the output (show or diff).
  Currently that is always `json`; in future a user could request `--level xml` to see raw XML diffs.

The flag and the cascade level differ in that the flag let's you choose a *lower* level, than what the cascade would have arrived at.
For example, whenever the cascade proceeds to `json`, a user can always choose (something like ) `knxray diff --level xml` (not implemented yet).
This isn't a terribly likely use case, because lower levels tend to be less human-readable and therefore less useful for diffing, but it's still conceptually possible.

## What we implement now

### 1. Registry pattern in `_show.py`

Replace the single `show()` body with a `_LEVELS` dict mapping level name to implementation function.

```python
_LEVELS = {
    "json": _show_json,
    # "xml": _show_xml,   # future
}

DEFAULT_LEVEL = "json"

def show(path: Path, level: str = DEFAULT_LEVEL) -> None:
    if level not in _LEVELS:
        raise ValueError(f"Unknown level '{level}'; choices: {list(_LEVELS)}")
    _LEVELS[level](path)

def _show_json(path: Path) -> None:
    print(to_json(parse(path)))
```

### 2. `level` parameter on `diff()` (stub)

Add `level: str = "json"` parameter to `diff()` for symmetry and future use,
but do not wire it into the cascade logic yet (cascade always uses all implemented levels).

### 3. Updated CLI help text

Change `show` help from `"Parse -> sorted JSON to stdout"` to
`"Parse -> JSON (xknxproject) to stdout"`.
No `--level` flag added yet.

### 4. README update

Add `--level LEVEL` to the "planned" section of "How diffing works",
alongside the planned level 3.

## Acceptance criteria

- [x] `knxray show demo.knxproj` output unchanged.
- [x] `knxray diff` output unchanged.
- [x] `show(path, level="unknown")` raises `ValueError` with the supported choices listed.
- [x] All 12 tests pass.
- [x] Adding a new level in future requires only: one new `_show_<level>` function + one dict entry.

## Validation 2026-05-12

All acceptance criteria met.
Implementation matches the plan exactly:

- `_show.py`: registry dict `_LEVELS`, `DEFAULT_LEVEL = "json"`, `show()` dispatches via dict.
- `_diff.py`: `diff()` accepts `level` parameter (unused stub), cascade logic unchanged.
- `_cli.py`: help text updated to "JSON (xknxproject)"; no `--level` flag added.
- `README.md`: planned `--level` flag and level 3 noted in "How diffing works".
- `PLAN.md`: committed before implementation per AGENTS.md spec-driven workflow.

No deviations from the plan.

## Future plans

### Near-term: level 3 XML semantic (`--level xml-semantic`)

Implement a human-readable XML-element diff that catches device parameters.
This is the missing step between level 2 (byte-compare XML files) and level 4 (JSON parse).
When this is done:

- Add `--level` to the CLI (values: `json`, `xml-semantic`; default: `json`).
- The level-4 "parser is blind" warning becomes redundant and can be removed,
  because the XML-semantic diff will already have surfaced those differences.
- Update `setup` to document a second textconv entry for XML-level git diffs.

### Medium-term: `--level xml` (raw zip listing)

Useful for inspecting what files are inside a `.knxproj` without a full parse.
Output: sorted list of filenames + sizes, or raw XML dump.

### Long-term: `--format` (translation)

When there is a concrete second output format (e.g. CSV of group addresses for import
into a spreadsheet), add `--format` as a second flag.
Until then, the format is implicit in the level.

### git textconv multi-entry pattern

Once a second level exists, users can configure separate textconv entries per level,
mirroring how pandoc is used for `.docx` files:

```gitconfig
[diff "knxray"]           textconv = knxray show                  # json (default)
[diff "knxray-xml"]       textconv = knxray show --level xml       # future
```

`knxray setup` will be updated to configure the default entry only.
Users who want additional levels configure them manually.
