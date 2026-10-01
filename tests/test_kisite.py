import unittest

import kisite


class KisiteTests(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(
            kisite.run('Takute kas "Hello World".'),
            ["Hello World"],
        )

    def test_four_arithmetic_operations(self):
        source = """
        Takute kas 3 + 5.
        Takute kas 10 - 4.
        Takute kas 6 * 7.
        Takute kas 20 / 5.
        """
        self.assertEqual(kisite.run(source), ["8", "6", "42", "4"])

    def test_precedence(self):
        self.assertEqual(kisite.run("Takute kas 2 + 3 * 4."), ["14"])

    def test_parentheses(self):
        self.assertEqual(kisite.run("Takute kas (2 + 3) * 4."), ["20"])

    def test_unary_operators(self):
        self.assertEqual(kisite.run("Takute kas -3 + +5."), ["2"])

    def test_curly_quoted_string(self):
        self.assertEqual(kisite.run("Takute kas “jaa”."), ["jaa"])

    def test_division_by_zero_is_an_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "division by zero"):
            kisite.run("Takute kas 1 / 0.")


if __name__ == "__main__":
    unittest.main()
