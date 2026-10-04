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

    def assert_practice2_e_output(self, output: list[str], values: list[list[int]], k: int, expected: int):
        n = len(values)
        self.assertEqual(output[0], str(expected))
        self.assertEqual(len(output), n + 1)
        board = output[1:]
        self.assertTrue(all(len(row) == n for row in board))

        total = 0
        column_counts = [0] * n
        for i, row in enumerate(board):
            self.assertLessEqual(row.count("X"), k)
            for j, value in enumerate(row):
                self.assertIn(value, ".X")
                if value == "X":
                    total += values[i][j]
                    column_counts[j] += 1
        self.assertTrue(all(count <= k for count in column_counts))
        self.assertEqual(total, expected)

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

    def test_practice2_e_sample_1(self):
        source = (EXAMPLES / "practice2_e.kis").read_text(encoding="utf-8")
        values = [
            [5, 3, 2],
            [1, 4, 8],
            [7, 6, 9],
        ]
        input_data = """\
3 1
5 3 2
1 4 8
7 6 9
"""
        reference = kisite.run(source, input_data)
        compiled = kisite.run_compiled(source, input_data)
        self.assert_practice2_e_output(reference, values, 1, 19)
        self.assert_practice2_e_output(compiled, values, 1, 19)
        self.assertEqual(compiled, reference)

    def test_practice2_e_sample_2(self):
        source = (EXAMPLES / "practice2_e.kis").read_text(encoding="utf-8")
        values = [
            [10, 10, 1],
            [10, 10, 1],
            [1, 1, 10],
        ]
        input_data = """\
3 2
10 10 1
10 10 1
1 1 10
"""
        reference = kisite.run(source, input_data)
        compiled = kisite.run_compiled(source, input_data)
        self.assert_practice2_e_output(reference, values, 2, 50)
        self.assert_practice2_e_output(compiled, values, 2, 50)
        self.assertEqual(compiled, reference)

    def test_practice2_f_sample_1(self):
        source = (EXAMPLES / "practice2_f.kis").read_text(encoding="utf-8")
        input_data = """\
4 5
1 2 3 4
5 6 7 8 9
"""
        self.assert_backends_equal(source, input_data, ["5 16 34 60 70 70 59 36"])

    def test_practice2_f_sample_2(self):
        source = (EXAMPLES / "practice2_f.kis").read_text(encoding="utf-8")
        input_data = """\
1 1
10000000
10000000
"""
        self.assert_backends_equal(source, input_data, ["871938225"])


if __name__ == "__main__":
    unittest.main()
