"""Figure for the k = 2 direction: results/k2/k2_s3a.png (about 2 minutes).

(a) Along the ray p(t) = t * p_C38 (n = 13): Boros-Prekopa bound, full LP Pbar, <= 3-run LP, S3a LP.
(b) The same curves as gaps to Pbar (log scale): BP is loose, 3 runs fail, S3a matches to solver precision.
(c) Size: S3a columns (polynomial, ~n^7) versus the 2^n states of the full LP.
"""
from fractions import Fraction as Fr
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pwbound.general import bp_value, certainty_condition, float_tight
from pwbound.runs_lp import runs_lp
from pwbound.segment_lp import s3a_columns, segment_lp
from scripts.demo_k2 import C38

OUT = Path(__file__).resolve().parent.parent / "results" / "k2"


def main():
    base = [Fr(s) for s in C38]
    ts, rows = np.unique(np.round(np.r_[np.linspace(0.6, 1.35, 16), np.linspace(0.95, 1.12, 18)], 4)), []
    for t in ts:
        p = sorted(Fr(t).limit_denominator(1000) * x for x in base)
        if certainty_condition(p, 2):
            continue
        full = float_tight(p, 2)[0]
        rows.append((t, float(bp_value(p, 2)), full, runs_lp(p, 2, 3)[0], segment_lp(p, 2, 3, one_design=True)[0]))
        print(f"t={t:.3f} Pbar={full:.8f} S3a gap={full - rows[-1][4]:.1e} 3-run gap={full - rows[-1][3]:.1e}")
    t, bp, full, r3, s3 = map(np.array, zip(*rows))

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    ax[0].plot(t, bp, "--", color="tab:gray", label="Boros–Prékopa bound")
    ax[0].plot(t, full, color="black", lw=3, alpha=0.35, label="P̄ (full LP, 2ⁿ states)")
    ax[0].plot(t, r3, ":", color="tab:red", label="≤ 3-run LP (R3′, refuted)")
    ax[0].plot(t, s3, color="tab:blue", lw=1.2, label="S3a LP (polynomial)")
    ax[0].set(xlabel="scale t  (p = t · p_C38, n = 13)", ylabel="max P(S ≥ 2)", title="(a) values")
    ax[0].legend(fontsize=8)

    floor = 1e-13
    ax[1].semilogy(t, np.maximum(bp - full, floor), "--", color="tab:gray", label="BP − P̄")
    ax[1].semilogy(t, np.maximum(full - r3, floor), ":", color="tab:red", label="P̄ − (≤3 runs)")
    ax[1].semilogy(t, np.maximum(np.abs(full - s3), floor), color="tab:blue", label="|P̄ − S3a|")
    ax[1].axhline(1e-9, color="k", lw=0.5)
    ax[1].text(t[0], 1.5e-9, "solver tolerance", fontsize=7)
    ax[1].set(xlabel="scale t", ylabel="gap (log)", title="(b) gaps to P̄")
    ax[1].legend(fontsize=8)

    ns = np.arange(4, 23)
    cols = [sum(1 for _ in s3a_columns(int(m))) for m in ns]
    ax[2].semilogy(ns, 2.0 ** ns, color="black", label="2ⁿ states (full LP)")
    ax[2].semilogy(ns, cols, "o-", color="tab:blue", ms=3, label="S3a columns")
    ax[2].set(xlabel="n", ylabel="LP size (log)", title="(c) LP size")
    ax[2].legend(fontsize=8)

    fig.suptitle("k = 2, distinct marginals: S3a segment-design LP vs exact P̄ (S3a is a conjecture)", fontsize=11)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "k2_s3a.png", dpi=150)
    print("wrote", OUT / "k2_s3a.png")


if __name__ == "__main__":
    main()
