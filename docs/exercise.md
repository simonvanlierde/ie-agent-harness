# Exercise: do not trust the first answer

A proposal for about 2 hours, for MSc students. No course uses it yet. You need this repo, `uv`, and access
to an AI assistant of your choice. No coding skill is needed beyond running the commands.

## What you do

1. **Get a result (20 min).** Give the assistant the toy model (`src/toy_lca/__init__.py`) and ask for the
   footprint of 100 kg of steel, in kg CO2e. Write down its answer and how it got there.
2. **Check mass in = mass out (20 min).** Run `uv run pytest tests/test_lca.py -k mass`. For one process,
   add up the masses in and out by hand from `src/toy_lca/__init__.py` (`MASS_IN`, `PRODUCT_KG`, `WASTE_KG` and the emissions in `B`). The sum should match: the test passes when in minus out is zero.
3. **Run the golden test (15 min).** The golden test compares the code with one number worked out by hand. Run `uv run pytest tests/golden`. Read the hand calculation at the
   top of `tests/golden/test_golden.py`. Does the assistant's answer from step 1 match 211.4?
4. **Find a planted bug (35 min).** Your instructor gives you a copy of `src/toy_lca/__init__.py` with one
   change, for example a tonne counted as a kilogram, or a swapped factor. Run `uv run pytest`. Find the
   change. Say which check failed first, and which checks stayed green.
5. **Write down what the checks cannot catch (20 min).** For each check (golden test, mass balance, unit
   tests), name one error it would miss, and say how you would find it.

Do not edit `tests/golden/`: the golden test is your reference. If you think it is wrong, say so in your hand-in.

## Hand-in

- The result from step 1 and the prompt that produced it.
- The output of both checks (steps 2 and 3).
- The bug from step 4: what changed, which check caught it, which did not.
- Half a page on what you would still not trust, and what you would do about it.

## Why these checks

The golden test pins one number worked out by hand. The mass balance checks that each process conserves
mass. A kg-versus-t flip is caught by the unit tests. A swapped characterisation factor is caught only by
the golden test. A wrong emission entry is caught by both, and the balance names the process. Nothing here
catches a wrong factor that is also in your hand calculation.

## For the instructor

Planted bugs that work with this repo, each a one-line edit in `src/toy_lca/__init__.py`:

| Edit | Caught by |
| --- | --- |
| `"t": 1000.0` to `1.0` | unit tests only |
| `C` CH4 `28.0` to `2.8` | golden test only |
| `B` steel CH4 `0.01` to `0.1` | golden test and mass balance |
