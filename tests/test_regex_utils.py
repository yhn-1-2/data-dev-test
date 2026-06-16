import unittest

from regex_utils import reg_search


class RegSearchTest(unittest.TestCase):
    def test_assignment_example(self) -> None:
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

        self.assertEqual(
            reg_search(text, regex_list),
            [{"标的证券": "600900.SH", "换股期限": ["2023-06-02", "2027-06-01"]}],
        )


if __name__ == "__main__":
    unittest.main()
