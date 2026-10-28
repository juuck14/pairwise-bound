"""Exact minimum of a polynomial of degree <= 2 in (p, q) over a closed triangle.

The minimum over a compact triangle is attained at a vertex, at the interior
critical point of an edge restriction, or at an interior critical point of the
whole quadratic. With rational data every candidate is rational.
"""
from fractions import Fraction

from . import poly


def _coeffs(f):
    g = lambda m: Fraction(f.get(m, 0))
    # f = a p^2 + b q^2 + c pq + d p + e q + k
    return g((2, 0)), g((0, 2)), g((1, 1)), g((1, 0)), g((0, 1)), g((0, 0))


def _in_triangle(pt, tri):
    (x, y) = pt
    (x1, y1), (x2, y2), (x3, y3) = tri
    det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    l3 = 1 - l1 - l2
    return l1 >= 0 and l2 >= 0 and l3 >= 0


def candidates(f, tri):
    """Points of the triangle among which f attains its minimum."""
    a, b, c, d, e, _ = _coeffs(f)
    pts = [tuple(map(Fraction, v)) for v in tri]
    for i in range(3):
        u, v = pts[i], pts[(i + 1) % 3]
        dx, dy = v[0] - u[0], v[1] - u[1]
        # f(u + t (v - u)) = alpha t^2 + beta t + const
        alpha = a * dx * dx + b * dy * dy + c * dx * dy
        beta = 2 * a * u[0] * dx + 2 * b * u[1] * dy + c * (u[0] * dy + u[1] * dx) + d * dx + e * dy
        if alpha > 0:
            t = -beta / (2 * alpha)
            if 0 < t < 1:
                pts.append((u[0] + t * dx, u[1] + t * dy))
    det = 4 * a * b - c * c
    if det > 0 and a > 0:
        # grad = 0: [2a c; c 2b][p q]^T = -[d e]^T
        p0 = (-d * 2 * b + c * e) / det
        q0 = (-2 * a * e + c * d) / det
        if _in_triangle((p0, q0), tri):
            pts.append((p0, q0))
    return pts


def minimum(f, tri):
    """(min value, argmin point) of polynomial f over the closed triangle `tri`."""
    return min(((poly.evaluate(f, p, q), (p, q)) for p, q in candidates(f, tri)), key=lambda t: t[0])
