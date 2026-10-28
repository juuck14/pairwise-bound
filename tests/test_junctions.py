"""Every junction in results/regions/JUNCTIONS.md is exact: the listed pieces all
attain M there (checked symbolically with radicals)."""
import re

import pytest
import sympy as sp

from pwbound import parametric

from conftest import REPO

P, Q = sp.symbols("p q", real=True)


def rows():
    text = (REPO / "results" / "regions" / "JUNCTIONS.md").read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.match(r"V\d\d", cells[3]):
            out.append((sp.sympify(cells[0]), sp.sympify(cells[1]), [c.strip() for c in cells[3].split(",")]))
    return out


def q_expr(vid):
    f = parametric.vertex_by_id(vid)["Q"]
    return sum(sp.Rational(c.numerator, c.denominator) * P**i * Q**j for (i, j), c in f.items())


def test_table_is_not_empty():
    assert len(rows()) == 14


@pytest.mark.parametrize("p, q, pieces", rows())
def test_listed_pieces_attain_the_minimum_exactly(p, q, pieces):
    values = {v["id"]: sp.nsimplify(sp.radsimp(sp.expand(q_expr(v["id"]).subs({P: p, Q: q}))))
              for v in parametric.vertices()}
    m = min(values.values(), key=lambda v: float(v))
    for vid in pieces:
        assert sp.simplify(values[vid] - m) == 0, (vid, p, q)
    for vid, v in values.items():
        assert sp.simplify(v - m) >= 0
