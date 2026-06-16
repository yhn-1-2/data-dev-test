# Data Development Written Test / 数据开发笔试题

This repository contains the solution for the two programming tasks in
`开发工程师测试题-2026(1).docx`.

本项目使用 Python 标准库完成，不依赖第三方包。

## Task 1: ChinaMoney Bond CSV

The page `https://www.chinamoney.com.cn/english/bdInfo/` loads bond data through
JSON endpoints. The script follows the same flow as the web page:

1. Call `BondBaseInfoSearchConditionEN` to get search options.
2. Find the backend code for `Treasury Bond`, which is `100001`.
3. Call `BondMarketInfoListEN` with `bondType=100001` and `issueYear=2023`.
4. Read all result pages and export only the required columns:
   `ISIN`, `Bond Code`, `Issuer`, `Bond Type`, `Issue Date`, `Latest Rating`.

Run:

```bash
python bond_fetcher.py --output output/chinamoney_treasury_bond_2023.csv
```

The CSV is written with `utf-8-sig` encoding so it can be opened directly in
Excel while remaining a standard CSV file.

Current generated result:

- File: `output/chinamoney_treasury_bond_2023.csv`
- Rows: 111
- Validation: all rows have `Bond Type = Treasury Bond`; all `Issue Date`
  values are in 2023.

## Task 2: `reg_search`

`regex_utils.py` implements:

```python
reg_search(text: str, regex_list: list[dict[str, str]]) -> list[dict]
```

Each dictionary in `regex_list` maps an output field name to a regular
expression. The helper supports normal capturing groups and named groups:

- `(?P<value>...)` returns one value.
- `(?P<start>...)` and `(?P<end>...)` return a two-item list.
- Chinese dates like `2023 年 6 月 2 日` are normalized to `2023-06-02`.

Run the example:

```bash
python regex_utils.py
```

Expected output:

```python
[{'标的证券': '600900.SH', '换股期限': ['2023-06-02', '2027-06-01']}]
```

## Tests

No third-party packages are required.

```bash
python -m unittest discover -s tests
```

## Files

- `bond_fetcher.py`: ChinaMoney crawler and CSV exporter.
- `regex_utils.py`: custom regex matching function.
- `tests/`: unit tests for CSV formatting and regex extraction.
- `output/chinamoney_treasury_bond_2023.csv`: generated result CSV after running the crawler.
- `SUBMISSION.md`: Chinese submission notes and email template.
