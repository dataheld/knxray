---
title: Use knxray
output-file: index.html
---

## Installation

Run a command without installing knxray:

```sh
nix run github:dataheld/knxray -- show my-installation.knxproj
```

Or install the command:

```sh
nix profile install github:dataheld/knxray
```

The source repository also builds an ordinary Python package.
With Python 3.10 or later and uv available, install from a checkout:

```sh
uv tool install .
```

Git must be on your `PATH` for `knxray setup` and git integration.
knxray is not published on PyPI.

## Inspect a project

```sh
knxray show my-installation.knxproj
```

This prints sorted JSON with group addresses, devices,
and communication objects.
The output includes a notice about the parser's partial visibility.
The parser uses English (`en-US`) and removes the `last_modified` field
to avoid changes caused only by saving the project again in ETS.

## Compare two projects

```sh
knxray diff before.knxproj after.knxproj
```

The command prints a unified JSON diff to stdout.
When the normalized project XML differs but the parsed JSON does not,
it prints a warning to stderr instead.
See [Limitations](../limitations/README.md) for what the parser cannot show.

Successful comparisons exit with status zero, including when a difference
or warning is reported.
The command is not an exit-status replacement for `git diff --exit-code`.
Argument and input errors exit with a nonzero status.

## Configure git

Run this in each repository containing `.knxproj` files:

```sh
knxray setup
```

This configures `diff.knxray.textconv` as `knxray show`,
enables git's textconv cache, and appends
`*.knxproj diff=knxray` to `.gitattributes`.
An existing attributes file is preserved.
Repeated setup does not add duplicate entries.
Commit `.gitattributes` if other contributors should use the same attribute.
Each contributor still needs the command and git configuration.

To configure the driver in your global git configuration:

```sh
knxray setup --global
```

This does not create or change an attributes file.
Add `*.knxproj diff=knxray` to each repository's `.gitattributes`,
or to your configured global attributes file.

After configuration, `git diff`, `git show`, and `git log -p`
show readable JSON for `.knxproj` files through git's
[textconv mechanism](https://git-scm.com/docs/gitattributes#_performing_text_diffs_of_binary_files).
This runs `knxray show`, not the `knxray diff` comparison cascade.
It therefore does not emit the parser-blind comparison warning.

GitHub and GitLab web interfaces do not run textconv drivers.
