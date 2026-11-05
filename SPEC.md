# knxray Specification

## Design Constraints

### xknxproject Partial Visibility

The xknxproject library, knxray's only direct runtime dependency,
parses a subset of `.knxproj` content:

- Captured: group addresses, devices, communication objects.
- Not captured: device parameters (e.g. dim curves, PWM settings), some ETS metadata.

This is the central constraint shaping the entire design:
a "clean diff" cannot mean "files are identical."

### ETS Metadata Non-Determinism

ETS rewrites certain files on every save,
regardless of whether the user changed anything:
`.validation`, `.certificate`, `.signature`.
Byte-for-byte comparison of `.knxproj` files is therefore unreliable
as a "no change" signal.
Level 2 of the diff cascade excludes these files explicitly.
It also removes `LastModified` XML attributes and `ProjectTrace` audit entries
before comparing serialized XML.
This normalization is not a full XML-semantic comparison.

## Name

The distribution, Python package, and executable are named `knxray`.
Python 3.10 and later are supported.
There is no supported public Python library API.

## Diff Cascade

The cascade runs levels in order and stops at the first that finds equivalence.
This mirrors the approach for Office documents (`.docx`) via git `textconv`:
a semantic parser extracts meaningful content;
surrounding zip metadata is silently ignored.

### Level Rationale

| #                            | Why it exists                                                             |
| ---------------------------- | ------------------------------------------------------------------------- |
| 1 · Byte                     | Fastest exit: identical bytes means nothing to show.                      |
| 2 · XML-byte                 | Catches real changes while ignoring ETS metadata churn.                   |
| 3 · XML-semantic *(planned)* | Catches device parameters and other XML changes invisible to xknxproject. |
| 4 · JSON (xknxproject)       | Human-readable structured diff of what xknxproject can parse.             |

Level 3 is the critical missing piece.
Until it exists, any XML-level difference invisible to xknxproject
is surfaced only as a stderr warning at level 4.
Once level 3 exists, that warning becomes redundant.

## Parse Level Registry

`show` dispatches via a `_LEVELS` dict keyed by level name.
Adding a new level requires one new function and one dict entry.

`diff()` accepts a `level` parameter as a stub, unused until more levels exist.
No `--level` CLI flag is exposed yet:
it is deferred until there are 2+ levels to choose from.
The registry keeps adding that flag a small, isolated change when the time comes.

## Output Stability

JSON output must be reproducible across ETS saves that make no logical change:

- Keys sorted alphabetically.
- `last_modified` removed from the parsed output:
  ETS updates this on every save regardless of user intent.
- `default=str` for non-serializable values.

## Git Integration

`knxray` integrates with git via the `textconv` mechanism.

## Development Environment

- Always enter the Nix dev shell with `nix develop .` before working.
- nullkomma supplies the Python build, checks, development shell, and editors.
- Runtime dependencies are locked in `uv.lock`.
  Development dependencies belong in its `dev` group.
  Update the lock with `nk python-lock`, without upgrading unrelated packages.
- The runtime package is non-editable and excludes development dependencies.
  The development shell imports the working tree.
  Sandboxed tests use the installed package and Git supplied as a test tool.
- Ruff and ty configuration is Nix-owned.
  Ruff uses stable rules and import sorting, with Python 3.10 syntax.
  Editors use the same pinned ty server and treefmt formatter as local checks.
- Coverage measures `knxray` and reports terminal, XML, and HTML results,
  without a minimum coverage gate or upload.
- Keep the Linux and macOS outputs for both x86-64 and AArch64,
  including the existing `checks.pytest` alias.
- After a non-trivial change, run the shared local checks and sandboxed checks.

## Documentation and Publishing

The Quarto site at <https://knxray.maxheld.de> uses the maxheld brand
and knxray logo.
It documents the CLI, installation, and parser limits,
without introducing a library API or an API-reference generator.
The homepage includes the README, preserving its tested diff example.

GitHub Actions reuses nullkomma's CI and FlakeHub publishing.
The repository-owned Cloudflare job depends on successful CI
and deploys only on non-fork pushes to `main`.
Cloudflare state identifiers and credentials come from repository variables
and secrets, not from source.
Local validation does not deploy or publish.

## Accepted Tradeoffs

1. **Partial visibility is permanent**
   (unless xknxproject upstream gains device parameter support).
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

1. **One Python package for both distribution paths.**
   Hatchling builds ordinary wheels and source distributions.
   Nix uses the same package and locked runtime dependencies.
   PyPI publication is not configured.
   `setup` requires git on the caller's `PATH`.

1. **`--format` flag deferred.**
   Output format is tied to level for now;
   it is separated only when a concrete second format exists.
