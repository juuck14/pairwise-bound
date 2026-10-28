"""Human-readable formatting of polynomials and distributions."""
from fractions import Fraction

from .rational import fmt


def format_poly(terms):
    """terms: list of (coefficient, monomial string); "" is the constant monomial."""
    parts = []
    for coef, mono in terms:
        coef = Fraction(coef)
        if coef == 0:
            continue
        sign = "-" if coef < 0 else "+"
        mag = abs(coef)
        if mono == "":
            body = fmt(mag)
        elif mag == 1:
            body = mono
        elif mag.denominator == 1:
            body = f"{fmt(mag)}{mono}"
        else:
            body = f"({fmt(mag)}){mono}"
        parts.append((sign, body))
    if not parts:
        return "0"
    first_sign, first_body = parts[0]
    out = ("-" if first_sign == "-" else "") + first_body
    for sign, body in parts[1:]:
        out += f" {sign} {body}"
    return out


def reduced_dual_string(y):
    """f(a, b) = y0 + y1 a + y2 b + y3 a(a-1) + y4 b(b-1) + y5 ab."""
    monos = ("", "a", "b", "a(a-1)", "b(b-1)", "ab")
    return format_poly(list(zip(y, monos)))


def quadratic_coefficients(y):
    """Q_y(p, q) = y . (1, 2p, 3q, 2p^2, 6q^2, 6pq) as {monomial: coefficient}."""
    y0, y1, y2, y3, y4, y5 = (Fraction(v) for v in y)
    return {"": y0, "p": 2 * y1, "q": 3 * y2, "p^2": 2 * y3, "q^2": 6 * y4, "pq": 6 * y5}


def quadratic_string(y):
    coeffs = quadratic_coefficients(y)
    order = ("p^2", "pq", "q^2", "p", "q", "")
    return format_poly([(coeffs[m], m) for m in order])
