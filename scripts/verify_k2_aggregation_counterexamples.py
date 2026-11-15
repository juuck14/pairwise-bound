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


def exact_three_run_value(p):
    """Exact feasible law supported on atoms with <= 3 runs (sorted p), built on the HiGHS support of the
    restricted LP; returns its P(S >= 2) as a Fraction (a lower bound on Pbar)."""
    from pwbound.runs_lp import atoms_with_runs
    from scipy.sparse import lil_matrix
    n = len(p)
    atoms = atoms_with_runs(n, 3)
    pairs = list(itertools.combinations(range(n), 2))
    pos = {pr: 1 + n + t for t, pr in enumerate(pairs)}
    A = lil_matrix((1 + n + len(pairs), len(atoms)))
    for c, x in enumerate(atoms):
        A[0, c] = 1
        ones = [i for i in range(n) if x[i]]
        for i in ones:
            A[1 + i, c] = 1
        for i, j in itertools.combinations(ones, 2):
            A[pos[(i, j)], c] = 1
    pf = [float(x) for x in p]
    b = np.array([1.0] + pf + [pf[i] * pf[j] for i, j in pairs])
    res = linprog(-np.array([1.0 if sum(x) >= K else 0.0 for x in atoms]), A_eq=A.tocsr(), b_eq=b,
                  bounds=(0, None), method="highs-ds")
    sup = [c for c in range(len(atoms)) if res.x[c] > 1e-11]
    rhs = [Fr(1)] + list(p) + [p[i] * p[j] for i, j in pairs]
    rows = [[1] * len(sup)] + [[atoms[c][i] for c in sup] for i in range(n)] + \
           [[atoms[c][i] * atoms[c][j] for c in sup] for i, j in pairs]
    M = [rows[i] + [-rhs[i]] for i in range(len(rows))]
    for v in nullspace(M):
        if v[-1] != 0:
            x = [t / v[-1] for t in v][:-1]
            if min(x) >= 0:
                return sum(x[t] for t, c in enumerate(sup) if sum(atoms[c]) >= K)
    raise RuntimeError("no exact nonnegative law on the support")


def check_three_runs(name, p):
    """R3' at one point: exact <=3-run law value L equals the exact dual bound U, so Pbar = L = U."""
    U = exact_dual_bound(p)
    L = exact_three_run_value(p)
    print(f"{name}: <=3-run law value {float(L):.12f}, dual bound {float(U):.12f}, equal: {L == U}")
    return L == U


def exact_segment_value(p, r=3):
    """Exact feasible law that mixes segment-design columns (pwbound.segment_lp), built on the HiGHS
    support; returns its P(S >= 2) as a Fraction (a lower bound on Pbar)."""
    from pwbound.segment_lp import segment_columns
    from scipy.sparse import csc_matrix
    n = len(p)
    pairs = list(itertools.combinations(range(n), 2))
    pos = {pr: 1 + n + t for t, pr in enumerate(pairs)}
    cols = list(segment_columns(n, r))

    def column_exact(segs):
        marg, within = {}, {}
        for a, b, c in segs:
            L = b - a + 1
            for i in range(a, b + 1):
                marg[i] = Fr(c, L)
            for i, j in itertools.combinations(range(a, b + 1), 2):
                within[(i, j)] = Fr(c * (c - 1), L * (L - 1))
        ent = {0: Fr(1)}
        for i, v in marg.items():
            ent[1 + i] = v
        for i, j in itertools.combinations(sorted(marg), 2):
            v = within.get((i, j), marg[i] * marg[j])
            if v:
                ent[pos[(i, j)]] = v
        return ent

    data, rows, cids = [], [], []
    for cid, segs in enumerate(cols):
        for row, v in column_exact(segs).items():
            data.append(float(v)); rows.append(row); cids.append(cid)
    A = csc_matrix((data, (rows, cids)), shape=(1 + n + len(pairs), len(cols)))
    pf = [float(x) for x in p]
    b = np.array([1.0] + pf + [pf[i] * pf[j] for i, j in pairs])
    cost = [-1.0 if sum(c for _, _, c in segs) >= K else 0.0 for segs in cols]
    res = linprog(cost, A_eq=A, b_eq=b, bounds=(0, None), method="highs-ds")
    sup = [c for c in range(len(cols)) if res.x[c] > 1e-11]
    rhs = [Fr(1)] + list(p) + [p[i] * p[j] for i, j in pairs]
    ents = [column_exact(cols[c]) for c in sup]
    M = [[e.get(row, Fr(0)) for e in ents] + [-rhs[row]] for row in range(len(rhs))]
    for v in nullspace(M):
        if v[-1] != 0:
            x = [t / v[-1] for t in v][:-1]
            if min(x) >= 0:
                return sum(x[t] for t, c in enumerate(sup) if sum(cc for _, _, cc in cols[c]) >= K)
    raise RuntimeError("no exact nonnegative mixture on the support")


def exact_optimal_dual(p,K=2):
    """Exact optimal certificate q: solve q(x)=g(x) on the support of the full-LP optimal law (exactly),
    then verify q(x) >= g(x) on all x. Returns (U, ok)."""
    n=len(p); pf=[float(x) for x in p]; pairs=list(itertools.combinations(range(n),2))
    states=list(itertools.product((0,1),repeat=n))
    A=np.array([[1]+list(x)+[x[i]*x[j] for i,j in pairs] for x in states],float).T
    b=np.array([1.0]+pf+[pf[i]*pf[j] for i,j in pairs])
    r=linprog(-np.array([1.0 if sum(x)>=K else 0 for x in states]),A_eq=A,b_eq=b,bounds=(0,None),method='highs-ds',
              options={'primal_feasibility_tolerance':1e-10,'dual_feasibility_tolerance':1e-10})
    sup=[states[i] for i in range(len(states)) if r.x[i]>1e-12]
    # also include states whose reduced cost is ~0 (tight) to pin down q
    d=-r.eqlin.marginals; slack=[d[0]+sum(d[1+i]*x[i] for i in range(n))+sum(d[1+n+t]*x[i]*x[j] for t,(i,j) in enumerate(pairs))-(1 if sum(x)>=K else 0) for x in states]
    tight=[states[i] for i in range(len(states)) if abs(slack[i])<1e-9]
    rows=[[Fr(1)]+[Fr(v) for v in x]+[Fr(x[i]*x[j]) for i,j in pairs]+[-Fr(1 if sum(x)>=K else 0)] for x in tight]
    basis=nullspace(rows)
    sols=[v for v in basis if v[-1]!=0]
    if len(basis)!=1 or not sols: return None, False, len(basis)
    q=[t/sols[0][-1] for t in sols[0]][:-1]
    val=lambda x: q[0]+sum(q[1+i]*x[i] for i in range(n))+sum(q[1+n+t]*x[i]*x[j] for t,(i,j) in enumerate(pairs))
    ok=all(val(x)>=(1 if sum(x)>=K else 0) for x in states)
    U=q[0]+sum(q[1+i]*p[i] for i in range(n))+sum(q[1+n+t]*p[i]*p[j] for t,(i,j) in enumerate(pairs))
    return U, ok, 1
