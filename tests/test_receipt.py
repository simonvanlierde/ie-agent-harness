import importlib.util
from pathlib import Path

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
