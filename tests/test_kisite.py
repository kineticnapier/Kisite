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
        with self.assertRaisesRegex(kisite.KisiteError, "already initialized"):
            kisite.run("Sonome kas x tas 3. Sonome kas x tas 4.")

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

    def test_comparison_operators(self):
        source = """
        Takute kas 2 < 3.
        Takute kas 3 > 2.
        Takute kas 2 <= 2.
        Takute kas 3 >= 4.
        Takute kas 3 != 4.
        Takute kas 3 != 3.
        """
        self.assertEqual(
            kisite.run(source),
            ["true", "true", "true", "false", "true", "false"],
        )

    def test_not_equal_matches_kate_semantics(self):
        source = """
        Takute kas "a" != "b".
        Takute kas "a" != "a".
        Takute kas 3 != 3.0.
        """
        self.assertEqual(kisite.run(source), ["true", "false", "false"])

    def test_ordering_comparison_requires_numbers(self):
        with self.assertRaisesRegex(kisite.KisiteError, "ordering comparison requires numbers"):
            kisite.run('Takute kas "a" < "b".')

    def test_comparison_has_lower_precedence_than_arithmetic(self):
        source = """
        Takute kas 2 + 3 < 6.
        Takute kas 2 * 3 >= 1 + 5.
        """
        self.assertEqual(kisite.run(source), ["true", "true"])

    def test_kate_has_lower_precedence_than_arithmetic(self):
        self.assertEqual(kisite.run("Takute kas 2 + 3 kate 1 + 4."), ["true"])

    def test_kate_result_can_be_compared(self):
        self.assertEqual(kisite.run("Takute kas (1 kate 1) kate (2 kate 2)."), ["true"])

    def test_block_executes_statements_in_order(self):
        source = """
        {
            Takute kas "a".
            Takute kas "b".
        }
        """
        self.assertEqual(kisite.run(source), ["a", "b"])

    def test_block_shares_variable_scope(self):
        source = """
        {
            Sonome kas x tas 3.
            Kemese kas x tas x + 1.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["4"])

    def test_unterminated_block_is_an_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "unterminated block"):
            kisite.run('{ Takute kas "oops".')

    def test_palusta_executes_block_when_true(self):
        source = """
        Sonome kas x tas 8.
        Palusta x kate 8 {
            Takute kas "yes".
        }
        """
        self.assertEqual(kisite.run(source), ["yes"])

    def test_palusta_accepts_ordering_comparison(self):
        source = """
        Sonome kas x tas 11.
        Palusta x > 10 {
            Takute kas "big".
        }
        """
        self.assertEqual(kisite.run(source), ["big"])

    def test_palusta_executes_multiple_statements_when_true(self):
        source = """
        Sonome kas x tas 2.
        Palusta x > 0 {
            Takute kas "positive".
            Kemese kas x tas x + 1.
            Takute kas x.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["positive", "3", "3"])

    def test_palusta_skips_block_when_false(self):
        source = """
        Sonome kas x tas 0.
        Palusta x > 0 {
            Polike kas skipped vos stdin.
            Takute kas "bad".
        }
        Polike kas actual vos stdin.
        Takute kas actual.
        """
        self.assertEqual(kisite.run(source, "99"), ["99"])

    def test_japalusta_runs_when_condition_is_false(self):
        source = """
        Sonome kas x tas 0.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta {
            Takute kas "non-positive".
        }
        """
        self.assertEqual(kisite.run(source), ["non-positive"])

    def test_japalusta_is_skipped_when_condition_is_true(self):
        source = """
        Sonome kas x tas 3.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta {
            Takute kas "bad".
        }
        """
        self.assertEqual(kisite.run(source), ["positive"])

    def test_japalusta_can_mutate_state(self):
        source = """
        Sonome kas x tas 0.
        Palusta x > 0 {
            Kemese kas x tas 10.
        } Japalusta {
            Kemese kas x tas -1.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["-1"])

    def test_japalusta_skipped_branch_does_not_consume_input(self):
        source = """
        Sonome kas x tas 1.
        Palusta x > 0 {
            Takute kas "yes".
        } Japalusta {
            Polike kas skipped vos stdin.
        }
        Polike kas actual vos stdin.
        Takute kas actual.
        """
        self.assertEqual(kisite.run(source, "99"), ["yes", "99"])

    def test_japalusta_requires_block(self):
        with self.assertRaisesRegex(kisite.KisiteError, "japalusta must be followed by a block"):
            kisite.run('Palusta 1 kate 2 { Takute kas "no". } Japalusta Takute kas "bad".')

    def test_standalone_japalusta_is_rejected(self):
        with self.assertRaisesRegex(kisite.KisiteError, "japalusta must follow a palusta block"):
            kisite.run('Japalusta { Takute kas "bad". }')

    def test_nested_conditional_blocks(self):
        source = """
        Sonome kas x tas 2.
        Palusta x > 0 {
            Palusta x > 1 {
                Takute kas "inner".
            } Japalusta {
                Takute kas "not-inner".
            }
            Takute kas "outer".
        }
        """
        self.assertEqual(kisite.run(source), ["inner", "outer"])

    def test_palusta_skips_when_false(self):
        source = """
        Sonome kas x tas 7.
        Palusta x kate 8 {
            Takute kas "yes".
        }
        Takute kas "done".
        """
        self.assertEqual(kisite.run(source), ["done"])

    def test_palusta_can_mutate_state(self):
        source = """
        Sonome kas x tas 1.
        Palusta x kate 1 {
            Kemese kas x tas 2.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["2"])

    def test_palusta_requires_boolean_condition(self):
        with self.assertRaisesRegex(kisite.KisiteError, "condition must be boolean"):
            kisite.run('Palusta 1 { Takute kas "bad". }')

    def test_palusta_requires_block(self):
        with self.assertRaisesRegex(kisite.KisiteError, "must be followed by a block"):
            kisite.run('Palusta 1 kate 1 Takute kas "bad".')

    def test_postfix_palusta_is_rejected(self):
        with self.assertRaisesRegex(kisite.KisiteError, "postfix palusta syntax was removed"):
            kisite.run('Takute kas "yes" palusta 1 kate 1.')

    def test_polike_reads_integer_from_stdin(self):
        source = """
        Polike kas a vos stdin.
        Polike kas b vos stdin.
        Takute kas a + b.
        """
        self.assertEqual(kisite.run(source, "3 5"), ["8"])

    def test_polike_reads_multiple_values_with_kasta(self):
        source = """
        Polike kas a kasta b vos stdin.
        Takute kas a + b.
        """
        self.assertEqual(kisite.run(source, "3 5"), ["8"])

    def test_polike_reads_three_values_with_kasta(self):
        source = """
        Polike kas a kasta b kasta c vos stdin.
        Takute kas a + b + c.
        """
        self.assertEqual(kisite.run(source, "1 2 3"), ["6"])

    def test_polike_reads_float_and_string(self):
        source = """
        Polike kas x kasta y vos stdin.
        Takute kas x.
        Takute kas y.
        """
        self.assertEqual(kisite.run(source, "2.5 hello"), ["2.5", "hello"])

    def test_polike_overwrites_existing_variable(self):
        source = """
        Sonome kas x tas 1.
        Polike kas x vos stdin.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source, "9"), ["9"])

    def test_polike_exhausted_stdin_is_an_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "stdin is exhausted"):
            kisite.run("Polike kas x vos stdin.", "")

    def test_polike_can_be_conditional_without_consuming_input_when_false(self):
        source = """
        Sonome kas x tas 0.
        Palusta x kate 1 {
            Polike kas y vos stdin.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source, "99"), ["0"])


if __name__ == "__main__":
    unittest.main()
