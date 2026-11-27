---
name: check-lca-change
description: Use after changing code, matrices or factors in this repo's LCA calculation. Re-derives one result by hand and checks units and shapes before you report a number.
---

# Check an LCA change

## When to apply

After any edit to `src/toy_lca/`, or to a matrix, factor or unit in it, and before
you quote a result.

## Steps

1. Run `uv run pytest`. If a test fails, report the failure text. Do not edit the
   test to make it pass, and never touch `tests/golden/`.
2. Name the unit of every quantity the change touches (kg, t, kWh, kg CO2e).
   Look for kg and t flips.
3. Check that the matrix shapes still chain: A is square, B has one column per
   process, C has one column per emission, f has one entry per product.
4. Re-derive one result by hand from the matrices and compare it with the code's
   output. Show the arithmetic.
5. Check mass in equals mass out: `mass_imbalance(B, MASS_IN, PRODUCT_KG, WASTE_KG)` is zero for every
   process. It catches a broken emission or waste entry, not a wrong factor in `C` or `A`.
6. Report what you checked and what you did not.

## Output

A short list: tests run, units checked, hand calculation, mass balance, open doubts.
