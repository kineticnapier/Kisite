from pathlib import Path
import unittest

import kisite


EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "atcoder"


class AtCoderPractice2Tests(unittest.TestCase):
    def assert_backends_equal(self, source: str, input_data: str, expected: list[str]):
        reference = kisite.run(source, input_data)
        compiled = kisite.run_compiled(source, input_data)
        self.assertEqual(reference, expected)
        self.assertEqual(compiled, expected)
        self.assertEqual(compiled, reference)

    def assert_practice2_d_output(self, output: list[str]):
        source_grid = ["#..", "..#", "..."]
        self.assertEqual(output[0], "3")
        self.assertEqual(len(output), 4)
        grid = output[1:]
        self.assertTrue(all(len(row) == 3 for row in grid))

        tiles = 0
        for i in range(3):
            for j in range(3):
                original = source_grid[i][j]
                value = grid[i][j]
                if original == "#":
                    self.assertEqual(value, "#")
                    continue
                self.assertIn(value, ".<>^v")
                if value == ">":
                    self.assertLess(j + 1, 3)
                    self.assertEqual(grid[i][j + 1], "<")
                    tiles += 1
                elif value == "<":
                    self.assertGreaterEqual(j - 1, 0)
                    self.assertEqual(grid[i][j - 1], ">")
                elif value == "v":
                    self.assertLess(i + 1, 3)
                    self.assertEqual(grid[i + 1][j], "^")
                    tiles += 1
                elif value == "^":
                    self.assertGreaterEqual(i - 1, 0)
                    self.assertEqual(grid[i - 1][j], "v")
        self.assertEqual(tiles, 3)

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
        self.assert_backends_equal(source, input_data, ["0", "1", "0", "1"])

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
        self.assert_backends_equal(source, input_data, ["15", "7", "25", "6"])

    def test_practice2_c_sample(self):
        source = (EXAMPLES / "practice2_c.kis").read_text(encoding="utf-8")
        input_data = """\
5
4 10 6 3
6 5 4 3
1 1 0 0
31415 92653 58979 32384
1000000000 1000000000 999999999 999999999
"""
        self.assert_backends_equal(
            source,
            input_data,
            ["3", "13", "0", "314095480", "499999999500000000"],
        )

    def test_practice2_d_sample(self):
        source = (EXAMPLES / "practice2_d.kis").read_text(encoding="utf-8")
        input_data = """\
3 3
#..
..#
...
"""
        reference = kisite.run(source, input_data)
        compiled = kisite.run_compiled(source, input_data)
        self.assert_practice2_d_output(reference)
        self.assert_practice2_d_output(compiled)
        self.assertEqual(compiled, reference)


if __name__ == "__main__":
    unittest.main()
