import unittest

import kisite


class ArraysAndLoopsTests(unittest.TestCase):
    def test_array_literal_and_indexing(self):
        source = """
        Sonome kas a tas [10, 20, 30].
        Takute kas a[0].
        Takute kas a[2].
        """
        self.assertEqual(kisite.run(source), ["10", "30"])

    def test_empty_array(self):
        self.assertEqual(kisite.run("Takute kas []."), ["[]"])

    def test_dynamic_and_nested_indexing(self):
        source = """
        Sonome kas i tas 1.
        Sonome kas a tas [[1, 2], [3, 4]].
        Takute kas a[i][0].
        """
        self.assertEqual(kisite.run(source), ["3"])

    def test_indexed_assignment(self):
        source = """
        Sonome kas a tas [10, 20, 30].
        Kemese kas a[1] tas 99.
        Takute kas a[1].
        """
        self.assertEqual(kisite.run(source), ["99"])

    def test_nested_indexed_assignment(self):
        source = """
        Sonome kas a tas [[1, 2], [3, 4]].
        Kemese kas a[1][0] tas 9.
        Takute kas a[1][0].
        """
        self.assertEqual(kisite.run(source), ["9"])

    def test_index_must_be_integer(self):
        with self.assertRaisesRegex(kisite.KisiteError, "index must be an integer"):
            kisite.run("Sonome kas a tas [1]. Takute kas a[0.5].")

    def test_index_out_of_range(self):
        with self.assertRaisesRegex(kisite.KisiteError, "index out of range"):
            kisite.run("Sonome kas a tas [1]. Takute kas a[1].")

    def test_while_loop(self):
        source = """
        Sonome kas x tas 0.
        Pilike palusta x < 3 {
            Takute kas x.
            Kemese kas x tas x + 1.
        }
        """
        self.assertEqual(kisite.run(source), ["0", "1", "2"])

    def test_while_loop_requires_boolean(self):
        with self.assertRaisesRegex(kisite.KisiteError, "condition must be boolean"):
            kisite.run("Pilike palusta 1 { Takute kas 0. }")

    def test_foreach_array(self):
        source = """
        Sonome kas T tas [10, 20, 30].
        Pilike kas i pas T {
            Takute kas i.
        }
        """
        self.assertEqual(kisite.run(source), ["10", "20", "30"])

    def test_foreach_string(self):
        source = """
        Pilike kas c pas "abc" {
            Takute kas c.
        }
        """
        self.assertEqual(kisite.run(source), ["a", "b", "c"])

    def test_foreach_overwrites_existing_loop_variable(self):
        source = """
        Sonome kas i tas 99.
        Pilike kas i pas [1, 2] {
            Takute kas i.
        }
        Takute kas i.
        """
        self.assertEqual(kisite.run(source), ["1", "2", "2"])

    def test_foreach_requires_array_or_string(self):
        with self.assertRaisesRegex(kisite.KisiteError, "requires an array or string"):
            kisite.run("Pilike kas i pas 3 { Takute kas i. }")

    def test_pilike_requires_mode(self):
        with self.assertRaisesRegex(kisite.KisiteError, "must be followed by 'palusta' or 'kas'"):
            kisite.run("Pilike x { Takute kas x. }")

    def test_existing_palusta_and_japalusta_still_work(self):
        source = """
        Sonome kas x tas 0.
        Palusta x > 0 {
            Takute kas "positive".
        } Japalusta {
            Takute kas "non-positive".
        }
        """
        self.assertEqual(kisite.run(source), ["non-positive"])

    def test_existing_input_still_works(self):
        source = """
        Polike kas a kasta b vos stdin.
        Takute kas a + b.
        """
        self.assertEqual(kisite.run(source, "3 5"), ["8"])


if __name__ == "__main__":
    unittest.main()
