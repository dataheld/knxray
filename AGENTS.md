## Spec-Driven Workflow

For any non-trivial task:

1. Create or update `PLAN.md` with architecture, responsibilities, acceptance criteria, and step-by-step plan.
2. Commit it first.
3. Implement strictly against the committed `PLAN.md`.
4. After implementation, update the plan with any deviations + rationale.

### PIV Loop

For any task longer than ~5 tool calls or 30 minutes:

**After every 3–5 major steps (or before any automatic compaction)**: Run explicit validation.

Output a concise validation report, then update PLAN.md with a new “Validation [YYYY-MM-DD]” section summarizing status, decisions, and next steps.
Do not proceed with more changes until this is committed.

- Read the committed `PLAN.md`.
- Compare current implementation (code + tests + behavior).
  For each section in the spec:
  - What was planned?
  - What exists now?
  - Any deviations or missing pieces?
  - Are acceptance criteria met?
- Update PLAN.md with: status per section, deviations + rationale, remaining work, acceptance criteria met/missed.

Only continue after validation passes (or human review of the diff).

## Formatting

Unless the chosen or typical formatter for a file extension says otherwise, format code and text according to these rules:

- Always linebreak text after a period or a colon.
- Avoid more then one empty consecutive line.
