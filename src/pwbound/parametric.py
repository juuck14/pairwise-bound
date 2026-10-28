"""Parametric view of the 12-state LP over (p, q).

For a basis B the primal basic solution x_B(p, q) = A_B^{-1} b(p, q) has entries
that are polynomials of degree <= 2 in (p, q) (b is linear in the monomials
1, p, q, p^2, q^2, pq). The critical region of a dual-feasible basis B is
CR_B = {(p, q) : x_B(p, q) >= 0}; on it, M(p, q) = Q_{y_B}(p, q) and x_B(p, q)
is a maximizing distribution. The region of a dual vertex y is the union of
CR_B over the bases B with y_B = y.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import gcd, lcm

from . import exact_lp, model, poly, trimin
from .rational import solve


@lru_cache(maxsize=None)
def vertices():
    """Dual vertices with stable ids V01..V21 (order of exact_lp.dual_vertices)."""
    out = []
    for k, (y, bases) in enumerate(exact_lp.dual_vertices(), start=1):
        out.append({"id": f"V{k:02d}", "y": y, "Q": poly.from_dual(y), "bases": bases})
    return tuple(out)


def vertex_by_id(vid):
    return next(v for v in vertices() if v["id"] == vid)


@lru_cache(maxsize=None)
def basis_inverse(basis):
    """A_B^{-1} as a list of rows (exact)."""
    mat = exact_lp.basis_matrix(basis)
    cols = []
    for r in range(6):
        e = [0] * 6
        e[r] = 1
        cols.append(solve(mat, e))
    return [[cols[c][i] for c in range(6)] for i in range(6)]


@lru_cache(maxsize=None)
def parametric_primal(basis):
    """x_B(p, q) as a tuple of 6 polynomials, aligned with `basis`."""
    inv = basis_inverse(basis)
    return tuple(poly.from_rhs_combination(inv[i]) for i in range(6))


def primal_at(basis, p, q):
    return [poly.evaluate(f, p, q) for f in parametric_primal(basis)]


def in_critical_region(basis, p, q, strict=False):
    xs = primal_at(basis, p, q)
    return all(x > 0 for x in xs) if strict else all(x >= 0 for x in xs)


def values_at(p, q):
    """{vertex id: Q_y(p, q)}."""
    return {v["id"]: poly.evaluate(v["Q"], p, q) for v in vertices()}


def minimizers(p, q):
    vals = values_at(p, q)
    m = min(vals.values())
    return m, sorted(k for k, v in vals.items() if v == m)


DOMAIN = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)), (Fraction(1), Fraction(1)))


# ------------------------------------------------------------ regions as cones

def tight_states(y):
    """States (a, b) where the dual polynomial touches the indicator."""
    return tuple(s for s in model.STATES12 if model.dual_poly12(y, *s) == model.indicator12(s))


def _nullspace_1d(rows):
    """A nonzero vector h with rows @ h = 0, assuming the nullspace is 1-dimensional."""
    n = len(rows[0])
    m = [[Fraction(v) for v in r] for r in rows]
    pivots, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        m[r] = [v / m[r][c] for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [vi - f * vr for vi, vr in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivots]
    if len(free) != 1:
        return None
    h = [Fraction(0)] * n
    h[free[0]] = Fraction(1)
    for i, c in enumerate(pivots):
        h[c] = -m[i][free[0]]
    return h


def _primitive(h):
    """Scale a rational vector to a primitive integer vector (same direction)."""
    den = 1
    for v in h:
        den = lcm(den, v.denominator)
    ints = [int(v * den) for v in h]
    g = 0
    for v in ints:
        g = gcd(g, abs(v))
    return tuple(v // g for v in ints)


@lru_cache(maxsize=None)
def cone_facets(states):
    """Facet normals h (primitive integer, h . col >= 0) of cone{reduced_row(s)}."""
    gens = [model.reduced_row(*s) for s in states]
    facets = set()
    for subset in combinations(range(len(gens)), 5):
        h = _nullspace_1d([gens[i] for i in subset])
        if h is None:
            continue
        signs = {(sum(a * b for a, b in zip(h, g)) > 0) - (sum(a * b for a, b in zip(h, g)) < 0)
                 for g in gens}
        if 1 in signs and -1 in signs:
            continue
        if -1 in signs:
            h = [-v for v in h]
        facets.add(_primitive(h))
    return tuple(sorted(facets))


@lru_cache(maxsize=None)
def region_polynomials(vid):
    """g_h(p, q) = h . b(p, q) for every facet h; region = {all g_h >= 0}."""
    v = vertex_by_id(vid)
    return tuple((h, poly.from_rhs_combination(h)) for h in cone_facets(tight_states(v["y"])))


def in_region(vid, p, q):
    return all(poly.evaluate(g, p, q) >= 0 for _, g in region_polynomials(vid))


# --------------------------------------------------- activity: witnesses, covers

def is_strict_minimizer(vid, p, q):
    vals = values_at(p, q)
    return all(vals[vid] < v for k, v in vals.items() if k != vid)


def interior_points_by_denominator(max_denominator):
    """Rational points with 0 < p < q < 1, each once, ordered by common denominator."""
    for d in range(3, max_denominator + 1):
        for i in range(1, d):
            for j in range(i + 1, d):
                p, q = Fraction(i, d), Fraction(j, d)
                if max(p.denominator, q.denominator) == d:
                    yield p, q


def find_witnesses(max_denominator=60):
    """{vertex id: first point (by denominator) where it is the strict minimum}."""
    found = {}
    for p, q in interior_points_by_denominator(max_denominator):
        vals = values_at(p, q)
        best = min(vals.values())
        ids = [k for k, v in vals.items() if v == best]
        if len(ids) == 1 and ids[0] not in found:
            found[ids[0]] = (p, q)
    return found


def _midpoint(u, v):
    return ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)


def subdivide(tri):
    """Fixed 4-way midpoint split, in the order the verifier reproduces."""
    a, b, c = tri
    ab, bc, ca = _midpoint(a, b), _midpoint(b, c), _midpoint(c, a)
    return ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))


def dominance_cover(vid, tri=DOMAIN, depth=0, max_depth=10):
    """Tree proving vid is nowhere the strict minimum on `tri`.

    Leaf {"dominator": w}: Q_vid - Q_w >= 0 on the whole triangle (exact).
    Node {"split": [4 subtrees]} following `subdivide`. Returns None on failure.
    """
    q_v = vertex_by_id(vid)["Q"]
    for w in vertices():
        if w["id"] != vid and trimin.minimum(poly.add(q_v, w["Q"], -1), tri)[0] >= 0:
            return {"dominator": w["id"]}
    if depth == max_depth:
        return None
    children = [dominance_cover(vid, t, depth + 1, max_depth) for t in subdivide(tri)]
    if any(c is None for c in children):
        return None
    return {"split": children}


def strict_witness_check(vid, p, q):
    """True iff some basis of vertex `vid` has x_B(p, q) > 0 componentwise.

    Then the dual optimum at (p, q) is unique (complementary slackness pins
    y on the 6 basis states), so Q_vid < Q_other for every other vertex and,
    by continuity, on a neighbourhood: vertex `vid` is interior-active.
    """
    return any(in_critical_region(b, p, q, strict=True) for b in vertex_by_id(vid)["bases"])
