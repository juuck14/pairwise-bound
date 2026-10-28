"""Floating-point LPs solved with HiGHS (scipy) — exploration and cross-checks only.

The constraint matrices are rebuilt here from scratch instead of importing
`model`, so that a mistake in the exact pipeline's model definition would show
up as a disagreement rather than being shared.
"""
from itertools import combinations, product

import numpy as np
from scipy.optimize import linprog


def _solve_max(c, a_eq, b_eq):
    res = linprog(-np.asarray(c, dtype=float), A_eq=np.asarray(a_eq, dtype=float),
                  b_eq=np.asarray(b_eq, dtype=float), bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(f"HiGHS failed: {res.message}")
    return -res.fun, res.x


def full_lp(p, q):
    """32-state LP: total mass, 5 marginals, 10 pairwise products; max P(sum >= 3)."""
    p, q = float(p), float(q)
    target = [p, p, q, q, q]
    states = list(product((0, 1), repeat=5))
    rows, rhs = [[1.0] * 32], [1.0]
    for i in range(5):
        rows.append([float(x[i]) for x in states])
        rhs.append(target[i])
    for i, j in combinations(range(5), 2):
        rows.append([float(x[i] * x[j]) for x in states])
        rhs.append(target[i] * target[j])
    c = [1.0 if sum(x) >= 3 else 0.0 for x in states]
    value, x = _solve_max(c, rows, rhs)
    return value, dict(zip(states, x))


def reduced_lp(p, q):
    """12-state (A, B) LP with the five moment constraints; max P(A + B >= 3)."""
    p, q = float(p), float(q)
    states = [(a, b) for a in range(3) for b in range(4)]
    rows = [
        [1.0 for a, b in states],
        [float(a) for a, b in states],
        [float(b) for a, b in states],
        [float(a * (a - 1)) for a, b in states],
        [float(b * (b - 1)) for a, b in states],
        [float(a * b) for a, b in states],
    ]
    rhs = [1.0, 2 * p, 3 * q, 2 * p * p, 6 * q * q, 6 * p * q]
    c = [1.0 if a + b >= 3 else 0.0 for a, b in states]
    value, x = _solve_max(c, rows, rhs)
    return value, dict(zip(states, x))
