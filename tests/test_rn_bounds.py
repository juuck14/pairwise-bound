"""Comparison with Ramachandra & Natarajan (arXiv:2006.00516 v6)."""
from fractions import Fraction as F

import pytest

from pwbound import exact_lp, model, parametric, rn_bounds as R
from pwbound.rational import rank


def grid(n, scope_only=True):
    return [(F(i, n), F(j, n)) for i in range(n + 1) for j in range(n + 1) if not scope_only or i <= j]


def test_representative_values():
    p, q = F(2, 5), F(3, 5)
    probs = R.sorted_marginals(p, q)
    terms = [R.bp_closed_form(5 - r, 3 - r, *R.partial_moments(probs, r)) for r in range(3)]
    assert terms == [F(107, 125), F(22, 25), F(73, 75)]
    assert R.union_term(p, q) == F(23, 25)
    assert R.ordered_bp_tightened(p, q) == F(107, 125) > exact_lp.envelope(p, q) == F(61, 75)


@pytest.mark.parametrize("p, q", grid(30))
def test_closed_form_matches_moment_lp_and_bounds_are_valid(p, q):
    probs = R.sorted_marginals(p, q)
    for r in range(3):
        s1, s2 = R.partial_moments(probs, r)
        assert R.bp_closed_form(5 - r, 3 - r, s1, s2) == R.bp_lp(5 - r, 3 - r, s1, s2)
    m = exact_lp.envelope(p, q)
    assert R.ordered_bp_tightened(p, q) >= m
    assert R.ordered_sss(p, q) >= R.ordered_bp(p, q)
    assert R.ordered_chebyshev(p, q) >= R.ordered_bp(p, q)


@pytest.mark.parametrize("k", range(1, 97))
def test_theorem_4_1_reproduced_on_the_diagonal(k):
    p = F(k, 97)
    assert R.identical_closed_form(p) == exact_lp.envelope(p, p)


def test_bound_is_minimum_over_finite_dual_set():
    W = R.dual_points()
    for w in W:
        assert all(model.dual_poly12(w, a, b) >= model.indicator12((a, b)) for a, b in model.STATES12)
    for p, q in grid(24):
        assert R.ordered_bp_tightened(p, q) == min(model.reduced_dual_value(w, p, q) for w in W)


def test_only_sum_only_vertices_carry_full_rank():
    """Members of W with rank-6 tight columns are exactly V02, V16, V18; the rest
    are optimal only where b(p,q) lies in a proper subspace (empty interior)."""
    ids = {v["y"]: v["id"] for v in parametric.vertices()}
    full = set()
    for w in R.dual_points():
        tight = parametric.tight_states(w)
        r = rank([model.reduced_row(*s) for s in tight]) if tight else 0
        if r == 6:
            full.add(ids[w])
        else:
            assert w not in ids
    assert full == {"V02", "V16", "V18"}


def test_tight_exactly_on_sum_only_pieces_at_witnesses():
    """At each piece's witness the bound is tight iff the piece is V02, V16 or V18."""
    import json
    from conftest import REPO
    cert = json.loads((REPO / "results" / "regions" / "region_certificate.json").read_text())
    for a in cert["active"]:
        p, q = (F(x) for x in a["witness"])
        tight = R.ordered_bp_tightened(p, q) == exact_lp.envelope(p, q)
        assert tight == (a["id"] in {"V02", "V16", "V18"}), a["id"]


def test_non_vertex_two_moment_dual_is_convex_combination_of_v10_v11():
    y10 = parametric.vertex_by_id("V10")["y"]
    y11 = parametric.vertex_by_id("V11")["y"]
    combo = tuple(F(3, 5) * a + F(2, 5) * b for a, b in zip(y10, y11))
    assert combo in R.dual_points()
    assert combo == R._symmetrize(0, {i: F(7, 15) for i in range(5)},
                                  {(i, j): F(-2, 15) for i in range(5) for j in range(i + 1, 5)})


SUMMARY_TABLE = {   # notes/proofs/theorem_AB.md, as {(i, j): coefficient of p^i q^j}
    "V02": {(2, 0): F(1, 3), (1, 1): 2, (0, 2): 1},
    "V16": {(0, 0): 1, (1, 0): -2, (0, 1): -3, (2, 0): 1, (1, 1): 6, (0, 2): 3},
    "V18": {(0, 0): 1},
    "V12": {(1, 0): 2, (2, 0): F(-2, 3), (0, 2): 1, (1, 1): -1},
    "V10": {(1, 0): F(2, 3), (0, 1): F(5, 3), (1, 1): F(-2, 3), (0, 2): F(-2, 3)},
    "V11": {(1, 0): F(4, 3), (0, 1): 1, (2, 0): F(-1, 3), (1, 1): -1},
    "V14": {(1, 0): F(8, 3), (0, 2): 1, (2, 0): F(-2, 3), (1, 1): -2},
    "V15": {(1, 0): 4, (0, 2): 1, (1, 1): -4},
    "V19": {(0, 0): 1, (1, 0): 2, (0, 1): -3, (2, 0): -1, (0, 2): 3},
    "V20": {(0, 0): 1, (1, 0): 4, (0, 1): -3, (2, 0): -1, (1, 1): -3, (0, 2): 3},
    "V21": {(0, 0): 1, (1, 0): 6, (0, 1): -3, (1, 1): -6, (0, 2): 3},
}


@pytest.mark.parametrize("vid", sorted(SUMMARY_TABLE))
def test_summary_table_formulas(vid):
    assert parametric.vertex_by_id(vid)["Q"] == {m: F(c) for m, c in SUMMARY_TABLE[vid].items()}
