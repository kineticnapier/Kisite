import tempfile
import unittest
from pathlib import Path

import kisite


class Kisite014Tests(unittest.TestCase):
    def test_regression_arithmetic_variables_and_conditions(self):
        source = """
        Sonome kas x tas 2 + 3 * 4.
        Palusta x kate 14 {
            Kemese kas x tas x + 1.
        } Japalusta {
            Kemese kas x tas 0.
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["15"])

    def test_input_is_string_and_minika_converts(self):
        source = """
        Polike kas a kasta b vos stdin.
        Sonome kas x tas Kisite kas minika vis a.
        Sonome kas y tas Kisite kas minika vis b.
        Takute kas x + y.
        """
        self.assertEqual(kisite.run(source, "3 5"), ["8"])

    def test_arrays_index_assignment_and_foreach(self):
        source = """
        Sonome kas a tas [1, 2, 3].
        Kemese kas a[1] tas 9.
        Pilike kas x pas a { Takute kas x. }
        """
        self.assertEqual(kisite.run(source), ["1", "9", "3"])

    def test_function_and_recursion(self):
        source = """
        Kalivisku musope kas fact vis n {
            Palusta n <= 1 { Jasepe kas 1. }
            Jasepe kas n * (Kisite kas fact vis n - 1).
        }
        Takute kas Kisite kas fact vis 5.
        """
        self.assertEqual(kisite.run(source), ["120"])

    def test_bool_literals(self):
        self.assertEqual(
            kisite.run("Takute kas Kati. Takute kas Kixkati."),
            ["true", "false"],
        )

    def test_kix_not(self):
        self.assertEqual(
            kisite.run("Takute kas Kix Kati. Takute kas Kix Kixkati."),
            ["false", "true"],
        )

    def test_kix_requires_bool(self):
        with self.assertRaisesRegex(kisite.KisiteError, "kix requires a boolean"):
            kisite.run("Takute kas Kix 1.")

    def test_kasta_and_vista(self):
        source = """
        Takute kas Kati kasta Kati.
        Takute kas Kati kasta Kixkati.
        Takute kas Kixkati vista Kati.
        Takute kas Kixkati vista Kixkati.
        """
        self.assertEqual(kisite.run(source), ["true", "false", "true", "false"])

    def test_logical_precedence(self):
        self.assertEqual(
            kisite.run("Takute kas Kati vista Kixkati kasta Kixkati."),
            ["true"],
        )

    def test_logical_short_circuit(self):
        source = """
        Takute kas Kixkati kasta (Kisite kas nope).
        Takute kas Kati vista (Kisite kas nope).
        """
        self.assertEqual(kisite.run(source), ["false", "true"])

    def test_function_argument_separator_still_works(self):
        source = """
        Kalivisku musope kas both vis a kasta b {
            Jasepe kas a kasta b.
        }
        Takute kas Kisite kas both vis Kati kasta Kixkati.
        """
        self.assertEqual(kisite.run(source), ["false"])

    def test_logical_and_can_be_passed_with_parentheses(self):
        source = """
        Kalivisku musope kas echo vis x { Jasepe kas x. }
        Takute kas Kisite kas echo vis (Kati kasta Kixkati).
        """
        self.assertEqual(kisite.run(source), ["false"])

    def test_kipala_array_and_string(self):
        source = """
        Takute kas Kisite kas kipala vis [1, 2, 3].
        Takute kas Kisite kas kipala vis "abcd".
        """
        self.assertEqual(kisite.run(source), ["3", "4"])

    def test_kipala_rejects_number(self):
        with self.assertRaisesRegex(kisite.KisiteError, "kipala requires"):
            kisite.run("Takute kas Kisite kas kipala vis 3.")

    def test_putike_appends(self):
        source = """
        Sonome kas a tas [1, 2].
        Putike kas 3 tas a.
        Takute kas a[2].
        """
        self.assertEqual(kisite.run(source), ["3"])

    def test_putike_nested_array(self):
        source = """
        Sonome kas a tas [[1], [2]].
        Putike kas 9 tas a[0].
        Takute kas a[0][1].
        """
        self.assertEqual(kisite.run(source), ["9"])

    def test_putike_requires_array(self):
        with self.assertRaisesRegex(kisite.KisiteError, "putike target must be an array"):
            kisite.run('Sonome kas s tas "x". Putike kas 1 tas s.')

    def test_kinise_deletes_array_element(self):
        source = """
        Sonome kas a tas [10, 20, 30].
        Kinise kas a[1].
        Takute kas a[1].
        Takute kas Kisite kas kipala vis a.
        """
        self.assertEqual(kisite.run(source), ["30", "2"])

    def test_kinise_delete_requires_index(self):
        with self.assertRaisesRegex(kisite.KisiteError, "indexed array element"):
            kisite.run("Sonome kas a tas [1]. Kinise kas a.")

    def test_break(self):
        source = """
        Sonome kas x tas 0.
        Pilike palusta Kati {
            Kemese kas x tas x + 1.
            Palusta x kate 3 { Kinise. }
        }
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["3"])

    def test_continue(self):
        source = """
        Sonome kas out tas [].
        Pilike kas i pas Kisite kas pilika vis 5 {
            Palusta i kate 2 { Kinate. }
            Putike kas i tas out.
        }
        Pilike kas x pas out { Takute kas x. }
        """
        self.assertEqual(kisite.run(source), ["0", "1", "3", "4"])

    def test_break_outside_loop_is_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "inside a loop"):
            kisite.run("Kinise.")

    def test_continue_outside_loop_is_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "inside a loop"):
            kisite.run("Kinate.")

    def test_pilika_one_argument(self):
        source = """
        Pilike kas i pas Kisite kas pilika vis 4 {
            Takute kas i.
        }
        """
        self.assertEqual(kisite.run(source), ["0", "1", "2", "3"])

    def test_pilika_two_arguments(self):
        source = """
        Pilike kas i pas Kisite kas pilika vis 2 kasta 5 {
            Takute kas i.
        }
        """
        self.assertEqual(kisite.run(source), ["2", "3", "4"])

    def test_pilika_three_arguments(self):
        source = """
        Pilike kas i pas Kisite kas pilika vis 2 kasta 9 kasta 3 {
            Takute kas i.
        }
        """
        self.assertEqual(kisite.run(source), ["2", "5", "8"])

    def test_pilika_rejects_zero_step(self):
        with self.assertRaisesRegex(kisite.KisiteError, "step cannot be zero"):
            kisite.run("Pilike kas i pas Kisite kas pilika vis 0 kasta 4 kasta 0 { Takute kas i. }")

    def test_kipala_range(self):
        self.assertEqual(
            kisite.run("Takute kas Kisite kas kipala vis (Kisite kas pilika vis 2 kasta 8 kasta 2)."),
            ["3"],
        )

    def test_file_stream_keeps_position(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "input.txt"
            p.write_text("10 20 30", encoding="utf-8")
            source = """
            Polike kas a kasta b vos "input.txt".
            Polike kas c vos "input.txt".
            Takute kas a.
            Takute kas b.
            Takute kas c.
            """
            self.assertEqual(kisite.run(source, base_dir=d), ["10", "20", "30"])

    def test_missing_file_stream_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(kisite.KisiteError, "cannot open stream"):
                kisite.run('Polike kas x vos "missing.txt".', base_dir=d)

    def test_typed_minika(self):
        source = """
        Sonome kas x sis minika tas 3.
        Kemese kas x tas 2.5.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["2.5"])

    def test_typed_takuta(self):
        self.assertEqual(
            kisite.run('Sonome kas s sis takuta tas "abc". Takute kas s.'),
            ["abc"],
        )

    def test_typed_kineska(self):
        self.assertEqual(
            kisite.run("Sonome kas a sis kineska tas [1]. Putike kas 2 tas a. Takute kas a[1]."),
            ["2"],
        )

    def test_typed_kati(self):
        self.assertEqual(
            kisite.run("Sonome kas b sis kati tas Kati. Takute kas b."),
            ["true"],
        )

    def test_type_mismatch_on_initialize(self):
        with self.assertRaisesRegex(kisite.KisiteError, "requires type minika"):
            kisite.run('Sonome kas x sis minika tas "3".')

    def test_type_mismatch_on_assignment(self):
        with self.assertRaisesRegex(kisite.KisiteError, "requires type kati"):
            kisite.run("Sonome kas b sis kati tas Kati. Kemese kas b tas 1.")

    def test_polike_respects_existing_type(self):
        with self.assertRaisesRegex(kisite.KisiteError, "requires type minika"):
            kisite.run("Sonome kas x sis minika tas 0. Polike kas x vos stdin.", "5")

    def test_else_if_first_branch(self):
        source = """
        Sonome kas x tas 3.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta palusta x kate 0 {
            Takute kas "zero".
        } Japalusta {
            Takute kas "negative".
        }
        """
        self.assertEqual(kisite.run(source), ["positive"])

    def test_else_if_middle_branch(self):
        source = """
        Sonome kas x tas 0.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta palusta x kate 0 {
            Takute kas "zero".
        } Japalusta {
            Takute kas "negative".
        }
        """
        self.assertEqual(kisite.run(source), ["zero"])

    def test_else_if_last_branch(self):
        source = """
        Sonome kas x tas -1.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta palusta x kate 0 {
            Takute kas "zero".
        } Japalusta {
            Takute kas "negative".
        }
        """
        self.assertEqual(kisite.run(source), ["negative"])


if __name__ == "__main__":
    unittest.main()
