"""Build and write `pw5-point/v1` certificates (format: verifier/SPEC.md).

The generator side only assembles the certificate; validity is decided by the
independent verifier in verifier/verify.py.
"""
import json
from fractions import Fraction

from .model import PAIRS, STATES12, STATES32, bitstring, lift_dual, lift_primal
from .rational import fmt

FORMAT = "pw5-point/v1"


def build_certificate(p, q, value, pi, y, provenance=None):
    """Assemble a certificate from a 12-state primal pi and a reduced dual y."""
    mu = lift_primal(pi)
    u0, u, uu = lift_dual(y)
    return {
        "format": FORMAT,
        "problem": {"p": fmt(p), "q": fmt(q), "groups": [[1, 2], [3, 4, 5]], "threshold": 3},
        "claim": {"value": fmt(value)},
        "primal": {
            "reduced": {f"{a},{b}": fmt(pi[(a, b)]) for a, b in STATES12},
            "lifted": {bitstring(x): fmt(mu[x]) for x in STATES32},
        },
        "dual": {
            "reduced": {f"y{k}": fmt(v) for k, v in enumerate(y)},
            "lifted": {
                "const": fmt(u0),
                "x": {str(i + 1): fmt(u[i]) for i in range(5)},
                "xx": {f"{i + 1},{j + 1}": fmt(uu[(i, j)]) for i, j in PAIRS},
            },
        },
        "provenance": provenance or {},
    }


def certificate_filename(p, q):
    """e.g. p=2/5, q=3/5 -> "p2_5-q3_5.json"."""
    def tag(v):
        return fmt(Fraction(v)).replace("/", "_").replace("-", "m")
    return f"p{tag(p)}-q{tag(q)}.json"


def dumps(cert):
    return json.dumps(cert, indent=2, ensure_ascii=False) + "\n"


def write_certificate(cert, path):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(dumps(cert))
