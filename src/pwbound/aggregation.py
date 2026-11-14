"""Grouped (aggregated) moment LPs for pairwise independent Bernoulli vectors (float, exploration).

For a partition of the coordinates into groups G_1..G_g, the aggregated LP maximises
P(N_1 + ... + N_g >= k) over laws of the group counts N_a in {0..|G_a|} with the moments that
pairwise independence fixes:

    E N_a = P_a = sum_{i in G_a} p_i,
    E C(N_a, 2) = e_2(p_{G_a}),
    E N_a N_b = P_a P_b  (a != b).

Every pairwise independent law induces such a law of counts, so each aggregated value is an
upper bound on Pbar(n,k,p); the all-singletons partition gives Pbar itself, the one-group
partition gives the Boros-Prekopa bound. Working hypothesis H(k=2, 4 groups)
(notes/reassessment_2026-11-14.md): the minimum over partitions of the sorted coordinates into
at most 4 contiguous groups equals Pbar(n,2,p). It held on every random point for n <= 7 but is
FALSE at n = 8 (exact certificate, tests/test_aggregation.py); whether a bounded number of
groups suffices is open. Float only (HiGHS); nothing here is a proof.
"""
import itertools
import math


def aggregated_bound(p, groups, k):
    """HiGHS value of the aggregated LP for the partition `groups` (lists of indices into p)."""
    import numpy as np
    from scipy.optimize import linprog
    sizes = [len(g) for g in groups]
    P = [sum(p[i] for i in g) for g in groups]
    E2 = [sum(p[i] * p[j] for i, j in itertools.combinations(g, 2)) for g in groups]
    states = list(itertools.product(*[range(s + 1) for s in sizes]))
    rows, rhs = [[1.0] * len(states)], [1.0]
    for a in range(len(groups)):
        rows.append([s[a] for s in states])
        rhs.append(P[a])
        if sizes[a] >= 2:
            rows.append([math.comb(s[a], 2) for s in states])
            rhs.append(E2[a])
    for a, b in itertools.combinations(range(len(groups)), 2):
        rows.append([s[a] * s[b] for s in states])
        rhs.append(P[a] * P[b])
    c = [-1.0 if sum(s) >= k else 0.0 for s in states]
    res = linprog(c, A_eq=np.array(rows, dtype=float), b_eq=np.array(rhs), bounds=(0, None), method="highs")
    return -res.fun if res.status == 0 else None


def contiguous_partitions(n, max_groups):
    """Partitions of range(n) into at most max_groups contiguous blocks."""
    for g in range(1, max_groups + 1):
        for cuts in itertools.combinations(range(1, n), g - 1):
            bounds = [0, *cuts, n]
            yield [list(range(bounds[i], bounds[i + 1])) for i in range(g)]


def best_contiguous_bound(p, k, max_groups):
    """min over contiguous partitions (of p sorted ascending) into <= max_groups groups of the
    aggregated bound; returns (value, group sizes)."""
    ps = sorted(p)
    best = (math.inf, None)
    for part in contiguous_partitions(len(ps), max_groups):
        v = aggregated_bound(ps, part, k)
        if v is not None and v < best[0]:
            best = (v, [len(g) for g in part])
    return best
