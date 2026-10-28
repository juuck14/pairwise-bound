"""Exact rational grid scan of which dual quadratic attains M(p, q) (exploration).

    python -m scripts.scan --n 120 [--record]

For each grid point (i/n, j/n) in [0,1]^2 it records the set of dual vertices
attaining the minimum. Grid results are exploration only: a grid can miss thin
regions, so they never establish a claim on their own.
"""
import argparse
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

from pwbound import parametric, poly
from scripts.env_report import env_report

REPO = Path(__file__).resolve().parents[1]


def classify(p, q):
    if p == 0 or q == 0 or p == 1 or q == 1:
        return "edge"
    if p == q:
        return "diagonal"
    return "inside" if p < q else "outside(p>q)"


def scan(n):
    unique = {}       # region -> Counter of vertex ids that are the unique minimizer
    attained = {}     # region -> Counter of vertex ids attaining the minimum
    for i in range(n + 1):
        for j in range(n + 1):
            p, q = Fraction(i, n), Fraction(j, n)
            region = classify(p, q)
            _, ids = parametric.minimizers(p, q)
            attained.setdefault(region, Counter()).update(ids)
            if len(ids) == 1:
                unique.setdefault(region, Counter()).update(ids)
    return unique, attained


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n", type=int, default=120)
    parser.add_argument("--record", action="store_true",
                        help="save summary and metadata under results/runs/")
    args = parser.parse_args(argv)
    start = time.perf_counter()
    unique, attained = scan(args.n)
    elapsed = time.perf_counter() - start

    verts = parametric.vertices()
    print(f"grid denominator n = {args.n}; {len(verts)} dual vertices")
    header = f"{'id':4} {'Q(p,q)':42} " + " ".join(f"{r[:12]:>12}" for r in
                                                  ("inside", "diagonal", "edge", "outside(p>q)"))
    print(header)
    for v in verts:
        cells = []
        for r in ("inside", "diagonal", "edge", "outside(p>q)"):
            cells.append(f"{unique.get(r, Counter())[v['id']]:>5}/{attained.get(r, Counter())[v['id']]:<6}")
        print(f"{v['id']:4} {poly.to_string(v['Q']):42} " + " ".join(cells))
    print("cells: (#points where unique minimizer) / (#points where attaining the minimum)")
    print(f"elapsed {elapsed:.2f}s")

    if args.record:
        out = REPO / "results" / "runs" / f"scan-n{args.n}"
        out.mkdir(parents=True, exist_ok=True)
        summary = {
            v["id"]: {
                "Q": poly.to_string(v["Q"]),
                "unique": {r: unique.get(r, Counter())[v["id"]] for r in unique},
                "attained": {r: attained.get(r, Counter())[v["id"]] for r in attained},
            }
            for v in verts
        }
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        meta = {"command": "python -m scripts.scan " + " ".join(argv or sys.argv[1:]),
                "inputs": {"n": args.n}, "seed": None, "elapsed_seconds": round(elapsed, 2),
                "environment": env_report()}
        (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(f"recorded -> {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
