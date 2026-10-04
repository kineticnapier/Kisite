import unittest

import kisite


class KisiteArrayComprehensionTests(unittest.TestCase):
    def test_basic_mapping(self):
        source = """
        Sonome kas a tas [1, 2, 3].
        Sonome kas b tas [x * 2 Pilike kas x pas a].
        Takute kas b vis " ".
        """
        self.assertEqual(kisite.run(source), ["2 4 6"])

    def test_filtered_comprehension(self):
        source = """
        Sonome kas a tas [x Pilike kas x pas (Kisite kas pilika vis 7) Palusta x % 2 kate 0].
        Takute kas a vis " ".
        """
        self.assertEqual(kisite.run(source), ["0 2 4 6"])

    def test_destructuring_comprehension(self):
        source = """
        Sonome kas h tas [[1, 2], [3, 4]].
        Sonome kas s tas 10.
        Sonome kas scaled tas [[s * x, s * y] Pilike kas x kasta y pas h].
        Takute kas scaled[0] vis " ".
        Takute kas scaled[1] vis " ".
        """
        self.assertEqual(kisite.run(source), ["10 20", "30 40"])

    def test_binding_does_not_leak(self):
        source = """
        Sonome kas x tas 99.
        Sonome kas a tas [x + 1 Pilike kas x pas [1, 2]].
        Takute kas x.
        Takute kas a vis " ".
        """
        self.assertEqual(kisite.run(source), ["99", "2 3"])

    def test_condition_must_be_boolean(self):
        source = "Sonome kas a tas [x Pilike kas x pas [1, 2] Palusta x]."
        with self.assertRaises(kisite.KisiteError):
            kisite.run(source)

    def test_duplicate_destructuring_name_is_rejected(self):
        source = "Sonome kas a tas [x Pilike kas x kasta x pas [[1, 2]]]."
        with self.assertRaises(kisite.KisiteError):
            kisite.run(source)


if __name__ == "__main__":
    unittest.main()
