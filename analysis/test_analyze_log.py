import os
import tempfile
import unittest

import analyze_log as al

READABLE_LINE = ("t= 316.0 s | Bus:  4.984 V | Shunt:   2.270 mV | Load:  4.986 V | "
                 "Current:    22.20 mA | Power:   112.00 mW\n")
NEGATIVE_LINE = ("t= 318.0 s | Bus:  4.856 V | Shunt:  -2.180 mV | Load:  4.854 V | "
                 "Current:   -21.80 mA | Power:   108.00 mW\n")
CSV_LINE = "1000,4.988,2.26,22.60,114.00\n"


def write_tmp(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


class ParseTests(unittest.TestCase):
    def test_readable_format(self):
        path = write_tmp(READABLE_LINE)
        self.addCleanup(os.remove, path)
        self.assertEqual(al.parse(path), [(4.984, 2.27, 22.2, 112.0)])

    def test_csv_format(self):
        path = write_tmp("ms,bus_V,shunt_mV,current_mA,power_mW\n" + CSV_LINE)
        self.addCleanup(os.remove, path)
        self.assertEqual(al.parse(path), [(4.988, 2.26, 22.6, 114.0)])

    def test_negative_values(self):
        path = write_tmp(NEGATIVE_LINE)
        self.addCleanup(os.remove, path)
        self.assertEqual(al.parse(path), [(4.856, -2.18, -21.8, 108.0)])

    def test_ignores_banner_and_noise(self):
        path = write_tmp("INA219 connected at 0x40\n-----\n" + READABLE_LINE + "garbage line\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(len(al.parse(path)), 1)


if __name__ == "__main__":
    unittest.main()
