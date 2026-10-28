"""Exact solution of the 12-state LP by exhaustive basis enumeration.

The reduced LP is  max c.x  s.t.  A x = b(p, q), x >= 0  with A of size 6 x 12
(model.reduced_matrix) and full row rank 6. A basis is a set of 6 columns with
nonsingular A_B. For a basis B:
  primal basic solution  x_B = A_B^{-1} b(p, q)    (depends on p, q)
  dual basic solution    y_B = A_B^{-T} c_B        (independent of p, q)
B is optimal at (p, q) iff x_B >= 0 and A^T y_B >= c (dual feasible). Such a
basis exists for every (p, q) because the LP is feasible and bounded.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from . import model
from .rational import solve


def _columns():
    return [model.reduced_row(a, b) for a, b in model.STATES12]


def basis_matrix(basis):
    cols = _columns()
    return [[cols[j][r] for j in basis] for r in range(6)]


def primal_basic_solution(basis, p, q):
    """x_B = A_B^{-1} b(p, q) as a list aligned with `basis`, or None if singular."""
    return solve(basis_matrix(basis), model.reduced_rhs(p, q))


def dual_basic_solution(basis):
    """y_B solving A_B^T y = c_B, or None if singular."""
    cols = _columns()
    c = model.reduced_objective()
    return solve([list(cols[j]) for j in basis], [c[j] for j in basis])


def is_dual_feasible(y):
    return all(model.dual_poly12(y, a, b) >= model.indicator12((a, b)) for a, b in model.STATES12)


@lru_cache(maxsize=None)
def enumerate_bases():
    """All nonsingular bases with their dual solutions: tuple of (basis, y)."""
    out = []
    for basis in combinations(range(len(model.STATES12)), 6):
        y = dual_basic_solution(basis)
        if y is not None:
            out.append((basis, tuple(y)))
    return tuple(out)


@lru_cache(maxsize=None)
def dual_feasible_bases():
    return tuple((b, y) for b, y in enumerate_bases() if is_dual_feasible(y))


@lru_cache(maxsize=None)
def dual_vertices():
    """Distinct dual vertices y (sorted) mapped to the bases that produce them."""
    groups = {}
    for basis, y in dual_feasible_bases():
        groups.setdefault(y, []).append(basis)
    return tuple((y, tuple(groups[y])) for y in sorted(groups))


def envelope(p, q):
    """min over dual vertices of Q_y(p, q); equals M(p, q) by LP duality."""
    return min(model.reduced_dual_value(y, p, q) for y, _ in dual_vertices())


def solve_point(p, q):
    """Exact optimum at (p, q) with matching primal and dual certificates.

    Scans dual-feasible bases in lexicographic order and returns the first one
    whose primal basic solution is nonnegative (deterministic choice).
    """
    p, q = Fraction(p), Fraction(q)
    for basis, y in dual_feasible_bases():
        x = primal_basic_solution(basis, p, q)
        if x is not None and min(x) >= 0:
            pi = {s: Fraction(0) for s in model.STATES12}
            for j, v in zip(basis, x):
                pi[model.STATES12[j]] = v
            value = sum(v for s, v in pi.items() if model.indicator12(s))
            if value != model.reduced_dual_value(y, p, q):  # complementary slackness
                raise RuntimeError(f"primal/dual mismatch for basis {basis} at p={p}, q={q}")
            return {"p": p, "q": q, "value": value, "pi": pi, "y": y,
                    "basis": [model.STATES12[j] for j in basis]}
    raise RuntimeError(f"no optimal basis found at p={p}, q={q}")


def primal_optimum_by_enumeration(p, q):
    """Max objective over all primal basic feasible solutions (independent route)."""
    p, q = Fraction(p), Fraction(q)
    c = model.reduced_objective()
    best = None
    for basis, _ in enumerate_bases():
        x = primal_basic_solution(basis, p, q)
        if x is not None and min(x) >= 0:
            value = sum(c[j] * v for j, v in zip(basis, x))
            best = value if best is None or value > best else best
    return best
