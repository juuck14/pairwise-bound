"""Exploration checks for the grouped-moment LPs (pwbound.aggregation). Float evidence only."""
import random

from pwbound import aggregation as AG, general as G


def test_one_group_is_boros_prekopa_and_singletons_are_exact():
    rng = random.Random(1)
    for _ in range(10):
        n, k = 5, rng.randint(1, 4)
        p = [rng.random() for _ in range(n)]
        one = AG.aggregated_bound(p, [list(range(n))], k)
        assert abs(one - min(1.0, float(G.bp_value([round(x, 12) for x in p], k)))) < 1e-6
        tight, _ = G.float_tight(p, k)
        assert abs(AG.aggregated_bound(p, [[i] for i in range(n)], k) - tight) < 1e-7


def test_k1_two_contiguous_groups_reproduce_khw():
    """k = 1: pivot (largest p) + rest reproduces R-N Theorem 2.3 (Kounias-Hunter-Worsley)."""
    rng = random.Random(2)
    for _ in range(15):
        p = sorted(rng.random() ** 2 for _ in range(6))
        khw = min(1.0, sum(p) - p[-1] * sum(p[:-1]))
        v, _ = AG.best_contiguous_bound(p, 1, 2)
        assert abs(v - khw) < 1e-7


def test_k2_four_contiguous_groups_match_pbar_float_n6():
    """Exploration: at n = 6 (k = 2), <= 4 contiguous groups of the sorted marginals give
    Pbar(n,2,p) on random points with Pbar < 1. (Not true in general: see the n = 8 test.)"""
    rng = random.Random(3)
    checked = 0
    while checked < 25:
        p = [rng.random() ** rng.choice([1, 2, 0.5]) for _ in range(6)]
        tight, _ = G.float_tight(p, 2)
        if tight > 1 - 1e-7:
            continue
        v, _ = AG.best_contiguous_bound(p, 2, 4)
        assert v - tight < 1e-7
        v3, _ = AG.best_contiguous_bound(p, 2, 3)
        assert v3 >= tight - 1e-7
        checked += 1


def test_k2_four_groups_fail_at_n8_exact():
    """H(k=2, 4 groups) is false: at this n = 8 point an exact half-integral dual certificate
    gives Pbar <= U = 68418893/10^8, while every aggregated LP over <= 4 contiguous groups has
    an exact feasible law of value >= 0.684191845 > U (reassessment 2026-11-14, J28)."""
    import itertools
    import math
    from fractions import Fraction as Fr

    import numpy as np
    from scipy.optimize import linprog
    from pwbound.rational import nullspace

    p = [Fr(s) for s in ["0.0055", "0.0108", "0.0318", "0.034", "0.0647", "0.3735", "0.3831", "0.5845"]]
    n, k = 8, 2
    pairs = list(itertools.combinations(range(n), 2))
    states = list(itertools.product((0, 1), repeat=n))
    pf = [float(x) for x in p]
    res = linprog([1] + pf + [pf[i] * pf[j] for i, j in pairs],
                  A_ub=[[-v for v in [1] + list(x) + [x[i] * x[j] for i, j in pairs]] for x in states],
                  b_ub=[-(1 if sum(x) >= k else 0) for x in states], bounds=(None, None), method="highs")
    q = [Fr(round(c * 2), 2) for c in res.x]
    val = lambda x: q[0] + sum(q[1 + i] * x[i] for i in range(n)) + sum(
        q[1 + n + t] * x[i] * x[j] for t, (i, j) in enumerate(pairs))
    assert all(val(x) >= (1 if sum(x) >= k else 0) for x in states)          # exact dual feasibility
    U = q[0] + sum(q[1 + i] * p[i] for i in range(n)) + sum(q[1 + n + t] * p[i] * p[j] for t, (i, j) in enumerate(pairs))
    assert U == Fr(68418893, 10 ** 8)

    def exact_feasible_value(part):
        sizes = [len(g) for g in part]
        P = [sum(p[i] for i in g) for g in part]
        E2 = [sum(p[i] * p[j] for i, j in itertools.combinations(g, 2)) for g in part]
        st = list(itertools.product(*[range(s + 1) for s in sizes]))
        rows, rhs = [[1] * len(st)], [Fr(1)]
        for a in range(len(part)):
            rows.append([s[a] for s in st]); rhs.append(P[a])
            if sizes[a] >= 2:
                rows.append([math.comb(s[a], 2) for s in st]); rhs.append(E2[a])
        for a, b in itertools.combinations(range(len(part)), 2):
            rows.append([s[a] * s[b] for s in st]); rhs.append(P[a] * P[b])
        rr = linprog([-(1 if sum(s) >= k else 0) for s in st], A_eq=np.array(rows, float),
                     b_eq=np.array([float(v) for v in rhs]), bounds=(0, None), method="highs-ds")
        sup = [j for j in range(len(st)) if rr.x[j] > 1e-11]
        # exact solution on the support: particular solution of [A_S | rhs] via a nullspace vector with last coord -1
        M = [[rows[i][j] for j in sup] + [-rhs[i]] for i in range(len(rows))]
        basis = nullspace(M)
        sol = None
        for v in basis:                       # combine basis vectors to make the last coordinate equal 1
            if v[-1] != 0:
                sol = [t / v[-1] for t in v]
                break
        assert sol is not None
        x = sol[:-1]
        assert all(sum(M[i][j] * sol[j] for j in range(len(sol))) == 0 for i in range(len(M)))
        assert min(x) >= 0                    # exact feasible law of group counts
        return sum(x[t] for t, j in enumerate(sup) if sum(st[j]) >= k)

    from pwbound.aggregation import contiguous_partitions
    low = min(exact_feasible_value(part) for part in contiguous_partitions(n, 4))
    assert low > U and float(low - U) > 2.9e-6


def test_proposition_a2_independent_law_approximates_k2():
    """k2_structure Prop. A2: P_ind(S>=2) <= Pbar(n,2,p) <= min(1,S2) <= (2+2 sqrt 2) P_ind(S>=2)."""
    import math
    rng = random.Random(4)
    c = 2 + 2 * math.sqrt(2)
    for _ in range(40):
        n = rng.randint(3, 6)
        p = [rng.random() ** rng.choice([1, 2, 5]) for _ in range(n)]
        d0, d1 = 1.0, 0.0
        for x in p:
            d0, d1 = d0 * (1 - x), d1 * (1 - x) + d0 * x
        pind = 1 - d0 - d1
        s1 = sum(p)
        s2 = (s1 * s1 - sum(x * x for x in p)) / 2
        tight, _ = G.float_tight(p, 2)
        assert pind <= tight + 1e-7 and tight <= min(1, s2) + 1e-7 and min(1, s2) <= c * pind + 1e-12


def test_k2_four_arbitrary_classes_fail_at_n9_exact():
    """Claim C37: at this n = 9 point no partition into <= 4 classes (all 11,051, not only contiguous)
    gives an exact aggregated LP; certified gap 4.2e-5 (about 40 s)."""
    from fractions import Fraction as Fr
    from scripts.verify_k2_aggregation_counterexamples import check, set_partitions
    p9 = [Fr(s) for s in ["0.0081", "0.024", "0.0348", "0.0384", "0.0433", "0.0446", "0.3587", "0.3903", "0.5778"]]
    assert check("C37", p9, list(set_partitions(9, 4)))


def _lambda_t_float(pR, t):
    """Lambda_t(p_R) = min sum w_ij p_i p_j s.t. w(E(S)) >= f_t(|S|) for all S (k2_structure Prop. K1)."""
    import itertools
    import math
    from scipy.optimize import linprog
    f = lambda s: max([0] + [(1 if s + j >= 2 else 0) - (2 - j) * s - math.comb(j, 2) for j in range(t + 1)])
    m = len(pR)
    if m < 2:
        return 0.0
    E = list(itertools.combinations(range(m), 2))
    A, b = [], []
    for s in range(2, m + 1):
        for S in itertools.combinations(range(m), s):
            A.append([-(1 if (i in S and j in S) else 0) for i, j in E])
            b.append(-f(s))
    r = linprog([pR[i] * pR[j] for i, j in E], A_ub=A, b_ub=b, bounds=(None, None), method="highs")
    return r.fun


def test_k1_split_upper_bound_is_valid_float():
    """Prop. K1: Pbar(n,2,p) <= 2 P_R - P_R P_T + e2(p_T) + Lambda_t(p_R) for every split (R, T)."""
    import itertools
    rng = random.Random(5)
    e2 = lambda v: (sum(v) ** 2 - sum(x * x for x in v)) / 2
    for _ in range(12):
        n = rng.randint(4, 6)
        p = [rng.random() ** rng.choice([1, 2, 4]) for _ in range(n)]
        tight, _ = G.float_tight(p, 2)
        for r in range(1, n):
            for R in itertools.combinations(range(n), r):
                pR = [p[i] for i in R]
                pT = [p[i] for i in range(n) if i not in R]
                PR, PT = sum(pR), sum(pT)
                ub = 2 * PR - PR * PT + e2(pT) + _lambda_t_float(pR, len(pT))
                assert tight <= ub + 1e-7


def test_k2_closed_form_of_lambda_t():
    """Prop. K2: for t >= |R|, Lambda_t(p_R) = e2(p_R) - p_max (P_R - p_max) (forest polytope, star)."""
    rng = random.Random(6)
    for _ in range(20):
        m = rng.randint(2, 6)
        pR = [rng.random() for _ in range(m)]
        t = rng.randint(m, m + 2)
        e2 = (sum(pR) ** 2 - sum(x * x for x in pR)) / 2
        mx = max(pR)
        assert abs(_lambda_t_float(pR, t) - (e2 - mx * (sum(pR) - mx))) < 1e-8


def test_bp_over_pbar_exceeds_1505_exact():
    """k2_report: with p = (1, b, a x 40), Pbar(42,2,p) = KHW(rest) (X_1 = 1 a.s. and R-N Thm 2.3),
    and the Boros-Prekopa bound exceeds it by a factor > 1.505 (exact rationals)."""
    from fractions import Fraction as F
    a, b = F(933, 100000), F(28128, 100000)
    rest = [b] + [a] * 40
    S, mx = sum(rest), max(rest)
    pbar = min(F(1), S - mx * (S - mx))
    assert pbar == F(2146509, 3906250)
    ratio = G.bp_value([F(1)] + rest, 2) / pbar
    assert ratio > F(1505, 1000)


def test_three_run_lp_matches_pbar_when_below_one_float():
    """Hypothesis R3' (k2_structure §13, exploration): for k = 2 and Pbar < 1, the LP over atoms whose ones
    form <= 3 runs in sorted order equals Pbar; it is always a lower bound. Includes the C36/C37 points."""
    from pwbound.runs_lp import runs_lp
    pts = [[0.0055, 0.0108, 0.0318, 0.034, 0.0647, 0.3735, 0.3831, 0.5845],
           [0.0081, 0.024, 0.0348, 0.0384, 0.0433, 0.0446, 0.3587, 0.3903, 0.5778]]
    rng = random.Random(7)
    while len(pts) < 14:
        p = sorted(rng.random() ** rng.choice([2, 3, 4]) for _ in range(rng.randint(6, 9)))
        if min(sum(p) - x for x in p) < 2:
            pts.append(p)
    for p in pts:
        tight, _ = G.float_tight(p, 2)
        v3, _ = runs_lp(p, 2, 3)
        assert v3 <= tight + 1e-7
        if tight < 1 - 1e-7:
            assert tight - v3 < 1e-7


def test_three_run_law_is_exactly_optimal_at_hard_points():
    """R3' holds exactly (rational arithmetic) at the C36 and C37 points: a law on atoms with <= 3 runs
    reaches the exact dual upper bound."""
    from fractions import Fraction as Fr
    from scripts.verify_k2_aggregation_counterexamples import check_three_runs
    for ps in (["0.0055", "0.0108", "0.0318", "0.034", "0.0647", "0.3735", "0.3831", "0.5845"],
               ["0.0081", "0.024", "0.0348", "0.0384", "0.0433", "0.0446", "0.3587", "0.3903", "0.5778"]):
        assert check_three_runs("point", [Fr(s) for s in ps])
