import csv
import unittest
from pathlib import Path

from bond_fetcher import OUTPUT_COLUMNS, normalize_row, write_csv


class BondFetcherTest(unittest.TestCase):
    def test_normalize_row_keeps_required_columns(self) -> None:
        raw = {
            "isin": "CND10007C4N2",
            "bondCode": "239983",
            "entyFullName": "Ministry of Finance",
            "bondType": "Treasury Bond",
            "issueStartDate": "2023-12-22",
            "debtRtng": "---",
            "unused": "ignored",
        }

        self.assertEqual(
            normalize_row(raw),
            {
                "ISIN": "CND10007C4N2",
                "Bond Code": "239983",
                "Issuer": "Ministry of Finance",
                "Bond Type": "Treasury Bond",
                "Issue Date": "2023-12-22",
                "Latest Rating": "---",
            },
        )

    def test_write_csv_header(self) -> None:
        output = Path("output/test_bonds.csv")
        write_csv([], output)
        with output.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            self.assertEqual(next(reader), OUTPUT_COLUMNS)


if __name__ == "__main__":
    unittest.main()
