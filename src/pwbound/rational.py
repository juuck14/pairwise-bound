"""Exact rational helpers: strict parsing/formatting and Gaussian elimination."""
import re
from fractions import Fraction

_RATIONAL_RE = re.compile(r"-?[0-9]+(/[1-9][0-9]*)?", re.ASCII)


def parse_rational(text):
    """Parse "a" or "a/b" (ASCII digits only). Rejects decimals, exponents, NaN."""
    if not isinstance(text, str) or not _RATIONAL_RE.fullmatch(text):
        raise ValueError(f"not a rational string: {text!r}")
    num, _, den = text.partition("/")
    return Fraction(int(num), int(den) if den else 1)


def fmt(value):
    """Canonical string for a Fraction (or int): "a" or "a/b"."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def solve(matrix, rhs):
    """Solve the square system matrix @ x = rhs exactly; return None if singular."""
    n = len(matrix)
    aug = [[Fraction(v) for v in row] + [Fraction(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        aug[col] = [v / piv for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [vr - factor * vc for vr, vc in zip(aug[r], aug[col])]
    return [aug[i][n] for i in range(n)]


def rank(matrix):
    """Exact rank of a (not necessarily square) matrix."""
    rows = [[Fraction(v) for v in row] for row in matrix]
    if not rows:
        return 0
    r = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][col] != 0), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][col] != 0:
                factor = rows[i][col] / rows[r][col]
                rows[i] = [vi - factor * vr for vi, vr in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r
