"""Single source of truth for the problem: 32-state and 12-state models.

Variables are 0-indexed here: X1, X2 -> 0, 1 (group G1, marginal p) and
X3, X4, X5 -> 2, 3, 4 (group G2, marginal q). Reported names stay 1-indexed.
All functions work with Fractions (exact) or floats (exploration only).
"""
from fractions import Fraction
from itertools import combinations, product
from math import comb

N = 5
GROUP1 = (0, 1)
GROUP2 = (2, 3, 4)
THRESHOLD = 3
PAIRS = tuple(combinations(range(N), 2))
STATES32 = tuple(product((0, 1), repeat=N))
STATES12 = tuple((a, b) for a in range(3) for b in range(4))

REDUCED_CONSTRAINTS = ("total", "E[A]", "E[B]", "E[A(A-1)]", "E[B(B-1)]", "E[AB]")
FULL_CONSTRAINTS = (
    ("total",)
    + tuple(f"P(X{i + 1}=1)" for i in range(N))
    + tuple(f"P(X{i + 1}=1,X{j + 1}=1)" for i, j in PAIRS)
)


def bitstring(x):
    """State tuple -> "x1x2x3x4x5" (leftmost character is X1)."""
    return "".join(str(v) for v in x)


def group_counts(x):
    return (x[0] + x[1], x[2] + x[3] + x[4])


def marginals(p, q):
    return (p, p, q, q, q)


def indicator12(state):
    a, b = state
    return 1 if a + b >= THRESHOLD else 0


def indicator32(x):
    return 1 if sum(x) >= THRESHOLD else 0


# ------------------------------------------------------------ reduced model

def reduced_row(a, b):
    """Column of the 12-state constraint matrix for state (a, b)."""
    return (1, a, b, a * (a - 1), b * (b - 1), a * b)


def reduced_rhs(p, q):
    return (1, 2 * p, 3 * q, 2 * p * p, 6 * q * q, 6 * p * q)


def reduced_matrix():
    """6 x 12 constraint matrix; column order follows STATES12."""
    cols = [reduced_row(a, b) for a, b in STATES12]
    return [[col[r] for col in cols] for r in range(len(REDUCED_CONSTRAINTS))]


def reduced_objective():
    return [indicator12(s) for s in STATES12]


def dual_poly12(y, a, b):
    """f(a, b) = y . reduced_row(a, b)."""
    return sum(c * r for c, r in zip(y, reduced_row(a, b)))


def reduced_dual_value(y, p, q):
    """Quadratic Q_y(p, q) = y . reduced_rhs(p, q)."""
    return sum(c * r for c, r in zip(y, reduced_rhs(p, q)))


# --------------------------------------------------------------- full model

def full_row(x):
    """Column of the 32-state constraint matrix for state x."""
    return (1,) + tuple(x) + tuple(x[i] * x[j] for i, j in PAIRS)


def full_rhs(p, q):
    m = marginals(p, q)
    return (1,) + m + tuple(m[i] * m[j] for i, j in PAIRS)


def full_matrix():
    """16 x 32 constraint matrix; column order follows STATES32."""
    cols = [full_row(x) for x in STATES32]
    return [[col[r] for col in cols] for r in range(len(FULL_CONSTRAINTS))]


def full_objective():
    return [indicator32(x) for x in STATES32]


# ------------------------------------------------------ lifting / projection

def lift_primal(pi):
    """12-state law of (A, B) -> 32-state law, uniform within each orbit.

    mu(x) = pi(a, b) / (C(2, a) C(3, b)) with (a, b) = group_counts(x).
    """
    return {x: Fraction(pi[group_counts(x)]) / (comb(2, group_counts(x)[0]) * comb(3, group_counts(x)[1]))
            for x in STATES32}


def project_primal(mu):
    """32-state law -> law of (A, B)."""
    pi = {s: Fraction(0) for s in STATES12}
    for x, v in mu.items():
        pi[group_counts(x)] += v
    return pi


def lift_dual(y):
    """Reduced dual y = (y0..y5) -> 32-state dual (u0, u, uu).

    Uses x_i^2 = x_i: a(a-1) = 2 x1 x2, b(b-1) = 2 (x3x4 + x3x5 + x4x5),
    ab = sum of the six cross products. Hence the factors 2*y3 and 2*y4.
    """
    y0, y1, y2, y3, y4, y5 = (Fraction(v) for v in y)
    u = {i: (y1 if i in GROUP1 else y2) for i in range(N)}
    uu = {}
    for i, j in PAIRS:
        if i in GROUP1 and j in GROUP1:
            uu[(i, j)] = 2 * y3
        elif i in GROUP2 and j in GROUP2:
            uu[(i, j)] = 2 * y4
        else:
            uu[(i, j)] = y5
    return y0, u, uu


def full_dual_poly(u0, u, uu, x):
    return u0 + sum(u[i] * x[i] for i in range(N)) + sum(uu[(i, j)] * x[i] * x[j] for i, j in PAIRS)


def full_dual_value(u0, u, uu, p, q):
    m = marginals(p, q)
    return u0 + sum(u[i] * m[i] for i in range(N)) + sum(uu[(i, j)] * m[i] * m[j] for i, j in PAIRS)


# ------------------------------------------------------ reference distributions

def product_distribution(p, q):
    """Mutually independent law (always feasible) on the 32 states."""
    m = marginals(p, q)
    dist = {}
    for x in STATES32:
        prob = 1
        for i in range(N):
            prob *= m[i] if x[i] else 1 - m[i]
        dist[x] = prob
    return dist
