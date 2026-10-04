from pathlib import Path
import unittest

import kisite


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "atcoder"


class CompiledBackendTests(unittest.TestCase):
    def test_scalar_while_and_augmented_assignment(self):
        source = """
Sonome kas i tas 0.
Pilike palusta i < 1000 {
    i += 1.
}
Takute kas i.
"""
        self.assertEqual(kisite.run_compiled(source), ["1000"])

    def test_indexed_augmented_assignment(self):
        source = """
Sonome kas a tas [0].
Sonome kas i tas 0.
Pilike palusta i < 1000 {
    a[0] += 1.
    i += 1.
}
Takute kas a[0].
"""
        self.assertEqual(kisite.run_compiled(source), ["1000"])

    def test_function_and_array_comprehension(self):
        source = """
Kalivisku musope kas twice vis x {
    Jasepe kas x * 2.
}
Sonome kas a tas [Kisite kas twice vis x Pilike kas x pas (Kisite kas pilika vis 5)].
Takute kas a vis " ".
"""
        self.assertEqual(kisite.run_compiled(source), ["0 2 4 6 8"])

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
        self.assertEqual(
            kisite.run_compiled(source, input_data),
            ["15", "7", "25", "6"],
        )


if __name__ == "__main__":
    unittest.main()
