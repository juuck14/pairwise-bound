"""Exact (rational) certificates that grouped aggregation is not exact for Pbar(n,2,p).

C36: n = 8, every partition of the sorted marginals into <= 4 CONTIGUOUS groups is strictly above Pbar.
C37: n = 9, every partition into <= 4 classes (any, not only contiguous; all 11,051) is strictly above Pbar.

For each point: an exact dual certificate (quadratic q >= 1{|x|>=2} on {0,1}^n, rational coefficients)
gives Pbar <= U, and for every partition an exact feasible law of group counts gives a value >= L;
the claim is L > U. Run: python -m scripts.verify_k2_aggregation_counterexamples   (about 5 minutes)
"""
import itertools
import math
import sys
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog

from pwbound.aggregation import contiguous_partitions
from pwbound.rational import nullspace

K = 2


def set_partitions(n, max_blocks):
    def rec(i, blocks):
        if i == n:
            yield [b[:] for b in blocks]
            return
        for b in blocks:
            b.append(i)
            yield from rec(i + 1, blocks)
            b.pop()
        if len(blocks) < max_blocks:
            blocks.append([i])
            yield from rec(i + 1, blocks)
            blocks.pop()
    yield from rec(0, [])


def exact_dual_bound(p):
    n = len(p)
    pf = [float(x) for x in p]
    pairs = list(itertools.combinations(range(n), 2))
    states = list(itertools.product((0, 1), repeat=n))
    res = linprog([1] + pf + [pf[i] * pf[j] for i, j in pairs],
                  A_ub=[[-v for v in [1] + list(x) + [x[i] * x[j] for i, j in pairs]] for x in states],
                  b_ub=[-(1 if sum(x) >= K else 0) for x in states], bounds=(None, None), method="highs-ds")
    q = [Fr(c).limit_denominator(12) for c in res.x]
    val = lambda x: q[0] + sum(q[1 + i] * x[i] for i in range(n)) + sum(
        q[1 + n + t] * x[i] * x[j] for t, (i, j) in enumerate(pairs))
    assert all(val(x) >= (1 if sum(x) >= K else 0) for x in states), "rounded dual is not feasible"
    return q[0] + sum(q[1 + i] * p[i] for i in range(n)) + sum(q[1 + n + t] * p[i] * p[j] for t, (i, j) in enumerate(pairs))


def exact_feasible_value(p, part):
    sizes = [len(g) for g in part]
    P = [sum(p[i] for i in g) for g in part]
    E2 = [sum(p[i] * p[j] for i, j in itertools.combinations(g, 2)) for g in part]
    st = list(itertools.product(*[range(s + 1) for s in sizes]))
    rows, rhs = [[1] * len(st)], [Fr(1)]
    for a in range(len(part)):
        rows.append([s[a] for s in st]); rhs.append(P[a])
        if sizes[a] >= 2:
            rows.append([math.comb(s[a], 2) for s in st]); rhs.append(E2[a])
    for a, b in itertools.combinations(range(len(part)), 2):
        rows.append([s[a] * s[b] for s in st]); rhs.append(P[a] * P[b])
    rr = linprog([-(1 if sum(s) >= K else 0) for s in st], A_eq=np.array(rows, float),
                 b_eq=np.array([float(v) for v in rhs]), bounds=(0, None), method="highs-ds")
    sup = [j for j in range(len(st)) if rr.x[j] > 1e-11]
    M = [[rows[i][j] for j in sup] + [-rhs[i]] for i in range(len(rows))]
    for v in nullspace(M):
        if v[-1] != 0:
            x = [t / v[-1] for t in v][:-1]
            if min(x) >= 0:
                return sum(x[t] for t, j in enumerate(sup) if sum(st[j]) >= K)
    raise RuntimeError("no exact nonnegative solution on the HiGHS support")


def check(name, p, partitions):
    U = exact_dual_bound(p)
    L = min(exact_feasible_value(p, part) for part in partitions)
    ok = L > U
    print(f"{name}: Pbar <= U = {U} ({float(U):.10f}); min exact aggregated value L = {float(L):.10f}; "
          f"L - U = {float(L - U):.3e} -> {'CONFIRMED' if ok else 'NOT confirmed'}")
    return ok


def main():
    p8 = [Fr(s) for s in ["0.0055", "0.0108", "0.0318", "0.034", "0.0647", "0.3735", "0.3831", "0.5845"]]
    p9 = [Fr(s) for s in ["0.0081", "0.024", "0.0348", "0.0384", "0.0433", "0.0446", "0.3587", "0.3903", "0.5778"]]
    a = check("C36 (n=8, <=4 contiguous groups)", p8, list(contiguous_partitions(8, 4)))
    b = check("C37 (n=9, <=4 arbitrary classes)", p9, list(set_partitions(9, 4)))
    sys.exit(0 if a and b else 1)


if __name__ == "__main__":
    main()
