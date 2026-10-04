import io
import math
import unittest

import kisite


class FlushProbe(io.StringIO):
    def __init__(self):
        super().__init__()
        self.flush_count = 0

    def flush(self):
        self.flush_count += 1
        super().flush()


class Kisite011StdlibTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(kisite.VERSION, "0.1.1")

    def test_live_output_and_flush(self):
        stream = FlushProbe()
        result = kisite.run(
            'Takute kas "query". Kisite kas flush. Takute kas "done".',
            output_stream=stream,
        )
        self.assertEqual(result, ["query", "done"])
        self.assertEqual(stream.getvalue(), "query\ndone\n")
        self.assertEqual(stream.flush_count, 1)

    def test_flush_is_statement_only(self):
        with self.assertRaisesRegex(kisite.KisiteError, "does not return a value"):
            kisite.run("Takute kas Kisite kas flush.")

    def test_pi_and_trigonometry(self):
        source = """
        Sonome kas p tas Kisite kas pi.
        Takute kas Kisite kas sin vis p / 2.
        Takute kas Kisite kas cos vis 0.
        """
        output = kisite.run(source)
        self.assertAlmostEqual(float(output[0]), 1.0, places=12)
        self.assertAlmostEqual(float(output[1]), 1.0, places=12)

    def test_more_math_helpers(self):
        source = """
        Takute kas Kisite kas sqrt vis 81.
        Takute kas Kisite kas floor vis 3.9.
        Takute kas Kisite kas ceil vis 3.1.
        Takute kas Kisite kas hypot vis 3 kasta 4.
        """
        self.assertEqual(kisite.run(source), ["9", "3", "4", "5"])

    def test_heap_helpers(self):
        source = """
        Sonome kas h tas Kisite kas heapify vis [5, 1, 4, 3].
        Kisite kas heappush vis h kasta 2.
        Takute kas Kisite kas heappop vis h.
        Takute kas Kisite kas heappeek vis h.
        Takute kas Kisite kas kipala vis h.
        """
        self.assertEqual(kisite.run(source), ["1", "2", "4"])

    def test_heap_supports_pair_like_arrays(self):
        source = """
        Sonome kas h tas Kisite kas heapify vis [[3, 9], [1, 8], [1, 4]].
        Takute kas Kisite kas heappop vis h.
        """
        self.assertEqual(kisite.run(source), ["[1, 4]"])

    def test_bisect_helpers(self):
        source = """
        Sonome kas a tas [1, 2, 2, 2, 5].
        Takute kas Kisite kas bisectleft vis a kasta 2.
        Takute kas Kisite kas bisectright vis a kasta 2.
        """
        self.assertEqual(kisite.run(source), ["1", "4"])

    def test_sqrt_domain_error(self):
        with self.assertRaisesRegex(kisite.KisiteError, "sqrt domain error"):
            kisite.run("Takute kas Kisite kas sqrt vis -1.")


if __name__ == "__main__":
    unittest.main()
