from pathlib import Path
import unittest

import kisite


EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "atcoder" / "language_test_202505"


class LanguageTest202505Tests(unittest.TestCase):
    def run_both(self, name: str, input_data: str):
        source = (EXAMPLES / f"{name}.kis").read_text(encoding="utf-8")
        reference = kisite.run(source, input_data)
        compiled = kisite.run_compiled(source, input_data)
        self.assertEqual(compiled, reference)
        return reference

    def assert_both(self, name: str, input_data: str, expected: list[str]):
        self.assertEqual(self.run_both(name, input_data), expected)

    def test_practice_a(self):
        self.assert_both("practice_a", "1\n2 3\ntest\n", ["6 test"])

    def test_abc086_a(self):
        self.assert_both("abc086_a", "3 4\n", ["Even"])

    def test_abc081_a(self):
        self.assert_both("abc081_a", "101\n", ["2"])

    def test_abc081_b(self):
        self.assert_both("abc081_b", "3\n8 12 40\n", ["2"])

    def test_abc087_b(self):
        self.assert_both("abc087_b", "2\n2\n2\n100\n", ["2"])

    def test_abc083_b(self):
        self.assert_both("abc083_b", "20 2 5\n", ["84"])

    def test_abc088_b(self):
        self.assert_both("abc088_b", "2\n3 1\n", ["2"])

    def test_abc085_b(self):
        self.assert_both("abc085_b", "4\n10\n8\n8\n6\n", ["3"])

    def test_abc085_c(self):
        self.assert_both("abc085_c", "9 45000\n", ["4 0 5"])

    def test_abc049_c(self):
        self.assert_both("abc049_c", "erasedream\n", ["YES"])

    def test_abc086_c(self):
        self.assert_both("abc086_c", "2\n3 1 2\n6 1 1\n", ["Yes"])

    def test_abc259_b(self):
        output = self.run_both("abc259_b", "2 2 180\n")
        x, y = map(float, output[0].split())
        self.assertAlmostEqual(x, -2.0, places=9)
        self.assertAlmostEqual(y, -2.0, places=9)

    def test_abc169_b(self):
        self.assert_both("abc169_b", "2\n1000000000 1000000000\n", ["1000000000000000000"])

    def test_abc358_d(self):
        self.assert_both("abc358_d", "4 2\n3 4 5 4\n1 4\n", ["7"])

    def test_dp_g(self):
        self.assert_both("dp_g", "4 5\n1 2\n1 3\n3 2\n2 4\n3 4\n", ["3"])

    def test_dp_j(self):
        output = self.run_both("dp_j", "3\n1 1 1\n")
        self.assertAlmostEqual(float(output[0]), 5.5, places=9)

    def test_dp_l(self):
        self.assert_both("dp_l", "4\n10 80 90 30\n", ["10"])

    def test_abc325_d(self):
        self.assert_both("abc325_d", "3\n1 1\n1 1\n2 1\n", ["3"])

    def test_abc328_e(self):
        self.assert_both("abc328_e", "3 3 10\n1 2 1\n2 3 2\n1 3 9\n", ["0"])

    def test_memorytest_b_sample(self):
        self.assert_both("memorytest_b", "5 2 1 3\n3\n2\n0\n4\n", ["4", "29", "13"])

    def test_abc370_d(self):
        self.assert_both("abc370_d", "2 4 3\n1 2\n1 2\n1 3\n", ["2"])

    def test_abc385_d(self):
        input_data = """\
3 3 0 0
0 2
2 2
2 0
U 2
R 2
D 2
"""
        self.assert_both("abc385_d", input_data, ["2 0 3"])

    def test_abc411_f(self):
        input_data = """\
7 7
1 2
1 3
2 3
1 4
1 5
2 5
6 7
5
1 2 3 1 5
"""
        self.assert_both("abc411_f", input_data, ["4", "3", "3", "3", "2"])

    def test_abc421_e(self):
        output = self.run_both("abc421_e", "1 2 3 4 5 6\n")
        self.assertAlmostEqual(float(output[0]), 14.6588633742, places=8)


if __name__ == "__main__":
    unittest.main()
