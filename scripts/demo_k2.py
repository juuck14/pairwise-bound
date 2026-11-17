"""Demo of the current research direction: k = 2, distinct marginals (R-N open problem (a)).

Pbar(n,2,p) = max P(X_1+...+X_n >= 2) over pairwise independent Bernoulli laws with marginals p.

Compares, at one point:
  - the Boros-Prekopa two-moment bound (closed form, not tight in general),
  - the full LP over all 2^n states (exact but exponential),
  - the "<= 3 runs" LP (an earlier hypothesis R3', refuted: claim C38),
  - the S3a segment-design LP (polynomially many columns; conjectured exact when Pbar < 1),
and then certifies, in rational arithmetic, that S3a reaches Pbar at this point:
an exact quadratic certificate q >= 1{|x|>=2} on all 2^n states gives Pbar <= U, and an exact
mixture of S3a columns gives a law with value U.

Run:  python -m scripts.demo_k2                         (default: the C38 point, n = 13, ~15 s)
      python -m scripts.demo_k2 --p 0.01,0.02,0.03,0.05,0.3,0.3,0.3,0.3,0.3
"""
import argparse
import time
from fractions import Fraction as Fr

from pwbound.general import bp_value, certainty_condition, float_tight
from pwbound.runs_lp import runs_lp
from pwbound.segment_lp import s3a_columns, segment_lp

C38 = ["0.0219"] * 6 + ["0.0259", "0.0278", "0.0288", "0.0398", "0.3486", "0.3688", "0.4033"]


def timed(f, *a, **kw):
    t = time.time()
    out = f(*a, **kw)
    return out, time.time() - t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--p", default=",".join(C38), help="comma-separated decimals or fractions (n <= 16)")
    ap.add_argument("--no-exact", action="store_true", help="skip the rational certificate step")
    args = ap.parse_args()
    p = sorted(Fr(s) for s in args.p.split(","))
    n = len(p)
    if n > 16:
        raise SystemExit("the full 2^n LP is used for comparison; keep n <= 16")

    print(f"n = {n}, k = 2, sorted marginals p = {[str(x) for x in p]}")
    print(f"S1 = sum p = {float(sum(p)):.6f}")
    if certainty_condition(p, 2):
        print("Theorem C4: every leave-one-out sum is >= 2, so Pbar = 1 (nothing to optimise).")
        return

    bp, _ = timed(bp_value, p, 2)
    print(f"\n[1] Boros-Prekopa bound (closed form)          {float(bp):.10f}")
    (full, _), t_full = timed(float_tight, p, 2)
    print(f"[2] full LP over 2^{n} = {2 ** n} states (HiGHS)    {full:.10f}   ({t_full:.1f} s)")
    (r3, _), t_r3 = timed(runs_lp, p, 2, 3)
    print(f"[3] <= 3-run LP (refuted hypothesis R3')        {r3:.10f}   gap to [2] = {full - r3:.2e}")
    ncol = sum(1 for _ in s3a_columns(n))
    (s3a, w), t_s3a = timed(segment_lp, p, 2, 3, one_design=True)
    print(f"[4] S3a segment-design LP ({ncol} columns)  {s3a:.10f}   gap to [2] = {full - s3a:.2e}"
          f"   ({t_s3a:.1f} s)")
    print("    columns used (intervals [a,b] in sorted order, c = number of ones drawn uniformly):")
    for segs, wt in sorted(w.items(), key=lambda kv: -kv[1])[:8]:
        desc = " + ".join(f"[{a + 1}..{b + 1}]" + ("" if c == b - a + 1 else f" choose {c}") for a, b, c in segs)
        print(f"      {wt:.6f}  {desc or '(all zero)'}")
    if len(w) > 8:
        print(f"      ... {len(w) - 8} more")

    if args.no_exact:
        return
    from scripts.verify_k2_aggregation_counterexamples import exact_optimal_dual, exact_s3a_value
    print("\n[5] exact (rational) check")
    (U, ok, _), t_u = timed(exact_optimal_dual, p)
    if U is None or not ok:
        print("    could not extract an exact certificate at this point (numerical support issue)")
        return
    print(f"    certificate q >= 1{{|x|>=2}} checked on all {2 ** n} states: Pbar <= {U}   ({t_u:.1f} s)")
    S, t_s = timed(exact_s3a_value, p)
    print(f"    exact mixture of S3a columns attains          {S}   ({t_s:.1f} s)")
    print(f"    VERDICT: S3a = Pbar exactly at this point: {S == U}")


if __name__ == "__main__":
    main()
