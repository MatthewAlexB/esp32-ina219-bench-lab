import os
import tempfile
import unittest

import analyze_lab1 as al
import fit_accuracy as fa


def tmp(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


CAPTURE = """# gain=3 adc=0x3 samples=4
label,i,t_us,bus_V,shunt_mV,current_mA,ovf
pg3_adc3,0,1000,4.980,2.20,22.00,0
pg3_adc3,1,2000,4.984,2.24,22.40,0
pg3_adc3,2,3000,4.984,2.22,22.20,0
pg3_adc3,3,4000,4.984,2.26,22.60,0
pg3_adcF,0,0,4.984,2.24,22.40,0
pg3_adcF,1,100000,4.984,2.24,22.40,0
timeout
"""


class AnalyzeLab1Tests(unittest.TestCase):
    def test_groups_and_skips_noise(self):
        p = tmp(CAPTURE)
        self.addCleanup(os.remove, p)
        groups = al.parse(p)
        self.assertEqual(list(groups), ["pg3_adc3", "pg3_adcF"])
        self.assertEqual(len(groups["pg3_adc3"]), 4)

    def test_rate_and_stats(self):
        p = tmp(CAPTURE)
        self.addCleanup(os.remove, p)
        s = al.summarize(al.parse(p)["pg3_adc3"])
        self.assertAlmostEqual(s["rate_hz"], 1000.0)
        self.assertAlmostEqual(s["mean_ma"], 22.3)
        self.assertAlmostEqual(s["range_ma"], 0.6)

    def test_noise_in_counts(self):
        rows = [(0, 5, 2.20, 22.0, 0), (1000, 5, 2.24, 22.4, 0)]
        s = al.summarize(rows)
        # std of shunt = 0.0283 mV -> about 2.83 counts of 10 uV
        self.assertAlmostEqual(s["std_counts"], 2.828, places=2)


class FitAccuracyTests(unittest.TestCase):
    def test_perfect_line(self):
        r = fa.fit([(1, 1), (2, 2), (3, 3), (4, 4)])
        self.assertAlmostEqual(r["slope"], 1.0)
        self.assertAlmostEqual(r["intercept"], 0.0)

    def test_gain_and_offset(self):
        r = fa.fit([(10, 10.5 + 0.2), (20, 21.0 + 0.2), (30, 31.5 + 0.2)])
        self.assertAlmostEqual(r["slope"], 1.05, places=6)
        self.assertAlmostEqual(r["intercept"], 0.2, places=6)

    def test_load_skips_header(self):
        p = tmp("reference,measured\n1,1.1\n2,2.1\n3,3.1\n")
        self.addCleanup(os.remove, p)
        self.assertEqual(len(fa.load(p)), 3)


if __name__ == "__main__":
    unittest.main()
