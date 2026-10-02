import unittest

import kisite


class KisiteTests(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(kisite.run('Takute kas "Hello World".'), ["Hello World"])

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

    def test_sonome_initializes_variable(self):
        source = """
        Sonome kas x tas 3.
        Takute kas x.
        Takute kas x + 5.
        """
        self.assertEqual(kisite.run(source), ["3", "8"])

    def test_sonome_rejects_reinitialization(self):
        source = """
        Sonome kas x tas 3.
        Sonome kas x tas 4.
        """
        with self.assertRaisesRegex(kisite.KisiteError, "already initialized"):
            kisite.run(source)

    def test_kemese_updates_existing_variable(self):
        source = """
        Sonome kas x tas 3.
        Kemese kas x tas x + 5.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["8"])

    def test_kemese_rejects_unknown_variable(self):
        with self.assertRaisesRegex(kisite.KisiteError, "not initialized"):
            kisite.run("Kemese kas x tas 3.")

    def test_unknown_variable_is_an_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "not initialized"):
            kisite.run("Takute kas x.")

    def test_kate_returns_boolean(self):
        source = """
        Takute kas 3 kate 3.
        Takute kas 3 kate 4.
        Takute kas "a" kate "a".
        Takute kas "a" kate "b".
        """
        self.assertEqual(kisite.run(source), ["true", "false", "true", "false"])

    def test_kate_has_lower_precedence_than_arithmetic(self):
        self.assertEqual(kisite.run("Takute kas 2 + 3 kate 1 + 4."), ["true"])

    def test_kate_result_can_be_compared(self):
        self.assertEqual(kisite.run("Takute kas (1 kate 1) kate (2 kate 2)."), ["true"])

    def test_palusta_executes_statement_when_true(self):
        source = """
        Sonome kas x tas 8.
        Takute kas "yes" palusta x kate 8.
        """
        self.assertEqual(kisite.run(source), ["yes"])

    def test_palusta_skips_statement_when_false(self):
        source = """
        Sonome kas x tas 7.
        Takute kas "yes" palusta x kate 8.
        Takute kas "done".
        """
        self.assertEqual(kisite.run(source), ["done"])

    def test_palusta_can_mutate_state(self):
        source = """
        Sonome kas x tas 1.
        Kemese kas x tas 2 palusta x kate 1.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["2"])

    def test_palusta_requires_boolean_condition(self):
        with self.assertRaisesRegex(kisite.KisiteError, "condition must be boolean"):
            kisite.run('Takute kas "bad" palusta 1.')


if __name__ == "__main__":
    unittest.main()
