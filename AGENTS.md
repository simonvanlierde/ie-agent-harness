# AGENTS.md

You are a new member of this lab. This file is your onboarding document. Read it first.

## The project

A toy matrix LCA in `src/toy_lca/`: `h = C B A^-1 f`. All data is made up.

## Lab rules

- **Protocols are skills.** Before you report a number, follow `skills/check-lca-change/SKILL.md`.
- **Calibration is tests.** `uv run pytest` must pass. `tests/golden/` holds a value worked out by hand. It is
  the reference instrument: you do not edit, delete or skip it. If you think it is wrong, stop and tell a person.
- **Interlocks are hooks.** A git hook refuses commits that touch `tests/golden/` without a person's
  approval, and runs ruff and pytest; CI fails a pull request that changes them without an `Approved-by:`
  trailer. Do not bypass either (`--no-verify`, `GOLDEN_APPROVED=1`, a trailer you wrote yourself).
- State the unit of every number you report. Mass is in kg inside the code.
- Run `uv run ruff check` and `uv run ruff format` before you finish.
- Say what you did not check.
