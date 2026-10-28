import random
from fractions import Fraction as F
from math import comb

from pwbound import model
from pwbound.rational import rank


def random_rationals(seed, count, denominator=97):
    rng = random.Random(seed)
    return [F(rng.randint(0, denominator), denominator) for _ in range(count)]


def binomial_reduced(p, q):
    """Law of (A, B) under mutual independence: Bin(2, p) x Bin(3, q)."""
    return {(a, b): comb(2, a) * p**a * (1 - p) ** (2 - a) * comb(3, b) * q**b * (1 - q) ** (3 - b)
            for a, b in model.STATES12}


def apply(matrix, vector):
    return [sum(r * v for r, v in zip(row, vector)) for row in matrix]


def test_reduced_matrix_has_full_row_rank():
    assert rank(model.reduced_matrix()) == 6


def test_full_matrix_has_full_row_rank():
    assert rank(model.full_matrix()) == 16


def test_product_distribution_satisfies_full_constraints():
    ps = random_rationals(1, 10)
    for p, q in zip(ps[::2], ps[1::2]):
        mu = model.product_distribution(p, q)
        assert apply(model.full_matrix(), [mu[x] for x in model.STATES32]) == list(model.full_rhs(p, q))


def test_binomial_law_satisfies_reduced_constraints():
    # catches wrong coefficients such as 6q^2 or 6pq in reduced_rhs
    ps = random_rationals(2, 10)
    for p, q in zip(ps[::2], ps[1::2]):
        pi = binomial_reduced(p, q)
        assert apply(model.reduced_matrix(), [pi[s] for s in model.STATES12]) == list(model.reduced_rhs(p, q))


def test_project_of_product_is_binomial():
    p, q = F(2, 7), F(5, 9)
    assert model.project_primal(model.product_distribution(p, q)) == binomial_reduced(p, q)


def test_lift_then_project_is_identity():
    pi = binomial_reduced(F(1, 3), F(3, 4))
    assert model.project_primal(model.lift_primal(pi)) == pi


def test_lift_of_reduced_feasible_point_is_full_feasible():
    p, q = F(3, 10), F(7, 10)
    mu = model.lift_primal(binomial_reduced(p, q))
    assert apply(model.full_matrix(), [mu[x] for x in model.STATES32]) == list(model.full_rhs(p, q))


def test_lift_dual_agrees_with_reduced_dual_pointwise_and_in_value():
    y = (F(1, 2), F(-3, 7), F(5, 3), F(2, 9), F(-1, 4), F(7, 5))
    u0, u, uu = model.lift_dual(y)
    for x in model.STATES32:
        a, b = model.group_counts(x)
        assert model.full_dual_poly(u0, u, uu, x) == model.dual_poly12(y, a, b)
    p, q = F(1, 6), F(4, 5)
    assert model.full_dual_value(u0, u, uu, p, q) == model.reduced_dual_value(y, p, q)


def test_objective_sizes():
    assert sum(model.full_objective()) == 16
    assert sum(model.reduced_objective()) == 6
