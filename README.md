# ie-agent-harness

A small worked example of how to check the work of an AI coding agent in industrial ecology (IE). An agent is
a program that edits your files and runs commands for you. You do not need to write code to follow this repo.
Reading it takes about 6 minutes.

I wrote this as a teaching example. It is MIT licensed and it is not a product of the AI4IE working group.

Why it exists: an agent can change an LCA model and report a number that looks fine and is wrong. The fix here
is the one a lab uses for an instrument: keep a known answer, and do not let the agent change it. The model
is a toy with two processes (electricity and steel) and made-up numbers. The checks around it are the point.
The name says "harness": the instructions, tests and checks that keep an agent within bounds.

What to do next:

- **Never open a terminal?** Take one habit from this repo. Work out one result of your own model by hand,
  such as the footprint of one product, and write it down. Each time an AI tool changes the model, rerun
  that result and compare it with your number. Then read the table in "What each check catches" to see
  what this habit catches and what it misses. It works for any model, in any tool.
- **Some Python?** Run the checks and break the model yourself: see "Try it" and "Break it yourself".
- **Want this in your own project?** Copy `AGENTS.md`, `skills/`, `tests/golden/`, `scripts/`,
  `.pre-commit-config.yaml` and `.github/workflows/ci.yml`. Then replace the toy model and its reference
  answer with your own, worked out by hand.

## The agent as a new lab member

Each file plays a part a lab already knows.

| In the lab | In this repo | File |
| --- | --- | --- |
| Onboarding document: what a new member reads first | a short file of instructions that agents read before they start | `AGENTS.md` |
| Protocol: steps to follow for a task | a checklist (a "skill"): a short instruction file the agent opens when a task matches | `skills/check-lca-change/SKILL.md` |
| Calibration: a known answer the instrument must reproduce | the reference answer (a "golden test"): a test against a number worked out by hand | `tests/golden/` |
| Safety interlock: stops a bad action | a script that refuses an action (a "hook"): git, the version-history tool, runs it before it saves a change | `.pre-commit-config.yaml`, `scripts/guard-golden.sh`, `scripts/check-golden-approval.sh` |
| Lab audit: the same checks, run independently | checks on GitHub (CI, continuous integration): a server runs them on every upload | `.github/workflows/ci.yml` |

The idea comes from ai4ie.org: check AI-assisted work against something the AI could not change. See
[Verify AI-assisted work](https://ai4ie.org/best-practices/verify/) and
[Prompts and skills](https://ai4ie.org/best-practices/prompts-and-skills/#agent-skill-files).

## What the model is

`src/toy_lca/__init__.py` computes `h = C B A^-1 f`, the standard matrix LCA. `A` links products and
processes, `B` lists the emissions of each process (here CO2 and CH4), `C` turns emissions into kg CO2e,
and `f` is the demand. The golden test works out 100 kg of steel by hand: 211.4 kg CO2e.

## What each check catches

The model has three checks, all run by `uv run pytest`. Each has a blind spot.

| Check | What it tests | What it catches | What it misses |
| --- | --- | --- | --- |
| Unit tests (`tests/test_lca.py`) | unit conversion and matrix shapes | a tonne counted as a kilogram; matrices that do not fit together | a wrong number in `A`, `B` or `C` |
| Golden test (`tests/golden/`) | one answer: 100 kg steel is 211.4 kg CO2e | any change that moves that answer, such as a wrong emission, factor or matrix entry | which part is wrong; two errors that cancel at this demand; a unit slip in any unit but kg |
| Mass balance (`mass_imbalance` in `src/toy_lca/__init__.py`) | mass in equals mass out for each process | a wrong emission or waste entry; it names the process and the kg | a wrong factor in `C` or `A`; two mass errors that cancel |

The balance uses made-up masses per unit of output: raw inputs, product, other waste and every emission in
`B`. The golden test tells you the answer is off. The balance tells you which process is off.
None of them proves the model is right. They show it agrees with things worked out apart from the code.

## Try it

You need git and two tools:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) runs Python and installs this project's
  packages. On macOS or Linux, install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`. Its
  install page has the Windows command.
- [prek](https://prek.j178.dev/installation/) installs the scripts that run before each commit (the
  hooks). Once you have uv, install it with `uv tool install prek`. The older `pre-commit` tool works too.

Then, in a terminal:

```sh
git clone https://github.com/simonvanlierde/ie-agent-harness.git
cd ie-agent-harness
uv sync
uv run pytest
uv run ruff check && uv run ruff format --check
prek install
```

`uv run pytest` runs every test, including the three checks above. `ruff` checks the code's style.
`prek install` sets up the hooks; with pre-commit, run `pre-commit install` instead. `just check` runs the
same commands as the `test` job in CI, if you have [`just`](https://just.systems/).

## Break it yourself

Each step plants one error in `src/toy_lca/__init__.py` and runs the checks. After each, undo it with
`git restore src/toy_lca/__init__.py`.

1. Find `UNIT_TO_KG = {"kg": 1.0, "t": 1000.0}` and change `1000.0` to `1.0` (a tonne counted as a
   kilogram). Run `uv run pytest`. Two unit tests fail. The golden test passes, because it only uses kg.
2. Find `C = np.array([[1.0, 28.0]])`, the characterisation factors, and change the CH4 factor `28.0` to
   `2.8`. Only the golden test fails. It says it expected 211.4 kg CO2e. The mass balance passes, because it
   never looks at `C`.
3. Find `B`, the emissions. Its rows are CO2 and CH4, and its columns are electricity and steel, so steel's
   CH4 is the `0.01` in `[0.002, 0.01]`. Change it to `0.1`. The golden test fails, and so do both
   mass-balance tests. The first says `steel -0.090`: steel puts out 0.09 kg more than goes in. The second
   fails too, because it plants the same error on top of yours.
4. Now cheat. Make the change from step 2 again. In `tests/golden/test_golden.py`, set `GOLDEN_KG_CO2E` to
   the wrong output, 178.64. Run `git add src/toy_lca/__init__.py tests/golden/test_golden.py`, then
   `git commit -m "update CH4 factor"`. Ruff and the tests pass, because you changed the expected value to
   match. But the golden hook refuses and tells you to ask a person. A person approves with an
   `Approved-by:` line in the commit message, or by setting `GOLDEN_APPROVED=1` for one commit. Undo with
   `git restore --staged --worktree src/toy_lca/__init__.py tests/golden/test_golden.py`.

`git commit --no-verify` skips the hook, so CI checks again: a pull request that changes `tests/golden/`
fails unless one of its commits has an `Approved-by:` line. Anyone can type that line, so on a shared repo
add a
[branch ruleset](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
for `main` that requires a pull request, a review and the `golden-approval` check. CI runs the pull
request's own copy of this check, so only a required review stops a pull request that edits the check
itself.

The golden hook and the approval check watch `tests/golden/` only. A new `conftest.py` or a change to
`pyproject.toml` can stop the golden test from running at all. So CI also runs `tests/golden` on its own,
with those settings ignored.

## Footprint receipt

`scripts/receipt.py` turns one agent run into one row: date, task, input tokens, output tokens, cost. A token
is the unit of text a model reads or writes, and providers bill by it. You give the token counts and the
prices per million tokens. Your agent tool or your provider's usage page shows the counts. The script has no
prices of its own. It does not price cached tokens either. Agent runs often reuse text from a cache, which
costs less than input. If your run did, take the cost from your provider's own report.

```sh
uv run python scripts/receipt.py "fix unit bug" 12000 3500 3 15 --csv receipts.csv
```

There is no energy or CO2 column. Providers do not publish a measured energy figure per run, and a guess from
the token count would look like data without being data. Add one only when you have a source you can read.

## Use it with any agent

Nothing here is tied to one product. Checks that live in git and CI work for every agent. To stop an agent
earlier, wire the same commands into its own hook system, if it has one:

- **Before an edit:** refuse any path under `tests/golden/`.
- **After an edit:** run `uv run ruff format`.
- **When the agent says it is done:** run `uv run pytest` and hand the failures back.

Keep that wiring in your own settings, not in this repo. Also keep a second copy of the golden value where
the agent cannot reach it, such as a CI job on a protected branch. The `GOLDEN_APPROVED=1` switch is only as
strong as the rule that an agent never sets it.

## Exercise

[docs/exercise.md](docs/exercise.md) is a proposed two-hour exercise for MSc students built on these checks.

## Questions

Open an [issue](https://github.com/simonvanlierde/ie-agent-harness/issues). No question is too basic.

## Licence

MIT. See [LICENSE](LICENSE).
