"""Fetch Treasury Bond data from ChinaMoney and export it as CSV.

The assignment asks for public data from:
https://www.chinamoney.com.cn/english/bdInfo/

This script calls the same JSON endpoints used by the page, filters by
Bond Type = Treasury Bond and Issue Year = 2023, and writes the required
columns to a valid CSV file.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any
from urllib import parse, request


BASE_URL = "https://www.chinamoney.com.cn"
CONDITION_ENDPOINT = f"{BASE_URL}/ags/ms/cm-u-bond-md/BondBaseInfoSearchConditionEN"
LIST_ENDPOINT = f"{BASE_URL}/ags/ms/cm-u-bond-md/BondMarketInfoListEN"

OUTPUT_COLUMNS = [
    "ISIN",
    "Bond Code",
    "Issuer",
    "Bond Type",
    "Issue Date",
    "Latest Rating",
]

FIELD_MAP = {
    "ISIN": "isin",
    "Bond Code": "bondCode",
    "Issuer": "entyFullName",
    "Bond Type": "bondType",
    "Issue Date": "issueStartDate",
    "Latest Rating": "debtRtng",
}

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/english/bdInfo/",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


class ChinaMoneyClient:
    """Small standard-library HTTP client for ChinaMoney JSON endpoints."""

    def __init__(self, timeout: int = 30, use_env_proxy: bool = False) -> None:
        self.timeout = timeout
        if use_env_proxy:
            self.opener = request.build_opener()
        else:
            # Some local machines have stale proxy variables. Disabling proxies
            # makes the script connect directly and avoids false connection errors.
            self.opener = request.build_opener(request.ProxyHandler({}))

    def post_json(self, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        encoded = parse.urlencode(payload or {}).encode("utf-8")
        req = request.Request(url, data=encoded, headers=COMMON_HEADERS, method="POST")
        with self.opener.open(req, timeout=self.timeout) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        rep_code = str(data.get("head", {}).get("rep_code", ""))
        if rep_code and rep_code != "200":
            message = data.get("head", {}).get("rep_message", "")
            raise RuntimeError(f"ChinaMoney API returned {rep_code}: {message}")
        return data


def get_bond_type_code(client: ChinaMoneyClient, display_name: str) -> str:
    """Return the backend code for a displayed bond type name."""

    data = client.post_json(CONDITION_ENDPOINT)
    bond_types = data.get("data", {}).get("bondType", [])
    for item in bond_types:
        if item.get("bondDisplayType") == display_name:
            return str(item["bondTypeCode"])
    available = ", ".join(
        str(item.get("bondDisplayType", "")) for item in bond_types if item.get("bondDisplayType")
    )
    raise ValueError(f"Bond type {display_name!r} was not found. Available: {available}")


def fetch_bond_page(
    client: ChinaMoneyClient,
    *,
    page_no: int,
    page_size: int,
    bond_type_code: str,
    issue_year: int,
) -> dict[str, Any]:
    """Fetch one result page.

    The page sends page numbers as 1-based values, while the response stores
    pageNo as zero-based. We keep the public 1-based value in this function.
    """

    payload = {
        "pageNo": page_no,
        "pageSize": page_size,
        "isin": "",
        "bondCode": "",
        "issueEnty": "",
        "bondType": bond_type_code,
        "couponType": "",
        "issueYear": issue_year,
        "rtngShrt": "",
        "bondSpclPrjctVrty": "",
    }
    return client.post_json(LIST_ENDPOINT, payload)


def normalize_row(raw: dict[str, Any]) -> dict[str, str]:
    """Keep only the columns required by the assignment."""

    row: dict[str, str] = {}
    for output_name, source_name in FIELD_MAP.items():
        value = raw.get(source_name)
        row[output_name] = "" if value is None else str(value).strip()
    return row


def fetch_all_bonds(
    *,
    bond_type: str = "Treasury Bond",
    issue_year: int = 2023,
    page_size: int = 15,
    sleep_seconds: float = 0.1,
    use_env_proxy: bool = False,
) -> list[dict[str, str]]:
    """Fetch all matching bonds and return normalized rows."""

    client = ChinaMoneyClient(use_env_proxy=use_env_proxy)
    bond_type_code = get_bond_type_code(client, bond_type)

    first_page = fetch_bond_page(
        client,
        page_no=1,
        page_size=page_size,
        bond_type_code=bond_type_code,
        issue_year=issue_year,
    )
    data = first_page.get("data", {})
    page_total = int(data.get("pageTotal", 1))
    rows = [normalize_row(item) for item in data.get("resultList", [])]

    for page_no in range(2, page_total + 1):
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
        page = fetch_bond_page(
            client,
            page_no=page_no,
            page_size=page_size,
            bond_type_code=bond_type_code,
            issue_year=issue_year,
        )
        rows.extend(normalize_row(item) for item in page.get("data", {}).get("resultList", []))

    return rows


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export ChinaMoney bond search data to CSV.")
    parser.add_argument(
        "--output",
        default="output/chinamoney_treasury_bond_2023.csv",
        help="CSV output path.",
    )
    parser.add_argument("--bond-type", default="Treasury Bond", help="Displayed bond type name.")
    parser.add_argument("--issue-year", type=int, default=2023, help="Issue year filter.")
    parser.add_argument("--page-size", type=int, default=15, help="Page size sent to the API.")
    parser.add_argument(
        "--use-env-proxy",
        action="store_true",
        help="Use proxy settings from environment variables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = fetch_all_bonds(
        bond_type=args.bond_type,
        issue_year=args.issue_year,
        page_size=args.page_size,
        use_env_proxy=args.use_env_proxy,
    )
    output_path = Path(args.output)
    write_csv(rows, output_path)
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
