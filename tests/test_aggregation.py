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
