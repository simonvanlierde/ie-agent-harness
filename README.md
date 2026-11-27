# ie-agent-harness

A small starter for an agentic harness in industrial ecology (IE): the files that keep an AI coding agent
honest. It has a toy matrix LCA, a hand-checked golden test, one skill, a commit hook and CI. Reading it takes
about 10 minutes. You do not need to write code to follow it.

## The agent as a new lab member

| In the lab | In this repo | File |
| --- | --- | --- |
| Onboarding document | what the agent reads first | `AGENTS.md` |
| Protocols | steps it follows on demand | `skills/check-lca-change/SKILL.md` |
| Calibration | a known answer the code must reproduce | `tests/golden/`, `tests/` |
| Safety interlock | a check that stops a bad action | `.pre-commit-config.yaml`, `scripts/guard-golden.sh`, `scripts/check-golden-approval.sh` |
| Lab audit | the same checks on every push | `.github/workflows/ci.yml` |

The idea is the one on ai4ie.org: check AI-assisted work against something the AI could not change. See
[Verify AI-assisted work](https://ai4ie.org/best-practices/verify/) and
[Prompts and skills](https://ai4ie.org/best-practices/prompts-and-skills/#agent-skill-files).

## What is in the toy model

`src/toy_lca/__init__.py` computes `h = C B A^-1 f` for two processes (electricity, steel) and two emissions
(CO2, CH4). The numbers are made up. The golden test works out 100 kg of steel by hand: 211.4 kg CO2e.

## Two checks, two blind spots

| Check | What it pins | What it catches | What it cannot catch |
| --- | --- | --- | --- |
| Golden test (`tests/golden/`) | one number: 100 kg steel is 211.4 kg CO2e | any change that moves that number, such as a wrong emission, factor or matrix entry | which part is wrong; an error that cancels out at this one demand; a unit error in another unit (it only uses kg) |
| Mass balance (`mass_imbalance` in `src/toy_lca/__init__.py`) | mass in equals mass out for each process | an emission or waste entry that breaks a process's mass, and it names the process and the kg | a wrong characterisation factor (`C`), a wrong technosphere coefficient (`A`), or two mass errors that cancel |

The balance uses made-up masses per unit of output: raw inputs, product, other waste, plus every emission in
`B`. The golden test tells you the answer is off. The balance tells you which process is off.
Neither one proves the model is right. They show it is consistent with two things worked out apart from the code.

## Footprint receipt

`scripts/receipt.py` turns one agent run into one row: date, task, input tokens, output tokens, cost.
You give the token counts and the prices per million tokens; nothing is hardcoded.

```sh
uv run python scripts/receipt.py "fix unit bug" 12000 3500 3 15 --csv receipts.csv
```

There is no energy or CO2 column. Providers do not publish a measured energy figure per run, and an
estimate from tokens would be a guess dressed as a number. Add one only when you have a source you can read.

## Exercise

[docs/exercise.md](docs/exercise.md) is a proposed two-hour exercise for MSc students built on these checks.

## Quickstart

```sh
uv sync
uv run pytest
uv run ruff check && uv run ruff format --check
uv run prek install      # or: pre-commit install; installs the commit hooks
```

You need [uv](https://docs.astral.sh/uv/) and [prek](https://github.com/j178/prek) (or pre-commit).

## Break it yourself

1. In `src/toy_lca/__init__.py`, change `UNIT_TO_KG` so `"t"` is `1.0` (a tonne counted as a kilogram),
   or change the CH4 factor in `C` from `28.0` to `2.8`.
2. Run `uv run pytest`. A unit test or the golden test fails. The golden message says what it expected
   (211.4 kg CO2e) and what it got. Note the kg and t flip only shows in the tonne tests, so the factor
   change is the one the golden test catches.
3. Now try the cheat: keep the wrong CH4 factor, set `GOLDEN_KG_CO2E` in `tests/golden/test_golden.py` to the
   wrong output (178.64), `git add` both files and run `git commit`. Ruff and pytest pass, but the golden
   hook refuses: a person has to approve changes to the golden tests (`Approved-by:` trailer or
   `GOLDEN_APPROVED=1`). `git commit --no-verify` skips the hook, so CI checks again: a pull request
   that changes `tests/golden/` fails unless one of its commits has an `Approved-by:` trailer. The
   trailer is a claim anyone can type, so on a shared repo add a
   [branch ruleset](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
   for `main` that requires a pull request, a review and the `golden-approval` check. CI runs the pull
   request's own copy of this check, so only a required review stops a pull request that edits the
   check itself.
4. Undo your edits (`git restore --staged . && git restore .`).

Second round, the mass balance: in `B` change the steel CH4 emission from `0.01` to `0.1`, then run
`uv run pytest`. The golden test fails, and so does the balance test, which says process 1 (steel) is out
by 0.09 kg. Now change `C` from `28.0` to `2.8` instead: only the golden test fails. The balance still passes,
because it never looks at `C`. Undo your edits again.

## Use it with any agent

Nothing here is tied to one product. Checks that live in git and CI work for every agent. To make an agent
stop earlier, wire the same commands into its own hook system, if it has one:

- **Before an edit:** deny any path under `tests/golden/`.
- **After an edit:** run `uv run ruff format`.
- **When the agent says it is done:** run `uv run pytest` and hand the failures back.

Keep that wiring in your own settings, not in this repo. Put a second copy of the golden value somewhere the
agent cannot reach, such as a CI job from a protected branch.

## Licence

MIT. See [LICENSE](LICENSE).
