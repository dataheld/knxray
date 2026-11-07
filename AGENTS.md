## Spec-Driven Workflow

### Meta-Files

There are number of *meta*-files which provide important context for this project.
They have different roles:

- `README.md`:
  Geared towards the *user* of the project.
  What problem does this project adress, why would they care, and how can they benefit.
  For bigger projects, this *cannot* be a full manual, though should include brief installation instructions, early in the document.
- `SPEC.md`:
  Geared towards the *implementers* of the project, including AI agents.
  What constraints were faced during the design, what choices where made and why, what's important to remember for the future.
  Things like architecture, responsibilities, acceptance criteria.

These files must not duplicate the implementation (code).
They are also not concerned with the *how* but with the *what* and *why*.

Update these files when major decisions have been made or when important information on constraints, etc. has surfaced.

### PIV Loop

For any task longer than ~5 tool calls or 30 minutes:

**After every 3–5 major steps (or before any automatic compaction):** run explicit validation against the above "meta-files".

Output a concise validation report, and update the above meta-files as necessary.
Do not proceed with more changes until this is committed.

- Read the committed meta-documents.
- Compare current implementation (code + tests + behavior).
  For each section in the spec:
  - What was planned?
  - What exists now?
  - Any deviations or missing pieces?
  - Are acceptance criteria met?
- Include in the validation report: status per section, deviations + rationale, remaining work, acceptance criteria met/missed.

Only continue after validation passes (or human review of the diff).

## Future Plans

Future plans belong in the issue tracker (GitHub issues for the repo), not in any of the meta-files or anywhere else inside the repo for that matter.

Possible and rare exception: if some implementation code can't be understood without reference to an intended, but future additional feature.
In that case, a short comment in the code is in order.

## Formatting

### Text

If something is some kind of an enumeration of similar parts, always use a list.

Unless the chosen or typical formatter for a file extension says otherwise:

- Always linebreak text after a period or a colon.
- Avoid more than one empty consecutive line.

#### Markdown

- Do not add empty lines between items in a list.

## Style & Paradigm

### APIs

#### CLI

CLI should follow the unix philosophy:
each tool (or command) should do one thing, and do it well.
Commands should be easily composible and well-behaved (exit conditions, etc.).

If appropriate use a `PROJECTNAME OBJECT VERB MODIFIERS` structure for the CLI.

<!-- nullkomma:agents:start -->
## nullkomma

This project's development environment comes from [nullkomma](https://github.com/dataheld/nullkomma).
Run commands inside its dev shell:
`direnv exec . <command>`, or `nix develop --command <command>` without direnv.
`nk` lists the project's workflows;
`nk <name> [args]` runs one.
Agents can also use them as MCP tools, from `.mcp.json`.
Both run in the working tree;
under `process-compose up`, tasks that rerun on changes may run in a copy,
named in their logs.

Check your work locally, from fastest to strictest:

1. While you work, run the narrowest task that covers the change.
1. Before you report a change as done, run `nk all`, then `nk flake-check`,
   and fix what fails.
   `nk all` formats, builds and runs every check in the working tree.
   `nk flake-check` runs all checks sandboxed, as CI does,
   and sees only files that Git tracks: `git add` new files first.

Skills for nullkomma itself are in `.agents/skills/nk-*`;
if they are missing, run `nk generate-files`.
<!-- nullkomma:agents:end -->
