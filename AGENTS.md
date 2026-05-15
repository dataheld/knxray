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
