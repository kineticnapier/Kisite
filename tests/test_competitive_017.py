import unittest

import kisite


class Kisite017Tests(unittest.TestCase):
    def test_destructuring_and_readints(self):
        source = """
        Sonome kas N kasta K tas Kisite kas readints vis 2.
        Takute kas N + K.
        """
        self.assertEqual(kisite.run(source, "3 5"), ["8"])

    def test_readint(self):
        self.assertEqual(kisite.run("Takute kas Kisite kas readint.", "42"), ["42"])

    def test_fill_deep_copies_nested_arrays(self):
        source = """
        Sonome kas a tas Kisite kas fill vis [] kasta 2.
        Putike kas 7 tas a[0].
        Takute kas Kisite kas kipala vis a[1].
        """
        self.assertEqual(kisite.run(source), ["0"])

    def test_augmented_assignment(self):
        source = """
        Sonome kas x tas 10.
        x += 5.
        x *= 2.
        x //= 6.
        x %= 4.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["1"])

    def test_indexed_augmented_assignment_and_negative_index(self):
        source = """
        Sonome kas a tas [1, 2, 3].
        a[-1] += 4.
        Takute kas a[-1].
        """
        self.assertEqual(kisite.run(source), ["7"])

    def test_slice(self):
        source = """
        Sonome kas a tas [0, 1, 2, 3, 4].
        Takute kas a[1:-1] vis " ".
        Takute kas a[::-1] vis " ".
        """
        self.assertEqual(kisite.run(source), ["1 2 3", "4 3 2 1 0"])

    def test_foreach_destructuring(self):
        source = """
        Sonome kas s tas 0.
        Pilike kas x kasta y pas [[1, 2], [3, 4]] {
            s += x * y.
        }
        Takute kas s.
        """
        self.assertEqual(kisite.run(source), ["14"])

    def test_array_concat_repeat_reverse(self):
        source = """
        Sonome kas a tas [1, 2] + [3].
        Sonome kas b tas [0] * 3.
        Takute kas a vis " ".
        Takute kas b vis " ".
        Takute kas (Kisite kas reverse vis a) vis " ".
        """
        self.assertEqual(kisite.run(source), ["1 2 3", "0 0 0", "3 2 1"])

    def test_combinations(self):
        source = """
        Sonome kas total tas 0.
        Pilike kas v pas Kisite kas combinations vis [1, 2, 3, 4] kasta 3 {
            total += Kisite kas sum vis v.
        }
        Takute kas total.
        """
        self.assertEqual(kisite.run(source), ["30"])

    def test_set_of_point_arrays(self):
        source = """
        Sonome kas pts tas [[1, 2], [1, 2], [0, 3]].
        Sonome kas unique tas Kisite kas set vis pts.
        Sonome kas sorted tas Kisite kas paline vis unique.
        Takute kas Kisite kas kipala vis sorted.
        Takute kas sorted[0][0].
        """
        self.assertEqual(kisite.run(source), ["2", "0"])

    def test_gcd_lcm(self):
        self.assertEqual(
            kisite.run("Takute kas Kisite kas gcd vis 12 kasta 18. Takute kas Kisite kas lcm vis 6 kasta 8."),
            ["6", "24"],
        )

    def test_bitwise(self):
        source = """
        Takute kas 5 & 3.
        Takute kas 1 << 3 + 1.
        Takute kas ~0.
        Sonome kas x tas 1.
        x <<= 4.
        Takute kas x.
        """
        self.assertEqual(kisite.run(source), ["1", "16", "-1", "16"])

    def test_resize_and_truncate(self):
        source = """
        Sonome kas a tas Kisite kas resize vis [1, 2] kasta 4 kasta 9.
        Takute kas a vis " ".
        Takute kas (Kisite kas truncate vis a kasta 2) vis " ".
        """
        self.assertEqual(kisite.run(source), ["1 2 9 9", "1 2"])

    def test_modint_arithmetic(self):
        source = """
        Sonome kas a tas Kisite kas modint vis 10 kasta 7.
        Takute kas a + 3.
        Takute kas a * 3.
        Takute kas a / 3.
        Takute kas -a.
        """
        self.assertEqual(kisite.run(source), ["6", "2", "1", "4"])

    def test_modpow_modinv(self):
        self.assertEqual(
            kisite.run("Takute kas Kisite kas modpow vis 2 kasta 10 kasta 1000. Takute kas Kisite kas modinv vis 3 kasta 7."),
            ["24", "5"],
        )

    def test_exact_convolution(self):
        source = 'Takute kas (Kisite kas convolution vis [1, 2] kasta [3, 4]) vis " ".'
        self.assertEqual(kisite.run(source), ["3 10 8"])

    def test_mod_convolution(self):
        source = 'Takute kas (Kisite kas convolution vis [1, 2, 3] kasta [4, 5] kasta 998244353) vis " ".'
        self.assertEqual(kisite.run(source), ["4 13 22 15"])

    def test_ntt_path(self):
        left = ", ".join("1" for _ in range(40))
        right = ", ".join("1" for _ in range(40))
        source = f"Sonome kas c tas Kisite kas convolution vis [{left}] kasta [{right}] kasta 998244353. Takute kas c[0]. Takute kas c[39]. Takute kas c[-1]."
        self.assertEqual(kisite.run(source), ["1", "40", "1"])

    def test_modint_convolution_infers_modulus(self):
        source = """
        Sonome kas a tas [(Kisite kas modint vis 1 kasta 998244353), (Kisite kas modint vis 2 kasta 998244353)].
        Sonome kas b tas [3, 4].
        Sonome kas c tas Kisite kas convolution vis a kasta b.
        Takute kas c vis " ".
        """
        self.assertEqual(kisite.run(source), ["3 10 8"])


if __name__ == "__main__":
    unittest.main()
