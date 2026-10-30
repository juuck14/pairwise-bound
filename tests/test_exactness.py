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


def test_theorem_s_law_is_exact():
    """Theorem S constructively: k = 2 with rho_ij = p_i p_j, and n = 5, k = 3 with the
    Petersen formula; when (I)-(III) hold the law is exact and P(S >= k) = S2 / C(k,2)."""
    rng = random.Random(29)
    built = {2: 0, 3: 0}
    for _ in range(300):
        n = 5
        p = [F(rng.randint(1, 60), 100) for _ in range(n)]
        s1, s2 = G.moments(p)
        cond_I = all(x == 0 or l <= 1 for x, l in zip(p, G.leave_one_out(p)))
        law = G.second_moment_layer_law(p, 2, {(i, j): p[i] * p[j] for i, j in combinations(range(n), 2)})
        assert (law is not None) == cond_I
        if law is not None:
            s_law = G.verify_law(p, law)
            assert set(s_law) <= {0, 1, 2} and G.tail(s_law, 2) == s2
            built[2] += 1
        w = {(i, j): p[i] * p[j] for i, j in combinations(range(n), 2)}
        rho = {}
        for T in combinations(range(n), 3):
            comp = tuple(i for i in range(n) if i not in T)
            rho[T] = (sum(w[e] for e in combinations(T, 2)) + w[comp] - s2 / 3) / 2
        law = G.second_moment_layer_law(p, 3, rho)
        cond = (all(x == 0 or l <= 2 for x, l in zip(p, G.leave_one_out(p)))
                and min(rho.values()) >= 0 and 1 - s1 + 2 * s2 / 3 >= 0)
        assert (law is not None) == cond
        if law is not None:
            s_law = G.verify_law(p, law)
            assert set(s_law) <= {0, 1, 3} and G.tail(s_law, 3) == s2 / 3
            built[3] += 1
    assert built[2] > 20 and built[3] > 20


@pytest.mark.parametrize("n, k, pbar", [(6, 3, F(1, 5)), (6, 5, F(1, 2)), (6, 3, F(7, 10)), (5, 3, F(4, 5))])
def test_local_robustness_near_identical_marginals_float(n, k, pbar):
    """Theorem L(a), float: for non-exceptional identical-marginal supports, small
    heterogeneous perturbations keep the bound exact."""
    bp, laws = G.bp_optimum(n, k, *G.moments([pbar] * n))
    K = sorted(laws[0]) if bp < 1 else None
    if K is not None:
        assert G.layer_kernel_dim(n, K) == 0
    rng = random.Random(n * 100 + k)
    for _ in range(5):
        p = [float(pbar) + 0.004 * (rng.random() - 0.5) for _ in range(n)]
        s1, s2 = (float(x) for x in G.moments(p))
        bp_f = float(G.bp_optimum(n, k, *G.moments([F(x) for x in p]))[0])
        assert abs(G.float_tight(p, k)[0] - bp_f) < 1e-8


def test_proposition_g_gap_lower_bound():
    """Proposition G: in the {0,k,n} regime, BP - P >= max_j |Delta_j| / kappa(n,k).
    Exact on the 2+3 pieces whose witnesses are in that regime; kappa(5,3) = 12."""
    assert G.rigidity_constant(5, 3) == 12
    from conftest import REPO
    cert_ = json.loads((REPO / "results" / "regions" / "region_certificate.json").read_text())
    checked = 0
    for a in cert_["active"]:
        p, q = (F(x) for x in a["witness"])
        marg = [p, p, q, q, q]
        bp, laws = G.bp_optimum(5, 3, *G.moments(marg))
        if [sorted(l) for l in laws] != [[0, 3, 5]]:
            continue
        gap = bp - exact_lp.envelope(p, q)
        assert gap >= G.rigidity_gap_lower_bound(marg, 3) > 0 or (gap > 0 and a["id"] == "V15")
        checked += 1
    assert checked == 6
    # representative point: gap 107/125 - 61/75 = 16/375, bound (6/125)/12 = 1/250
    marg = [F(2, 5)] * 2 + [F(3, 5)] * 3
    assert G.rigidity_defects(marg, 3) == [F(6, 125)] * 2 + [F(-4, 125)] * 3
    assert G.rigidity_gap_lower_bound(marg, 3) == F(1, 250)


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


# ---------------------------------------------------------------- Theorem C4 / Proposition C5

def test_peeling_curve_lemma():
    """Lemma P1: f_s(y) = (1-y)(b-sy). Exact identities y_{b^2}(a) = a/b and
    f_s(a/sqrt s) - f_1(a) = a (1 - sqrt s)(1 - b/sqrt s); float check of a <= y <= a/sqrt s."""
    import sympy as sp
    a_, b_, r_ = sp.symbols("a b r", positive=True)          # r = sqrt(s)
    f = lambda y, s: (1 - y) * (b_ - s * y)
    assert sp.expand(f(a_ / b_, b_ ** 2) - f(a_, 1)) == 0
    assert sp.expand(f(a_ / r_, r_ ** 2) - f(a_, 1) - a_ * (1 - r_) * (1 - b_ / r_)) == 0
    rng = random.Random(30)
    for _ in range(2000):
        b = rng.uniform(0.05, 0.999)
        s = b * b * rng.random()
        a = b * rng.random()
        y = G.peeling_y(s, b, a)
        assert abs((1 - y) * (b - s * y) - (1 - a) * (b - a)) < 1e-12
        assert a - 1e-12 <= y <= min(1.0, a / s ** 0.5) + 1e-12


def test_peeling_phi_at_b_squared():
    """Lemma P2: at s = b^2, y_i = a_i/b, hence Phi(b^2) = (k-1)(1-b)/b (exact)."""
    rng = random.Random(31)
    checked = 0
    for _ in range(200):
        n = rng.randint(4, 9)
        k = rng.randint(1, n - 2)
        p = [random_rational(rng, 1, 99) for _ in range(n)]
        red = G.minimal_point_below(p, k)
        if red is None or red[1] is None:
            continue
        _, pm, km = red
        b = max(pm)
        B = [x for x in pm if x == b]
        assert len(B) >= 2 and sum(pm) - b == km
        phi = sum(x / b for x in pm if x != b) - (km - len(B) + b / b ** 2)
        assert phi == (km - 1) * (1 - b) / b
        checked += 1
    assert checked > 50


@pytest.mark.parametrize("alpha,b", [(3, F(3, 4)), (3, F(2, 3)), (4, F(1, 2)), (5, F(9, 10)),
                                     (6, F(3, 5)), (7, F(1, 2))])
def test_theorem_c4_exact_two_valued(alpha, b):
    """Theorem C4 on exact instances (|B| = 2, alpha coordinates a = (2-b)/alpha): the peeling
    law is a pairwise independent law with S >= 2 a.s., and s <= b^2."""
    p, s, z = G.two_valued_k2_instance(alpha, b)
    assert sum(p) - b == 2 and max(p[2:]) < b
    assert 0 < s <= b * b
    for a, y in zip(p[2:], z[2:]):                          # Lemma P1 equation, exactly
        assert (1 - y) * (b - s * y) == (1 - a) * (b - a)
    assert sum(z[2:]) == 2 - 2 + b / s                      # Lemma P2 equation, exactly
    s_law = G.verify_law(p, G.peeling_law_k2(p, s, z))
    assert min(s_law) >= 2


def test_theorem_c4_float_random():
    """float: at random points satisfying the k = 2 condition, the reduced minimal point
    carries the peeling law with S >= 2 a.s. (moments to 1e-12)."""
    rng = random.Random(20261030)
    checked = 0
    for _ in range(300):
        n = rng.randint(5, 9)
        p = [F(rng.randint(1, 99), 100) for _ in range(n)]
        red = G.minimal_point_below(p, 2)
        if red is None or red[1] is None or red[2] != 2:
            continue
        pm = red[1]
        B, A, b, s, z = G.peeling_parameters(pm, 2)
        assert len(B) >= 2 and s <= b * b
        pf = [float(x) for x in pm]
        law = G.peeling_law_k2(pf, s, z)
        assert min(law.values()) >= -1e-13 and all(sum(x) >= 2 for x in law)
        m = len(pf)
        assert abs(sum(law.values()) - 1) < 1e-12
        for i in range(m):
            assert abs(sum(w for x, w in law.items() if x[i]) - pf[i]) < 1e-12
        for i, j in combinations(range(m), 2):
            assert abs(sum(w for x, w in law.items() if x[i] and x[j]) - pf[i] * pf[j]) < 1e-12
        checked += 1
    assert checked > 150


def test_peeling_design_moments_consistency_float():
    """Proposition C5 for any k: the moments of D satisfy sum pi = k, the k-design row sums
    sum_t Pi_lt = (k-1) pi_l, and every 2x2 table of D is nonnegative."""
    rng = random.Random(32)
    checked = 0
    for _ in range(300):
        n = rng.randint(5, 10)
        k = rng.randint(2, n - 2)
        p = [F(rng.randint(30, 99), 100) for _ in range(n)]
        red = G.minimal_point_below(p, k)
        if red is None or red[1] is None or red[2] < 2:
            continue
        pm, km = red[1], red[2]
        B, A, b, s, z = G.peeling_parameters(pm, km)
        pf = [float(x) for x in pm]
        pi, Pi = G.peeling_design_moments(pf, s, z)
        m = len(pf)
        assert abs(sum(pi) - km) < 1e-9
        for l in range(m):
            row = sum(Pi[tuple(sorted((l, t)))] for t in range(m) if t != l)
            assert abs(row - (km - 1) * pi[l]) < 1e-9
        for (l, t), w in Pi.items():
            assert min(w, pi[l] - w, pi[t] - w, 1 - pi[l] - pi[t] + w) >= -1e-12
        # the residual R exists by induction: z_A satisfies the certainty condition for k - |B|
        assert all(sum(z[i] for i in A) - z[i] >= km - len(B) - 1e-9 for i in A)
        checked += 1
    assert checked > 120


def test_two_valued_design_window_float():
    """Proposition C7 (float): at two-valued minimal points the root s of Phi satisfies the
    1-D conditions (I), (II), equivalently the symmetric k-design D exists."""
    import math
    rng = random.Random(33)
    checked = 0
    for _ in range(3000):
        alpha, beta = rng.randint(1, 10), rng.randint(2, 10)
        n = alpha + beta
        k = rng.randint(1, n - 1)
        lo_b, hi_b = k / (n - 1), min(0.9999, k / (beta - 1))
        if lo_b >= hi_b:
            continue
        b = rng.uniform(lo_b, hi_b)
        a = (k - (beta - 1) * b) / alpha
        if not 0 <= a < b:
            continue
        _, _, _, s, _ = G.peeling_parameters([b] * beta + [a] * alpha, k)
        L, U = max(0, k - alpha), min(k, beta)
        Epi = lambda g: beta * (beta - 1) * b * b * g[2] + beta * b * g[1] + g[0]   # g = (c0, c1, c2): c0 + c1 B + c2 B(B-1)
        for j in range(L, U):                                                     # (II)
            g = (j * (j + 1), -2 * j, 1)
            assert Epi(g) - s * (beta - j) * (beta - j - 1) >= -1e-9
        g = (-L * U, L + U - 1, -1)                                               # (I): (B-L)(U-B)
        assert Epi(g) + s * (beta - L) * (beta - U) >= -1e-9
        checked += 1
    assert checked > 1500


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
