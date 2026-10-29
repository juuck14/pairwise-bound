"""Slice q = 3/5: exact M(p, 3/5) against the best prior bound and mutual independence.

    python -m scripts.plot_slice

Writes results/regions/slice_q3_5.png. Values are computed exactly (Fractions)
and plotted as floats. Along this slice the ordered bound of Ramachandra and
Natarajan (Theorem 3.1(b) with section 3.2) coincides with the unordered
two-moment bound, so they are drawn as one curve (checked in tests).
"""
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pwbound import exact_lp, model, rn_bounds

REPO = Path(__file__).resolve().parents[1]
Q = Fraction(3, 5)
N = 240
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
EXACT, BOUND, INDEP = "#2a78d6", "#eb6834", "#1baf7a"
# exact piece transitions along q = 3/5 (sympy, see notes/presentation_content.md)
TRANSITIONS = [((21 ** 0.5 - 3) / 10, "V16 | V02"), (0.2, "V02 | V12"), (1 - 7 ** 0.5 / 5, "V12 | V11")]
PIECES = [(0.079, "V16"), (0.179, "V02"), (0.335, "V12"), (0.535, "V11")]


def series():
    ps, exact, bound, indep = [], [], [], []
    for i in range(N + 1):
        p = Q * i / N
        ps.append(float(p))
        exact.append(float(exact_lp.envelope(p, Q)))
        bound.append(float(rn_bounds.ordered_bp_tightened(p, Q)))
        indep.append(float(sum(v for x, v in model.product_distribution(p, Q).items() if sum(x) >= 3)))
    return ps, exact, bound, indep


def main():
    ps, exact, bound, indep = series()
    fig, ax = plt.subplots(figsize=(7.6, 4.8), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for x, _ in TRANSITIONS:
        ax.axvline(x, color=GRID, linewidth=1.0, zorder=0)
    for x, name in PIECES:
        ax.text(x, 1.005, name, ha="center", va="bottom", fontsize=8, color=MUTED)
    ax.plot(ps, bound, color=BOUND, linewidth=2, label="Best prior bound (Ramachandra-Natarajan)")
    ax.plot(ps, exact, color=EXACT, linewidth=2, label="Exact maximum M(p, 3/5)")
    ax.plot(ps, indep, color=INDEP, linewidth=2, label="Mutual independence")
    end = len(ps) - 1
    ax.text(ps[end] + 0.008, indep[end], "mutual\nindependence", fontsize=8, color=INK, va="center")
    ax.annotate("prior bound", xy=(0.36, bound[int(0.36 / 0.6 * N)]), xytext=(0.255, 0.93),
                fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.8))
    ax.annotate("exact M", xy=(0.36, exact[int(0.36 / 0.6 * N)]), xytext=(0.40, 0.70),
                fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.8))
    k = int(0.4 / 0.6 * N)
    ax.plot([0.4], [exact[k]], marker="o", markersize=7, color=EXACT, markeredgecolor=SURFACE,
            markeredgewidth=2, zorder=5)
    ax.plot([0.4], [bound[k]], marker="o", markersize=7, color=BOUND, markeredgecolor=SURFACE,
            markeredgewidth=2, zorder=5)
    ax.text(0.41, exact[k] - 0.035, "61/75", fontsize=8, color=INK)
    ax.text(0.41, bound[k] + 0.012, "107/125", fontsize=8, color=INK)
    ax.set_xlim(0, 0.6)
    ax.set_ylim(0.15, 1.0)
    ax.set_xlabel("p   (q = 3/5 fixed)", color=INK)
    ax.set_ylabel("max P(X1+...+X5 >= 3)", color=INK)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    ax.set_title("Slice q = 3/5: the prior bound is exact only on pieces V16, V02 (and at p = q)",
                 fontsize=9.5, color=INK, loc="left", pad=16)
    out = REPO / "results" / "regions" / "slice_q3_5.png"
    fig.savefig(out, bbox_inches="tight", facecolor=SURFACE)
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
