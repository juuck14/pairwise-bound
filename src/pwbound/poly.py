"""Exact bivariate polynomials in (p, q) as {(i, j): Fraction} for p^i q^j."""
from fractions import Fraction

MONOMIALS = ((0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (1, 1))  # 1, p, q, p^2, q^2, pq
# reduced_rhs(p, q) = (1, 2p, 3q, 2p^2, 6q^2, 6pq) = diag(RHS_SCALE) @ MONOMIALS
RHS_SCALE = (1, 2, 3, 2, 6, 6)


def clean(poly):
    return {m: Fraction(c) for m, c in poly.items() if c != 0}


def add(f, g, scale=1):
    out = dict(f)
    for m, c in g.items():
        out[m] = out.get(m, 0) + scale * c
    return clean(out)


def evaluate(poly, p, q):
    return sum(c * p**i * q**j for (i, j), c in poly.items())


def from_dual(y):
    """Q_y(p, q) = y . reduced_rhs(p, q) as a polynomial."""
    return clean({m: Fraction(s) * Fraction(c) for m, s, c in zip(MONOMIALS, RHS_SCALE, y)})


def from_rhs_combination(weights):
    """sum_r weights[r] * reduced_rhs_r(p, q) as a polynomial."""
    return clean({m: Fraction(s) * Fraction(w) for m, s, w in zip(MONOMIALS, RHS_SCALE, weights)})


def to_string(poly, var=("p", "q")):
    if not poly:
        return "0"
    order = sorted(poly, key=lambda m: (-(m[0] + m[1]), -m[0]))
    parts = []
    for (i, j) in order:
        c = poly[(i, j)]
        mono = "".join(
            (v if e == 1 else f"{v}^{e}") for v, e in ((var[0], i), (var[1], j)) if e
        )
        mag = abs(c)
        if mono == "":
            body = str(mag)
        elif mag == 1:
            body = mono
        elif mag.denominator == 1:
            body = f"{mag}{mono}"
        else:
            body = f"({mag}){mono}"
        parts.append(("-" if c < 0 else "+", body))
    out = ("-" if parts[0][0] == "-" else "") + parts[0][1]
    for sign, body in parts[1:]:
        out += f" {sign} {body}"
    return out
