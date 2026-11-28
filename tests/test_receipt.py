import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "receipt", Path(__file__).parents[1] / "scripts" / "receipt.py"
)
receipt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt)


def test_receipt_row_cost():
    # 1M in at 3 plus 0.5M out at 15 = 3 + 7.5
    row = receipt.receipt_row("t", 1_000_000, 500_000, 3.0, 15.0, date="2026-11-30")
    assert row == ["2026-11-30", "t", 1_000_000, 500_000, "10.5000"]


def test_csv_gets_header_once(tmp_path):
    f = tmp_path / "r.csv"
    for _ in range(2):
        receipt.main(["t", "10", "10", "1", "1", "--csv", str(f)])
    lines = f.read_text().splitlines()
    assert lines[0] == "date,task,input_tokens,output_tokens,cost"
    assert len(lines) == 3


@pytest.mark.parametrize(
    "args",
    [
        ["t", "-5", "10", "1", "1"],
        ["t", "10", "10", "nan", "1"],
        ["t", "10", "10", "1", "inf"],
        ["t", "10", "10", "-1", "1"],
    ],
)
def test_refuses_negative_or_non_finite(args, capsys):
    with pytest.raises(SystemExit) as exit_info:
        receipt.main(args)
    assert exit_info.value.code == 2
    assert "zero or more" in capsys.readouterr().err
