"""Exactness of the two-moment (Boros-Prekopa) bound for general marginals.

Statements: notes/proofs/exactness.md. Exact tests use Fractions; tests marked
"float" use HiGHS only to cross-check a criterion on random instances.
"""
import json
import random
from fractions import Fraction as F
from itertools import combinations
from math import comb

import pytest

from pwbound import exact_lp, general as G


def exceptional(n, K):
    """Theorem L1: the 3-layer unions whose moment vectors do NOT span (n >= 4)."""
    K = set(K)
    return (min(K) == 0 and max(K) == n and len(K - {0, n}) == 1 and 2 <= min(K - {0, n}) <= n - 2) \
        or K <= {0, 1, n - 1, n}


@pytest.mark.parametrize("n", [4, 5, 6, 7])
def test_layer_kernel_classification(n):
    for K in combinations(range(n + 1), 3):
        d = G.layer_kernel_dim(n, K)
        assert (d == 0) == (not exceptional(n, K)), (n, K, d)
    for s in range(2, n - 1):               # rigidity count of {0, s, n}
        assert G.layer_kernel_dim(n, (0, s, n)) == n - 1


def test_conditional_mean_identity_on_an_exact_law():
    p = [F(2, 5), F(2, 5), F(3, 5), F(3, 5), F(3, 5)]
    from pwbound import model, cert
    data = json.loads(open(cert.__file__.replace("src/pwbound/cert.py", "results/certificates/p2_5-q3_5.json")).read())
    law = {tuple(int(c) for c in key): F(v) for key, v in data["primal"]["lifted"].items()}
    G.verify_law(p, law)
    loo = G.leave_one_out(p)
    for j in range(5):
        on = sum(w for x, w in law.items() if x[j])
        assert sum(w * sum(x) for x, w in law.items() if x[j]) / on == 1 + loo[j]
        assert sum(w * sum(x) for x, w in law.items() if not x[j]) / (1 - on) == loo[j]


def test_rigidity_line_in_the_two_three_family():
    """E3: in the {0,3,5} regime the bound can be exact for p != q only on p + 2q = 2."""
    p, q = F(1, 2), F(3, 4)
    marg = [p, p, q, q, q]
    bp, laws = G.bp_optimum(5, 3, *G.moments(marg))
    assert [sorted(l) for l in laws] == [[0, 3, 5]]
    assert bp == exact_lp.envelope(p, q) == F(23, 24)
    assert G.bp_exactness_verdict(marg, 3)[1] == "open"
    p, q = F(2, 5), F(3, 5)                 # representative point, off the line
    v = G.bp_exactness_verdict([p, p, q, q, q], 3)
    assert v[1] == "not exact" and v[2].startswith("E3")


EXPECTED_PIECES = {"V02": "open", "V16": "open", "V18": "open", "V10": "E3", "V11": "E3", "V12": "E3",
                   "V14": "E3", "V21": "E3", "V19": "E2", "V20": "E2",
                   # the V15 witness (4/11, 9/11) lies on the E3 line p + 2q = 2; there the
                   # layer-3 measure would need P(X1=X2=1) = 16/121 >= P(all ones) = 18/121
                   "V15": "E4"}


def test_two_three_pieces_explained_by_criteria():
    """Corollary C(i) from the general criteria: at each piece witness, BP is exact
    (V02, V16, V18) or a necessary condition fails, and which one."""
    from conftest import REPO
    cert_ = json.loads((REPO / "results" / "regions" / "region_certificate.json").read_text())
    for a in cert_["active"]:
        p, q = (F(x) for x in a["witness"])
        bp, verdict, reason = G.bp_exactness_verdict([p, p, q, q, q], 3)
        want = EXPECTED_PIECES[a["id"]]
        if want == "open":
            assert verdict == "open" and bp == exact_lp.envelope(p, q), a["id"]
        else:
            assert verdict == "not exact" and reason.startswith(want), (a["id"], reason)


def quadratic_certificate(p, layers, h0, h1, h2):
    """Exact Farkas check: h = h0 + sum h1_i x_i + sum h2_ij x_i x_j is >= 0 on the layers,
    and its expectation under any pairwise independent law with marginals p is returned."""
    n = len(p)
    for s in layers:
        for ones in combinations(range(n), s):
            val = h0 + sum(h1[i] for i in ones) + sum(h2.get((i, j), 0) for i, j in combinations(ones, 2))
            assert val >= 0, (ones, val)
    return h0 + sum(h1[i] * p[i] for i in range(n)) + sum(c * p[i] * p[j] for (i, j), c in h2.items())


def test_interval_condition_is_not_sufficient():
    """E2 holds but BP is not exact: obstruction h = (A - 1)(1 - B), A = X1 + X2, B = X3 + X4."""
    p = [F(13, 20), F(19, 50), F(3, 4), F(17, 50)]
    bp, verdict, _ = G.bp_exactness_verdict(p, 3)
    assert bp == F(5047, 10000) and verdict == "open"
    assert [sorted(l) for l in G.bp_optimum(4, 3, *G.moments(p))[1]] == [[1, 2, 3]]
    h2 = {(0, 2): -1, (0, 3): -1, (1, 2): -1, (1, 3): -1}
    assert quadratic_certificate(p, (1, 2, 3), F(-1), [1, 1, 1, 1], h2) == F(-27, 10000)


def test_two_group_split_conditions_are_not_sufficient():
    """E2 and every 2-partition test pass, yet BP is not exact (n = 5, k = 4); obstruction
    h = 3(x1 x5 + x2 x3) - (S-1)(S-2)/2 (the matching {1,5},{2,3} meets every 4-set)."""
    p = [F(29, 100), F(2, 5), F(13, 25), F(23, 25), F(33, 50)]
    bp, verdict, _ = G.bp_exactness_verdict(p, 4)
    assert bp == F(6019, 15000) and verdict == "open"
    K = sorted(G.bp_optimum(5, 4, *G.moments(p))[1][0])
    assert K == [1, 2, 4]
    # -(S-1)(S-2)/2 = -1 + S - sum_{i<j} x_i x_j  (multilinear form)
    h2 = {(i, j): F(-1) for i, j in combinations(range(5), 2)}
    h2[(0, 4)] += 3
    h2[(1, 2)] += 3
    assert quadratic_certificate(p, K, F(-1), [1] * 5, h2) == F(-7, 1250)
    # float: every two-group aggregated (A,B) problem on {a + b in K} is feasible
    import numpy as np
    from scipy.optimize import linprog
    pf = [float(x) for x in p]
    for r in (1, 2):
        for G1 in combinations(range(5), r):
            G2 = [i for i in range(5) if i not in G1]
            a1, b1 = sum(pf[i] for i in G1), sum(pf[i] for i in G2)
            a2 = 2 * sum(pf[i] * pf[j] for i, j in combinations(G1, 2))
            b2 = 2 * sum(pf[i] * pf[j] for i, j in combinations(G2, 2))
            pts = [(a, b) for a in range(len(G1) + 1) for b in range(len(G2) + 1) if a + b in K]
            A = np.array([[1] * len(pts), [a for a, _ in pts], [b for _, b in pts],
                          [a * (a - 1) for a, _ in pts], [b * (b - 1) for _, b in pts], [a * b for a, b in pts]], float)
            rhs = np.array([1, a1, b1, a2, b2, a1 * b1])
            assert linprog(np.zeros(len(pts)), A_eq=A, b_eq=rhs, bounds=(0, None), method="highs").status == 0


def test_petersen_formula_for_second_moment_term():
    """n = 5, k = 3: the K_3-decomposition of (p_i p_j) is unique,
    rho(T) = (w(T) + w(T^c) - S2/3) / 2; for (p,p,q,q,q) it gives the V02 law."""
    p_, q_ = F(1, 4), F(1, 2)
    p = [p_, p_, q_, q_, q_]
    s2 = G.moments(p)[1]
    w = {(i, j): p[i] * p[j] for i, j in combinations(range(5), 2)}
    rho = {}
    for T in combinations(range(5), 3):
        comp = tuple(i for i in range(5) if i not in T)
        rho[T] = (sum(w[e] for e in combinations(T, 2)) + w[comp] - s2 / 3) / 2
    for (i, j), wij in w.items():
        assert sum(r for T, r in rho.items() if i in T and j in T) == wij
    assert rho[(2, 3, 4)] == (p_**2 - 3 * p_ * q_ + 3 * q_**2) / 3
    assert rho[(0, 1, 2)] == p_**2 / 3 and rho[(0, 2, 3)] == p_ * (3 * q_ - p_) / 6


def random_rational(rng, lo=1, hi=99, den=100):
    return F(rng.randint(lo, hi), den)


def test_top2_complement_law_is_exact_and_certain():
    """Theorem C(k = n-2): explicit law with S >= n-2 whenever all leave-one-out sums >= n-2."""
    rng = random.Random(20261029)
    made = 0
    for _ in range(400):
        n = rng.randint(3, 7)
        p = [random_rational(rng, 40, 99) for _ in range(n)]
        cond = all(s >= n - 2 for s, x in zip(G.leave_one_out(p), p) if x < 1)
        law = G.top2_complement_law(p)
        assert (law is not None) == cond
        if law is not None:
            s_law = G.verify_law(p, law)
            assert min(s_law) >= n - 2
            made += 1
    assert made > 20


def certain_feasible(p, k):
    value, _ = G.float_tight(p, k, states_filter=lambda x: sum(x) >= k)
    return value is not None


def test_certainty_criterion_float():
    """float: P(n,k,p) = 1 iff sum_{l != j} p_l >= k for all j with p_j < 1 (Conjecture C;
    necessity is Theorem C1). Points within 1e-3 of the boundary are skipped."""
    rng = random.Random(7)
    checked = 0
    for _ in range(600):
        n = rng.randint(4, 6)
        k = rng.randint(1, n - 1)
        p = [rng.random() ** rng.choice([0.3, 1.0]) for _ in range(n)]
        loo = min(sum(p) - x for x in p)
        if abs(loo - k) < 1e-3:
            continue
        assert certain_feasible(p, k) == (loo >= k), (n, k, p)
        checked += 1
    assert checked > 400


def test_second_moment_term_exactness_float():
    """float: P(n,k,p) = S2 / C(k,2) iff a pairwise independent law lives on layers {0,1,k},
    and condition (I) sum_{l != j} p_l <= k - 1 is necessary (Theorem S)."""
    rng = random.Random(11)
    hits = 0
    for _ in range(300):
        n = rng.randint(4, 6)
        k = rng.randint(2, n)
        p = [rng.random() ** rng.choice([0.5, 1, 2]) * rng.choice([0.3, 0.6, 1.0]) for _ in range(n)]
        s1, s2 = (float(x) for x in G.moments(p))
        target = s2 / comb(k, 2)
        tight, _ = G.float_tight(p, k)
        exact = abs(tight - target) < 1e-9
        layered = G.float_tight(p, k, states_filter=lambda x: sum(x) in (0, 1, k))[0] is not None
        assert exact == layered, (n, k, p)
        if exact:
            hits += 1
            assert all(sum(p) - x <= k - 1 + 1e-12 for x in p)
    assert hits > 20


def test_monotonicity_float():
    """Lemma M: P(n,k,p) is nondecreasing in each coordinate."""
    rng = random.Random(13)
    for _ in range(80):
        n = rng.randint(3, 6)
        k = rng.randint(1, n)
        p = [rng.random() for _ in range(n)]
        j = rng.randrange(n)
        p2 = list(p)
        p2[j] = p[j] + (1 - p[j]) * rng.random()
        assert G.float_tight(p2, k)[0] >= G.float_tight(p, k)[0] - 1e-9


def test_rn_example_3_2_verdicts():
    """Every BP cell of R-N Example 3.2 is decided with an exact certificate."""
    from scripts.explain_rn_example import analyse
    rows = [analyse(k) for k in range(1, 13)]
    unordered_exact = [r["k"] for r in rows if r["unordered"][1] == "exact"]
    ordered_exact = [r["k"] for r in rows if r["ordered"][1] == "exact"]
    assert unordered_exact == [1, 2, 3, 4, 7, 8]
    assert ordered_exact == [1, 2, 3, 4, 7, 8, 9, 12]
    for r in rows:
        assert r["unordered"][1] in ("exact", "not exact")
        assert r["ordered"][1] in ("exact", "not exact")
