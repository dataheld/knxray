# knxray Specification

## Design Constraints

### xknxproject Partial Visibility

The xknxproject library — knxray's only runtime dependency — parses a subset of `.knxproj` content:

- Captured: group addresses, devices, communication objects.
- Not captured: device parameters (e.g. dim curves, PWM settings), some ETS metadata.

This is the central constraint shaping the entire design:
a "clean diff" cannot mean "files are identical."

### ETS Metadata Non-Determinism

ETS rewrites certain files on every save regardless of whether the user changed anything:
`.validation`, `.certificate`, `.signature`.
Byte-for-byte comparison of `.knxproj` files is therefore unreliable as a "no change" signal.
Level 2 of the diff cascade excludes these files explicitly.

## Name

The project name is **knxray** — an X-ray pun (sees through opaque files), renamed from knxplain.

## Diff Cascade

The cascade runs levels in order and stops at the first that finds equivalence.
This mirrors the approach for Office documents (`.docx`) via git `textconv`:
a semantic parser extracts meaningful content; surrounding zip metadata is silently ignored.

### Level Rationale

| #                            | Why it exists                                                             |
| ---------------------------- | ------------------------------------------------------------------------- |
| 1 · Byte                     | Fastest exit: identical bytes means nothing to show.                      |
| 2 · XML-byte                 | Catches real changes while ignoring ETS metadata churn.                   |
| 3 · XML-semantic *(planned)* | Catches device parameters and other XML changes invisible to xknxproject. |
| 4 · JSON (xknxproject)       | Human-readable structured diff of what xknxproject can parse.             |

Level 3 is the critical missing piece.
Until it exists, any XML-level difference invisible to xknxproject is surfaced only as a stderr warning at level 4.
Once level 3 exists, that warning becomes redundant.

## Parse Level Registry

`show` dispatches via a `_LEVELS` dict keyed by level name.
Adding a new level requires one new function and one dict entry — no other changes.

`diff()` accepts a `level` parameter as a stub, unused until more levels exist.
No `--level` CLI flag is exposed yet — deferred until there are 2+ levels to choose from.
The registry keeps adding that flag a small, isolated change when the time comes.

## Output Stability

JSON output must be reproducible across ETS saves that make no logical change:

- Keys sorted alphabetically.
- `last_modified` removed from the parsed output — ETS updates this on every save regardless of user intent.
- `default=str` for non-serializable values.

## Git Integration

`knxray` integrates with git via the `textconv` mechanism.

## Development Environment

Never install tools interactively; declare them in `flake.nix` or `pyproject.toml`.

The brand comes from a private flake, so `nix develop`, `nix fmt` and `nix flake check` need FlakeHub access.
`nix run`, `nix profile install` and `uv run pytest` do not.

## Documentation

The site renders `README.md`, so the tested diff example has a single source.
A Mermaid block or a GitHub alert shows as source text there, so `README.md` has neither.

## Accepted Tradeoffs

1. **Partial visibility is permanent** (unless xknxproject upstream gains device parameter support).
   Mitigated with the `_notice` field and level-4 warning.

1. **No web UI diffs.**
   GitHub/GitLab bypass `textconv`; only local `git` commands benefit.
   GHA integration is a long-term goal but not yet planned.

1. **`--level` flag deferred.**
   No flag until 2+ levels exist.
   Registry pattern keeps the addition isolated.

1. **Monolithic JSON output.**
   One combined object, not split by section.
   Simpler architecture; larger but consistent diffs.

1. **Nix-only distribution.**
   knxray is a complete Python package, but is not published to PyPI or conda.

1. **`--format` flag deferred.**
   Output format tied to level for now; separated only when a concrete second format exists.
