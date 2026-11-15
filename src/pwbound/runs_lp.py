"""Pairwise-independence LP restricted to atoms with few runs (float, exploration).

Sort the marginals ascending. An atom x in {0,1}^n has r runs if its 1-coordinates form r maximal
blocks of consecutive positions. The LP

    max P(S >= k)  over laws on {x : runs(x) <= r}  with  E x_i = p_i,  E x_i x_j = p_i p_j

is a lower bound on Pbar(n,k,p) (it restricts the support) and has O(n^{2r}) columns and
1 + n + C(n,2) rows, so it is polynomial for fixed r. Hypothesis R3 (notes/k2_structure.md §13):
for k = 2, r = 3 already gives Pbar(n,2,p). Float (HiGHS) only.
"""
from itertools import combinations


def atoms_with_runs(n, r):
    """All x in {0,1}^n with at most r runs of ones (as tuples), the empty atom included."""
    out = [tuple([0] * n)]
    for j in range(1, r + 1):
        for cuts in combinations(range(n + 1), 2 * j):
            # runs [cuts[0], cuts[1]), [cuts[2], cuts[3]), ... ; consecutive runs must be separated
            if any(cuts[2 * t + 1] == cuts[2 * t + 2] for t in range(j - 1)):
                continue
            x = [0] * n
            for t in range(j):
                for i in range(cuts[2 * t], cuts[2 * t + 1]):
                    x[i] = 1
            out.append(tuple(x))
    return out


def runs_lp(p, k, r):
    """(value, law) of the LP restricted to atoms with <= r runs (p is sorted inside)."""
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix
    ps = sorted(float(x) for x in p)
    n = len(ps)
    atoms = atoms_with_runs(n, r)
    pairs = list(combinations(range(n), 2))
    A = lil_matrix((1 + n + len(pairs), len(atoms)))
    for c, x in enumerate(atoms):
        A[0, c] = 1
        ones = [i for i in range(n) if x[i]]
        for i in ones:
            A[1 + i, c] = 1
        pos = {pr: 1 + n + t for t, pr in enumerate(pairs)}
        for i, j in combinations(ones, 2):
            A[pos[(i, j)], c] = 1
    b = np.array([1.0] + ps + [ps[i] * ps[j] for i, j in pairs])
    cost = -np.array([1.0 if sum(x) >= k else 0.0 for x in atoms])
    res = linprog(cost, A_eq=A.tocsr(), b_eq=b, bounds=(0, None), method="highs")
    if res.status != 0:
        return None, None
    law = {atoms[c]: res.x[c] for c in range(len(atoms)) if res.x[c] > 1e-12}
    return -res.fun, law
