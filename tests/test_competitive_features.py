import unittest

import kisite


class CompetitiveFeatureTests(unittest.TestCase):
    def test_remainder(self):
        self.assertEqual(kisite.run("Takute kas 17 % 5."), ["2"])

    def test_floor_division(self):
        self.assertEqual(kisite.run("Takute kas 17 // 5. Takute kas -7 // 3."), ["3", "-3"])

    def test_multiplicative_precedence(self):
        self.assertEqual(kisite.run("Takute kas 2 + 17 % 5 * 3."), ["8"])

    def test_floor_division_requires_integers(self):
        with self.assertRaisesRegex(kisite.KisiteError, "integer operands"):
            kisite.run("Takute kas 5.0 // 2.")

    def test_remainder_requires_integers(self):
        with self.assertRaisesRegex(kisite.KisiteError, "integer operands"):
            kisite.run("Takute kas 5 % 2.0.")

    def test_floor_division_by_zero(self):
        with self.assertRaisesRegex(kisite.KisiteError, "integer division by zero"):
            kisite.run("Takute kas 5 // 0.")

    def test_remainder_by_zero(self):
        with self.assertRaisesRegex(kisite.KisiteError, "remainder by zero"):
            kisite.run("Takute kas 5 % 0.")

    def test_paline_sorts_numbers(self):
        source = """
        Sonome kas a tas Kisite kas paline vis [5, 1, 4, 2, 3].
        Pilike kas x pas a { Takute kas x. }
        """
        self.assertEqual(kisite.run(source), ["1", "2", "3", "4", "5"])

    def test_paline_sorts_nested_arrays_lexicographically(self):
        source = """
        Sonome kas a tas Kisite kas paline vis [[7, 8], [2, 5], [1, 5]].
        Takute kas a[0][0].
        Takute kas a[1][0].
        Takute kas a[2][0].
        """
        self.assertEqual(kisite.run(source), ["1", "2", "7"])

    def test_paline_returns_new_array(self):
        source = """
        Sonome kas a tas [3, 1, 2].
        Sonome kas b tas Kisite kas paline vis a.
        Takute kas a[0].
        Takute kas b[0].
        """
        self.assertEqual(kisite.run(source), ["3", "1"])

    def test_japonavi_and_ponavi_multiple_arguments(self):
        source = """
        Takute kas Kisite kas japonavi vis 9 kasta 2 kasta 7.
        Takute kas Kisite kas ponavi vis 9 kasta 2 kasta 7.
        """
        self.assertEqual(kisite.run(source), ["2", "9"])

    def test_japonavi_and_ponavi_array(self):
        source = """
        Sonome kas a tas [9, 2, 7].
        Takute kas Kisite kas japonavi vis a.
        Takute kas Kisite kas ponavi vis a.
        """
        self.assertEqual(kisite.run(source), ["2", "9"])

    def test_japonavi_and_ponavi_range(self):
        source = """
        Sonome kas r tas Kisite kas pilika vis 3 kasta 10 kasta 2.
        Takute kas Kisite kas japonavi vis r.
        Takute kas Kisite kas ponavi vis r.
        """
        self.assertEqual(kisite.run(source), ["3", "9"])

    def test_extreme_rejects_empty_array(self):
        with self.assertRaisesRegex(kisite.KisiteError, "empty sequence"):
            kisite.run("Takute kas Kisite kas japonavi vis [].")

    def test_paline_rejects_string_array(self):
        with self.assertRaisesRegex(kisite.KisiteError, "comparable numbers or arrays"):
            kisite.run('Takute kas Kisite kas paline vis ["b", "a"].')


if __name__ == "__main__":
    unittest.main()
