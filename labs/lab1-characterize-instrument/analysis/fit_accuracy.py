#!/usr/bin/env python3
"""Fit INA219 readings against a reference (Experiments 1 and 2).

Input is a CSV with two columns, reference then measured (a header line is
allowed). Prints the slope (gain error), intercept (offset), and the largest
residual, both in the data's units and as a percent of the reference.

Usage:
  python fit_accuracy.py data/current_accuracy.csv
"""
import argparse
import sys


def load(path):
    pairs = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue
            try:
                pairs.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    return pairs


def fit(pairs):
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ValueError("Reference values are all identical; cannot fit a line.")
    slope = sum((x - mx) * (y - my) for x, y in pairs) / sxx
    intercept = my - slope * mx
    residuals = [y - (slope * x + intercept) for x, y in pairs]
    errors_pct = [(y - x) / x * 100 for x, y in pairs if x != 0]
    return {
        "n": n,
        "slope": slope,
        "intercept": intercept,
        "max_residual": max(abs(r) for r in residuals),
        "max_error_pct": max(abs(e) for e in errors_pct) if errors_pct else float("nan"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csvfile")
    args = ap.parse_args()

    pairs = load(args.csvfile)
    if len(pairs) < 3:
        sys.exit("Need at least 3 valid (reference, measured) rows.")
    r = fit(pairs)
    print(f"points             {r['n']}")
    print(f"slope              {r['slope']:.5f}   (1.00000 = no gain error)")
    print(f"intercept          {r['intercept']:.4f}   (offset, same units as the data)")
    print(f"max fit residual   {r['max_residual']:.4f}")
    print(f"max error vs ref   {r['max_error_pct']:.2f} %")


if __name__ == "__main__":
    main()
