import json
import random
from fractions import Fraction as F

import pytest

from pwbound import exact_lp, model
from pwbound.cert import dumps
from scripts.make_certificate import make_certificate

from conftest import REPO, SEED_PI, SEED_Y

RNG_SEED = 20261028


def random_points(count, seed=RNG_SEED, denominator=60):
    rng = random.Random(seed)
    return [(F(rng.randint(0, denominator), denominator), F(rng.randint(0, denominator), denominator))
            for _ in range(count)]


def test_representative_point_reproduces_61_over_75():
    sol = exact_lp.solve_point(F(2, 5), F(3, 5))
    assert sol["value"] == F(61, 75)
    assert sol["pi"] == SEED_PI
    assert sol["y"] == SEED_Y


def test_committed_certificate_is_reproducible_and_verified(verifier):
    path = REPO / "results" / "certificates" / "p2_5-q3_5.json"
    _, cert = make_certificate(F(2, 5), F(3, 5))
    assert path.read_text(encoding="utf-8") == dumps(cert)
    assert verifier.verify_text(path.read_text(encoding="utf-8"))["verdict"] == "PASS"


def test_enumeration_counts():
    assert len(exact_lp.enumerate_bases()) == 764
    assert len(exact_lp.dual_feasible_bases()) == 50
    vertices = exact_lp.dual_vertices()
    assert len(vertices) == 21
    assert sorted(len(bases) for _, bases in vertices) == [1] * 19 + [6, 25]


def test_every_dual_vertex_dominates_the_indicator():
    for y, _ in exact_lp.dual_vertices():
        assert exact_lp.is_dual_feasible(y)


@pytest.mark.parametrize("p, q", random_points(15))
def test_three_exact_routes_agree(p, q):
    """solve_point (primal+dual basis) = min of dual quadratics = max over primal BFS."""
    value = exact_lp.solve_point(p, q)["value"]
    assert value == exact_lp.envelope(p, q)
    assert value == exact_lp.primal_optimum_by_enumeration(p, q)


@pytest.mark.parametrize("p, q", random_points(10, seed=RNG_SEED + 1)
                         + [(F(0), F(0)), (F(0), F(1)), (F(1), F(1)), (F(0), F(1, 3)),
                            (F(1, 4), F(1)), (F(1, 2), F(1, 2)), (F(3, 4), F(3, 4)),
                            (F(3, 5), F(2, 5))])
def test_generated_certificates_pass_the_verifier(verifier, p, q):
    _, cert = make_certificate(p, q)
    result = verifier.verify_text(json.dumps(cert), allow_outside_scope=True)
    assert result["verdict"] == "PASS", [c for c in result["checks"] if not c["ok"]]
