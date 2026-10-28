"""Bounds of Ramachandra & Natarajan (arXiv:2006.00516 v6) specialised to (p,p,q,q,q).

Transcribed from the v6 source (notes/literature.md):
  * eq. (BorosPrekopa) in section 1: closed-form two-moment bound BP(n, k; S1, S2)
  * Theorem 3.1 (a)-(c): ordered SSS, ordered Boros-Prekopa, ordered Chebyshev
  * section 3.2: the r = k-1 term tightened with Theorem 2.3 (union bound)
  * Theorem 4.1: identical marginals, closed form
All in exact arithmetic. The closed form is cross-checked against the moment LP
(univariate.max_tail-style enumeration) in the tests, which guards against
transcription errors.
"""
from fractions import Fraction
from itertools import combinations
from math import ceil, comb

from .rational import solve

N, K = 5, 3


def sorted_marginals(p, q):
    return sorted([Fraction(p)] * 2 + [Fraction(q)] * 3)


def partial_moments(probs, r):
    """S_{1r}, S_{2r}: first two binomial moments of the n - r smallest probabilities."""
    sub = probs[: len(probs) - r]
    s1 = sum(sub)
    s2 = sum(a * b for a, b in combinations(sub, 2))
    return s1, s2


def bp_closed_form(n, k, s1, s2):
    """Boros-Prekopa upper bound on P(xi >= k), xi in [0, n], E C(xi,1)=s1, E C(xi,2)=s2."""
    if s1 == n:            # degenerate: xi = n surely
        return Fraction(1)
    if k < ((n - 1) * s1 - 2 * s2) / (n - s1):
        return Fraction(1)
    if s1 == 0 or k < 1 + 2 * s2 / s1:
        return ((k + n - 1) * s1 - 2 * s2) / (k * n)
    if k == s1:
        # 0/0 in the index formula (e.g. p = 0, q = 1); the bound is the LP value
        return bp_lp(n, k, s1, s2)
    i = ceil(((k - 1) * s1 - 2 * s2) / (k - s1))
    return ((i - 1) * (i - 2 * s1) + 2 * s2) / ((k - i) ** 2 + (k - i))


def bp_lp(n, k, s1, s2):
    """Same bound computed as the moment LP over laws on {0..n} (basis enumeration)."""
    cols = [(1, l, comb(l, 2)) for l in range(n + 1)]
    best = None
    for basis in combinations(range(n + 1), 3):
        x = solve([[cols[j][r] for j in basis] for r in range(3)], (1, s1, s2))
        if x is None or min(x) < 0:
            continue
        value = sum(v for j, v in zip(basis, x) if j >= k)
        best = value if best is None or value > best else best
    return best


def ordered_bp(p, q, closed_form=True):
    """Theorem 3.1(b): min over r in [0, k-1] of BP(n-r, k-r) on the n-r smallest."""
    probs = sorted_marginals(p, q)
    f = bp_closed_form if closed_form else bp_lp
    return min(f(N - r, K - r, *partial_moments(probs, r)) for r in range(K))


def unordered_bp(p, q):
    return bp_closed_form(N, K, *partial_moments(sorted_marginals(p, q), 0))


def ordered_sss(p, q):
    """Theorem 3.1(a)."""
    probs = sorted_marginals(p, q)
    terms = [Fraction(1)]
    terms += [partial_moments(probs, r)[0] / (K - r) for r in range(K)]
    terms += [partial_moments(probs, r)[1] / comb(K - r, 2) for r in range(K - 1)]
    return min(terms)


def ordered_chebyshev(p, q):
    """Theorem 3.1(c)."""
    probs = sorted_marginals(p, q)
    best = Fraction(1)
    for r in range(K):
        s1, s2 = partial_moments(probs, r)
        if K < s1 + r:
            value = Fraction(1)
        else:
            var = s1 - (s1 * s1 - 2 * s2)
            denom = var + (K - r - s1) ** 2
            value = var / denom if denom else Fraction(1)
        best = min(best, value)
    return best


def union_term(p, q):
    """Section 3.2: P(at least one of the n-k+1 smallest) via Theorem 2.3."""
    probs = sorted_marginals(p, q)
    m = N - K + 1
    return sum(probs[:m]) - probs[m - 1] * sum(probs[: m - 1])


def ordered_bp_tightened(p, q):
    return min(ordered_bp(p, q), union_term(p, q))


# ----------------------------------------------- the bounds as 12-state duals

def _univariate_dual_vertices(n, k):
    """Vertices z of {z : z0 + z1 s + z2 C(s,2) >= 1[s >= k], s = 0..n}."""
    out = []
    for tight in combinations(range(n + 1), 3):
        z = solve([[1, s, comb(s, 2)] for s in tight], [1 if s >= k else 0 for s in tight])
        if z is not None and all(z[0] + z[1] * s + z[2] * comb(s, 2) >= (1 if s >= k else 0)
                                 for s in range(n + 1)):
            out.append(tuple(z))
    return out


def _symmetrize(u0, u, uu):
    """32-state dual (u0, u_i, u_ij), 0-indexed -> G-average -> 12-state y (Prop. D)."""
    g1, g2 = (0, 1), (2, 3, 4)
    y1 = Fraction(sum(u.get(i, 0) for i in g1), 2)
    y2 = Fraction(sum(u.get(i, 0) for i in g2), 3)
    u12 = Fraction(uu.get((0, 1), 0))
    u22 = Fraction(sum(uu.get(pair, 0) for pair in ((2, 3), (2, 4), (3, 4))), 3)
    ux = Fraction(sum(uu.get((i, j), 0) for i in g1 for j in g2), 6)
    return (Fraction(u0), y1, y2, u12 / 2, u22 / 2, ux)


def dual_points():
    """Finite set W of 12-state dual-feasible points with
    ordered_bp_tightened(p, q) = min_{w in W} Q_w(p, q) for p <= q.

    Term r of Theorem 3.1(b) is the moment LP of the partial sum of the n - r
    smallest variables (X1, X2, X3, ... when p <= q); its dual vertices g lift
    to the 32-state dual g(x_1 + ... + x_{n-r}), valid because S >= k forces
    the partial sum >= k - r. The section 3.2 term uses the Theorem 2.3 dual on
    X1, X2, X3. Averaging over S2 x S3 keeps feasibility and the value.
    Returns {w: [labels]}.
    """
    points = {}
    for r in range(K):
        idx = list(range(N - r))
        for z in _univariate_dual_vertices(N - r, K - r):
            u = {i: z[1] for i in idx}
            uu = {pair: z[2] for pair in combinations(idx, 2)}
            points.setdefault(_symmetrize(z[0], u, uu), []).append(
                f"Thm 3.1(b) r={r}, z=({', '.join(str(t) for t in z)})")
    union = _symmetrize(0, {0: 1, 1: 1, 2: 1}, {(0, 2): -1, (1, 2): -1})
    points.setdefault(union, []).append("section 3.2 / Thm 2.3 union term")
    return points


def identical_closed_form(p, n=N, k=K):
    """Theorem 4.1 (identical marginals p in (0,1))."""
    p = Fraction(p)
    if k < (n - 1) * p:
        return Fraction(1)
    if k < 1 + (n - 1) * p:
        return ((n - 1) * (1 - p) + k) * p / k
    i = ceil(n * p * (k - 1 - (n - 1) * p) / (k - n * p))
    return ((i - 1) * (i - 2 * n * p) + n * (n - 1) * p * p) / ((k - i) ** 2 + (k - i))
