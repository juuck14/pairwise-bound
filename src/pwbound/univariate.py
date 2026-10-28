"""Univariate binomial-moment LP for S = X1 + ... + X5 (exact, Fraction).

max P(S >= 3) over laws v on {0, ..., 5} with E[1] = 1, E[S] = s1 and
E[C(S, 2)] = s2. Two uses:
  * p = q: the full symmetric reduction (S_5 averaging), s1 = 5p, s2 = 10p^2;
    this must equal the 12-state value.
  * general (p, q): s1 = 2p + 3q, s2 = p^2 + 6pq + 3q^2 is a relaxation that
    only keeps the first two binomial moments of S, so its value is >= M(p, q).
"""
from fractions import Fraction
from itertools import combinations
from math import comb

from .rational import solve

SUPPORT = tuple(range(6))
THRESHOLD = 3


def binomial_moments(p, q):
    s1 = 2 * p + 3 * q
    s2 = p * p + 6 * p * q + 3 * q * q
    return s1, s2


def max_tail(s1, s2):
    """Exact optimum by enumerating all bases (3 constraints, 6 variables)."""
    cols = [(1, l, comb(l, 2)) for l in SUPPORT]
    rhs = (1, Fraction(s1), Fraction(s2))
    best = None
    for basis in combinations(SUPPORT, 3):
        x = solve([[cols[j][r] for j in basis] for r in range(3)], rhs)
        if x is None or min(x) < 0:
            continue
        value = sum(v for j, v in zip(basis, x) if j >= THRESHOLD)
        best = value if best is None or value > best else best
    return best


def symmetric_value(p):
    """Value of the fully symmetric model when p = q."""
    p = Fraction(p)
    return max_tail(5 * p, 10 * p * p)


def relaxation_value(p, q):
    """Two-moment relaxation for general (p, q): an upper bound on M(p, q)."""
    return max_tail(*binomial_moments(Fraction(p), Fraction(q)))
