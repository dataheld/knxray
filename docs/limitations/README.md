---
title: What a diff can show
output-file: index.html
---

knxray uses [xknxproject](https://github.com/XKNX/xknxproject)
to read group addresses, devices, and communication objects.
It does not show device parameters such as dim curves,
or all ETS settings.
A clean JSON diff does not establish that the project files are identical.
knxray does not modify the source project files.

## Comparison order

`knxray diff` stops at the first successful equality check:

1. Compare the complete files byte for byte.
   Identical files produce no output.
1. Compare archive entries after excluding `.validation`, `.certificate`,
   and `.signature` files.
   ETS rewrites those files on save.
   XML normalization also removes `LastModified` attributes
   and `ProjectTrace` audit entries.
   Equal normalized archives produce no output.
1. Parse both projects and compare the stable JSON.
   Differences produce a unified diff on stdout.
   Equal JSON after differing normalized XML produces a warning on stderr.

The XML check is not a full semantic comparison.
Whitespace and attribute-order differences can still matter.
The JSON diff cannot explain changes in XML that xknxproject does not parse.

## Git textconv

Git textconv invokes `knxray show` separately for each file.
It cannot run the archive comparison or detect a parser-blind change.
Use `knxray diff` when you need that warning.

GitHub and GitLab web interfaces do not run textconv.
knxray is a local command-line tool, not a web diff application.

## Supported inputs

The CLI has no password option for protected projects and no language option.
Its public interface consists of the `show`, `diff`, and `setup` commands.
The internal Python modules are not a supported library API.
