#!/usr/bin/env python3
"""Summarize an INA219 serial capture from the Lab 0 logger sketch.

Accepts either output mode of ina219_logger.ino:
  - readable: "t= 12.0 s | Bus: 4.988 V | Shunt: 2.260 mV | ... | Current: 22.60 mA | Power: 114.00 mW"
  - CSV:      "ms,bus_V,shunt_mV,current_mA,power_mW" rows

Usage:
  python analyze_log.py data/offset.log
  python analyze_log.py data/load.log --ohms 221 --ref-volts 4.99
"""
import argparse
import re
import statistics as st
import sys

READABLE = re.compile(
    r"Bus:\s*(-?[\d.]+)\s*V.*?Shunt:\s*(-?[\d.]+)\s*mV.*?"
    r"Current:\s*(-?[\d.]+)\s*mA.*?Power:\s*(-?[\d.]+)\s*mW"
)
CSV = re.compile(r"^\s*\d+,(-?[\d.]+),(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)\s*$")


def parse(path):
    rows = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = READABLE.search(line) or CSV.match(line)
            if m:
                rows.append(tuple(float(x) for x in m.groups()))
    return rows


def summarize(name, unit, values):
    mean = st.fmean(values)
    sd = st.stdev(values) if len(values) > 1 else 0.0
    print(f"{name:<8} mean {mean:>10.3f} {unit:<3} std {sd:>8.3f}  "
          f"min {min(values):>9.3f}  max {max(values):>9.3f}  "
          f"range {max(values) - min(values):>7.3f}")
    return mean


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logfile")
    ap.add_argument("--ohms", type=float,
                    help="measured resistance of the load, to compute expected current")
    ap.add_argument("--ref-volts", type=float,
                    help="reference voltage (multimeter) to compare the INA219 bus voltage against")
    args = ap.parse_args()

    rows = parse(args.logfile)
    if len(rows) < 2:
        sys.exit("Fewer than 2 valid samples found. Check the file format.")

    bus, shunt, cur, pwr = (list(c) for c in zip(*rows))
    print(f"{len(rows)} samples from {args.logfile}\n")
    bus_mean = summarize("bus", "V", bus)
    summarize("shunt", "mV", shunt)
    cur_mean = summarize("current", "mA", cur)
    summarize("power", "mW", pwr)

    if args.ref_volts:
        err = (bus_mean - args.ref_volts) / args.ref_volts * 100
        print(f"\nBus voltage vs reference {args.ref_volts:.3f} V: {err:+.2f} %")
    if args.ohms:
        volts = args.ref_volts or bus_mean
        expected = volts / args.ohms * 1000
        err = (cur_mean - expected) / expected * 100
        print(f"Expected current {expected:.2f} mA ({volts:.3f} V / {args.ohms:g} ohm); "
              f"INA219 mean {cur_mean:.2f} mA ({err:+.2f} %)")
    if cur_mean < 0:
        print("\nNote: negative current. Vin+ and Vin- are probably swapped.")


if __name__ == "__main__":
    main()
