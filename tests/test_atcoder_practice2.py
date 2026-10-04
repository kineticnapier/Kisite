from pathlib import Path
import unittest

import kisite


EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "atcoder"


class AtCoderPractice2Tests(unittest.TestCase):
    def test_practice2_a_sample(self):
        source = (EXAMPLES / "practice2_a.kis").read_text(encoding="utf-8")
        input_data = """\
4 7
1 0 1
0 0 1
0 2 3
1 0 1
1 1 2
0 0 2
1 1 3
"""
        self.assertEqual(kisite.run(source, input_data), ["0", "1", "0", "1"])

    def test_practice2_b_sample(self):
        source = (EXAMPLES / "practice2_b.kis").read_text(encoding="utf-8")
        input_data = """\
5 5
1 2 3 4 5
1 0 5
1 2 4
0 3 10
1 0 5
1 0 3
"""
        self.assertEqual(kisite.run(source, input_data), ["15", "7", "25", "6"])


if __name__ == "__main__":
    unittest.main()
