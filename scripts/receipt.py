"""Print one receipt row for an agent run: tokens and cost.

    uv run python scripts/receipt.py "fix unit bug" 12000 3500 3 15 [--csv f.csv]

Arguments: task label, input tokens, output tokens, price per million input
tokens, price per million output tokens (same currency). No energy or CO2
estimate: this repo has no measured source for it.
"""

import argparse
import csv
import datetime
import sys

HEADER = ["date", "task", "input_tokens", "output_tokens", "cost"]


def receipt_row(task, tokens_in, tokens_out, price_in, price_out, date=None):
    cost = (tokens_in * price_in + tokens_out * price_out) / 1_000_000
    date = date or datetime.date.today().isoformat()
    return [date, task, tokens_in, tokens_out, f"{cost:.4f}"]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("task")
    p.add_argument("input_tokens", type=int)
    p.add_argument("output_tokens", type=int)
    p.add_argument("price_in", type=float, help="price per million input tokens")
    p.add_argument("price_out", type=float, help="price per million output tokens")
    p.add_argument("--csv", help="append the row to this file instead of printing")
    a = p.parse_args(argv)
    row = receipt_row(a.task, a.input_tokens, a.output_tokens, a.price_in, a.price_out)
    if a.csv:
        with open(a.csv, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if fh.tell() == 0:
                w.writerow(HEADER)
            w.writerow(row)
    else:
        csv.writer(sys.stdout).writerow(row)


if __name__ == "__main__":
    main()
