"""Custom regular-expression search helper for the second assignment."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any


CHINESE_DATE_PATTERN = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")


def normalize_date(value: str) -> str:
    """Convert Chinese dates like '2023 年 6 月 2 日' to '2023-06-02'."""

    def repl(match: re.Match[str]) -> str:
        year, month, day = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

    return CHINESE_DATE_PATTERN.sub(repl, value).strip()


def _patterns(pattern_config: str | Iterable[str]) -> list[str]:
    if isinstance(pattern_config, str):
        return [pattern_config]
    return list(pattern_config)


def _extract_match(match: re.Match[str]) -> Any:
    groupdict = match.groupdict()
    if "value" in groupdict:
        return normalize_date(groupdict["value"])
    if "start" in groupdict and "end" in groupdict:
        return [normalize_date(groupdict["start"]), normalize_date(groupdict["end"])]
    if groupdict:
        return {key: normalize_date(value) for key, value in groupdict.items()}

    groups = match.groups()
    if len(groups) == 1:
        return normalize_date(groups[0])
    if len(groups) > 1:
        return [normalize_date(value) for value in groups]
    return normalize_date(match.group(0))


def reg_search(text: str, regex_list: list[dict[str, str | Iterable[str]]]) -> list[dict[str, Any]]:
    """Search text with a list of field-to-regex mappings.

    Args:
        text: Text to search.
        regex_list: A list of dictionaries. Each dictionary describes one
            extraction rule set, where keys are output field names and values
            are regex strings, or several alternative regex strings.

    Returns:
        A list of matched dictionaries. A rule set is included only when at
        least one field in it is matched.
    """

    results: list[dict[str, Any]] = []
    for rule_set in regex_list:
        item: dict[str, Any] = {}
        for field_name, pattern_config in rule_set.items():
            for pattern in _patterns(pattern_config):
                match = re.search(pattern, text, flags=re.S)
                if match:
                    item[field_name] = _extract_match(match)
                    break
        if item:
            results.append(item)
    return results


def demo() -> None:
    text = """
    标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
    有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
    券。
    换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
    之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
    日至 2027 年 6 月 1 日止。
    """
    regex_list = [
        {
            "标的证券": r"股票代码[:：]\s*(?P<value>\d{6}\.[A-Z]{2})",
            "换股期限": (
                r"即\s*(?P<start>\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)"
                r"\s*至\s*(?P<end>\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)"
            ),
        }
    ]
    print(reg_search(text, regex_list))


if __name__ == "__main__":
    demo()
