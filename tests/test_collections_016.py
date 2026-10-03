import unittest

import kisite


class Kisite016Tests(unittest.TestCase):
    def test_tuni_jatuni_and_tuna_type(self):
        source = """
        Sonome kas a sis tuna tas Tuni.
        Sonome kas b sis tuna tas Jatuni.
        Takute kas a.
        Takute kas b.
        """
        self.assertEqual(kisite.run(source), ["true", "false"])

    def test_tuna_type_rejects_number(self):
        with self.assertRaisesRegex(kisite.KisiteError, "requires type tuna"):
            kisite.run("Sonome kas b sis tuna tas Tuni. Kemese kas b tas 1.")

    def test_set_literal_membership_add_delete(self):
        source = """
        Sonome kas s tas {1, 2, 2}.
        Takute kas Kisite kas kipala vis s.
        Takute kas 2 pas s.
        Putike kas 3 tas s.
        Kinise kas s[1].
        Takute kas 1 pas s.
        Takute kas 3 pas s.
        """
        self.assertEqual(kisite.run(source), ["2", "true", "false", "true"])

    def test_dictionary_index_assignment_membership_delete(self):
        source = """
        Sonome kas d tas {"a": 1}.
        Kemese kas d["b"] tas 2.
        Takute kas d["b"].
        Takute kas "a" pas d.
        Kinise kas d["a"].
        Takute kas "a" pas d.
        """
        self.assertEqual(kisite.run(source), ["2", "true", "false"])

    def test_empty_set_and_dictionary(self):
        self.assertEqual(
            kisite.run("Takute kas Kisite kas kipala vis {}. Takute kas Kisite kas kipala vis {:}."),
            ["0", "0"],
        )

    def test_membership_array_string_and_range(self):
        source = """
        Takute kas 2 pas [1, 2, 3].
        Takute kas "b" pas "abc".
        Takute kas 4 pas (Kisite kas pilika vis 0 kasta 6 kasta 2).
        """
        self.assertEqual(kisite.run(source), ["true", "true", "true"])

    def test_sum_and_abs(self):
        source = """
        Takute kas Kisite kas sum vis [1, 2, 3, 4].
        Takute kas Kisite kas abs vis -7.
        """
        self.assertEqual(kisite.run(source), ["10", "7"])

    def test_separator_output(self):
        self.assertEqual(kisite.run('Takute kas [1, 2, 3] vis " ".'), ["1 2 3"])

    def test_dictionary_foreach_uses_keys(self):
        source = """
        Sonome kas d tas {"a": 1, "b": 2}.
        Pilike kas k pas d { Takute kas k. }
        """
        self.assertEqual(kisite.run(source), ["a", "b"])


if __name__ == "__main__":
    unittest.main()
