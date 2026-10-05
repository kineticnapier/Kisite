import unittest

import kisite


class FunctionTests(unittest.TestCase):
    def test_minika_converts_integer_text(self):
        self.assertEqual(kisite.run('Takute kas Kisite kas minika vis "123".'), ["123"])

    def test_minika_converts_float_text(self):
        self.assertEqual(kisite.run('Takute kas Kisite kas minika vis "2.5".'), ["2.5"])

    def test_minika_rejects_non_number(self):
        with self.assertRaisesRegex(kisite.KisiteError, "cannot convert"):
            kisite.run('Takute kas Kisite kas minika vis "abc".')

    def test_minika_requires_one_argument(self):
        with self.assertRaisesRegex(kisite.KisiteError, "expects 1 argument"):
            kisite.run("Kisite kas minika.")

    def test_function_definition_and_return(self):
        source = """
        Kalivisku musope kas add vis a kasta b {
            Jasepe kas a + b.
        }
        Takute kas Kisite kas add vis 2 kasta 3.
        """
        self.assertEqual(kisite.run(source), ["5"])

    def test_zero_argument_function(self):
        source = """
        Kalivisku musope kas answer {
            Jasepe kas 42.
        }
        Takute kas Kisite kas answer.
        """
        self.assertEqual(kisite.run(source), ["42"])

    def test_function_can_be_called_as_statement(self):
        source = """
        Kalivisku musope kas greet vis name {
            Takute kas name.
        }
        Kisite kas greet vis "hello".
        """
        self.assertEqual(kisite.run(source), ["hello"])

    def test_value_call_requires_return(self):
        source = """
        Kalivisku musope kas greet { Takute kas "hi". }
        Takute kas Kisite kas greet.
        """
        with self.assertRaisesRegex(kisite.KisiteError, "did not return a value"):
            kisite.run(source)

    def test_function_arity_is_checked(self):
        source = """
        Kalivisku musope kas add vis a kasta b { Jasepe kas a + b. }
        Takute kas Kisite kas add vis 1.
        """
        with self.assertRaisesRegex(kisite.KisiteError, "expects 2 arguments"):
            kisite.run(source)

    def test_nested_fixed_arity_builtin_arguments_do_not_consume_outer_kasta(self):
        source = """
        Kalivisku musope kas add vis x kasta y {
            Jasepe kas x + y.
        }
        Polike kas raw vos stdin.
        Takute kas Kisite kas add vis Kisite kas minika vis raw kasta Kisite kas minika vis raw.
        """
        self.assertEqual(kisite.run(source, "6\n"), ["12"])
        self.assertEqual(kisite.run_compiled(source, "6\n"), ["12"])

    def test_nested_user_function_arguments_do_not_consume_outer_kasta(self):
        source = """
        Kalivisku musope kas inc vis x { Jasepe kas x + 1. }
        Kalivisku musope kas add vis x kasta y { Jasepe kas x + y. }
        Takute kas Kisite kas add vis Kisite kas inc vis 2 kasta Kisite kas inc vis 3.
        """
        self.assertEqual(kisite.run(source), ["7"])
        self.assertEqual(kisite.run_compiled(source), ["7"])

    def test_function_has_local_scope(self):
        source = """
        Sonome kas x tas 100.
        Kalivisku musope kas f vis x {
            Kemese kas x tas x + 1.
            Jasepe kas x.
        }
        Takute kas Kisite kas f vis 5.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["6", "100"])

    def test_function_does_not_capture_global_variables(self):
        source = """
        Sonome kas x tas 10.
        Kalivisku musope kas f { Jasepe kas x. }
        Takute kas Kisite kas f.
        """
        with self.assertRaisesRegex(kisite.KisiteError, "not initialized"):
            kisite.run(source)

    def test_return_works_inside_nested_block(self):
        source = """
        Kalivisku musope kas sign vis x {
            Palusta x > 0 { Jasepe kas 1. }
            Jasepe kas 0.
        }
        Takute kas Kisite kas sign vis 4.
        """
        self.assertEqual(kisite.run(source), ["1"])

    def test_recursion(self):
        source = """
        Kalivisku musope kas fact vis n {
            Palusta n <= 1 { Jasepe kas 1. }
            Jasepe kas n * (Kisite kas fact vis n - 1).
        }
        Takute kas Kisite kas fact vis 5.
        """
        self.assertEqual(kisite.run(source), ["120"])

    def test_jasepe_is_rejected_at_top_level(self):
        with self.assertRaisesRegex(kisite.KisiteError, "inside a function"):
            kisite.run("Jasepe kas 1.")

    def test_undefined_function_is_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "not defined"):
            kisite.run("Kisite kas nope.")

    def test_duplicate_parameters_are_rejected(self):
        with self.assertRaisesRegex(kisite.KisiteError, "duplicate parameter"):
            kisite.run("Kalivisku musope kas f vis x kasta x { Jasepe kas x. }")


if __name__ == "__main__":
    unittest.main()
