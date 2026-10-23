#!/usr/bin/env python3
"""Summarize a Lab 1 capture from ina219_characterize.ino.

Input lines look like:  label,i,t_us,bus_V,shunt_mV,current_mA,ovf
Lines starting with '#', the header, and 'timeout' lines are ignored.

For each label (for example pg3_adc3) the script prints the number of samples,
the sample rate, and the mean, standard deviation and range of the current.
Noise is also shown in counts (one count = 10 microvolts across the shunt).

Usage:
  python analyze_lab1.py data/averaging_sweep.csv
"""
import argparse
import statistics as st
import sys

SHUNT_LSB_MV = 0.01  # 10 microvolts per count


def parse(path):
    groups = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("label,"):
                continue
            parts = line.split(",")
            if len(parts) != 7:
                continue
            try:
                label = parts[0]
                t_us = float(parts[2])
                bus_v = float(parts[3])
                shunt_mv = float(parts[4])
                cur_ma = float(parts[5])
                ovf = int(parts[6])
            except ValueError:
                continue
            groups.setdefault(label, []).append((t_us, bus_v, shunt_mv, cur_ma, ovf))
    return groups


def summarize(rows):
    n = len(rows)
    times = [r[0] for r in rows]
    dts = [b - a for a, b in zip(times, times[1:]) if b > a]
    rate = 1e6 / st.median(dts) if dts else float("nan")
    cur = [r[3] for r in rows]
    shunt = [r[2] for r in rows]
    sd = st.stdev(cur) if n > 1 else 0.0
    sd_shunt = st.stdev(shunt) if n > 1 else 0.0
    return {
        "n": n,
        "rate_hz": rate,
        "mean_ma": st.fmean(cur),
        "std_ma": sd,
        "std_counts": sd_shunt / SHUNT_LSB_MV,
        "range_ma": max(cur) - min(cur),
        "ovf": sum(r[4] for r in rows),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csvfile")
    args = ap.parse_args()

    groups = parse(args.csvfile)
    if not groups:
        sys.exit("No valid samples found. Check the file format.")

    print(f"{'label':<12}{'n':>6}{'rate Hz':>10}{'mean mA':>10}{'std mA':>9}"
          f"{'std cnt':>9}{'range mA':>10}{'ovf':>5}")
    for label, rows in groups.items():
        s = summarize(rows)
        print(f"{label:<12}{s['n']:>6}{s['rate_hz']:>10.1f}{s['mean_ma']:>10.2f}"
              f"{s['std_ma']:>9.3f}{s['std_counts']:>9.2f}{s['range_ma']:>10.2f}{s['ovf']:>5}")


if __name__ == "__main__":
    main()
