# knxplain

Creates diffable, plain-text JSON from *parts* of your `*.knxproj` using the [xknxproject](https://github.com/XKNX/xknxproject) parser.

> [!IMPORTANT]
> `xknxproject` only parses a *subset* of your `*.knxproj`, including group addresses, devices, and communication objects.
> Device parameters (for example, a dim curve) live in opaque per-device XML and are **not** shown.
> A clean diff here does **not** mean the `.knxproj` files are identical.
> To highlight these "false negatives", `knxdiff` emits a warning when the `*.knxproj` files differ, but the parsed JSON does not.

## Commands

| Command | Purpose |
| --- | --- |
| `knxshow <file.knxproj>` | Parse → sorted JSON to stdout. Primary git `textconv` driver. |
| `knxdiff <file1.knxproj> <file2.knxproj>` | JSON diff to stdout; warns to stderr when files differ but the diff is empty. |
| `knxsetup [--global]` | Configure git `textconv` for `*.knxproj` files in the current repo (or globally). |

## Quick start

**One-off inspection** (no install needed):

```bash
nix run github:dataheld/knxplain -- my-installation.knxproj
```

**Permanent git integration:**

```bash
# 1. Install
nix profile install github:dataheld/knxplain

# 2. Configure git (once per repo, or --global for all repos)
knxsetup
```

After `knxsetup`, `git diff`, `git show`, and `git log -p` show human-readable JSON diffs on committed `*.knxproj` files automatically. Under the hood this uses git's [`textconv` driver](https://git-scm.com/docs/gitattributes#_performing_text_diffs_of_binary_files).

> [!NOTE]
> GitHub and GitLab web UIs do not use `textconv`, so `git diff` integration only works locally.

## Nix flake outputs

```text
packages.default  — virtualenv with knxshow, knxdiff, knxsetup on PATH
apps.knxshow      — nix run .#knxshow
apps.knxdiff      — nix run .#knxdiff
apps.default      — alias for knxshow
devShells.default — development shell with editable install + uv
checks.default    — runs pytest in the Nix sandbox
```
