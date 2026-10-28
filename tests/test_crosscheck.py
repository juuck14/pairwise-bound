"""Cross-checks of the exact solver against independent routes and known facts."""
from fractions import Fraction as F

import pytest

from pwbound import exact_lp, float_lp, model, univariate

from test_exact import random_points

TOL = 1e-9


def M(p, q):
    return exact_lp.solve_point(F(p), F(q))["value"]


@pytest.mark.parametrize("p, q", random_points(12, seed=7))
def test_highs_full_and_reduced_match_exact(p, q):
    exact = float(M(p, q))
    full, _ = float_lp.full_lp(p, q)
    reduced, _ = float_lp.reduced_lp(p, q)
    assert abs(full - exact) < TOL
    assert abs(reduced - exact) < TOL


@pytest.mark.parametrize("k", range(0, 98))
def test_diagonal_matches_fully_symmetric_model(k):
    p = F(k, 97)
    assert M(p, p) == univariate.symmetric_value(p)


@pytest.mark.parametrize("p, q", [(p, q) for p, q in random_points(20, seed=11)])
def test_two_moment_relaxation_is_an_upper_bound(p, q):
    assert M(p, q) <= univariate.relaxation_value(p, q)


def test_two_moment_relaxation_is_strictly_looser_at_representative_point():
    assert univariate.relaxation_value(F(2, 5), F(3, 5)) == F(107, 125)
    assert M(F(2, 5), F(3, 5)) == F(61, 75)


@pytest.mark.parametrize("p, q", random_points(20, seed=13))
def test_sanity_bounds(p, q):
    """Product law is feasible (lower bound); Markov on S gives an upper bound."""
    m = M(p, q)
    product_value = sum(v for x, v in model.product_distribution(p, q).items() if sum(x) >= 3)
    assert product_value <= m <= min(F(1), (2 * p + 3 * q) / 3)


def test_not_symmetric_in_p_and_q():
    assert M(F(2, 5), F(3, 5)) == F(61, 75)
    assert M(F(3, 5), F(2, 5)) == F(19, 25)


@pytest.mark.parametrize("k", range(0, 61))
def test_edge_p_zero(k):
    """p = 0 forces X1 = X2 = 0, leaving P(X3 = X4 = X5 = 1) for three pairwise
    independent q-bits; Theorem 4.1 of Ramachandra-Natarajan (n = k = 3) gives
    q^2 for q <= 1/2 and 1 - 3q + 3q^2 for q >= 1/2."""
    q = F(k, 60)
    expected = q * q if q <= F(1, 2) else 1 - 3 * q + 3 * q * q
    assert M(0, q) == expected


@pytest.mark.parametrize("k", range(0, 61))
def test_edge_q_one(k):
    """q = 1 forces X3 = X4 = X5 = 1, so S >= 3 surely."""
    assert M(F(k, 60), 1) == 1
