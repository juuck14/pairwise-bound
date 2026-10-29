"""Exploration runs behind notes/proofs/exactness.md and notes/research_reassessment.md.

    python -m scripts.explore_exactness <name> [<name> ...]     (or: all)

Float HiGHS and random instances with fixed seeds: these are explorations, not proofs.
Names: certainty-random, certainty-boundary, certainty-minimal, regimes, split,
positivstellensatz, productform, scaled, twovalued, twovalued-reduced, gap, k2, decomp, kernels.
"""
import itertools
import math
import sys
from collections import Counter

import numpy as np
from scipy.optimize import linprog

from pwbound import general as G


def lp_feasible(A, b, bounds=(0, None)):
    return linprog(np.zeros(A.shape[1]), A_eq=A, b_eq=b, bounds=bounds, method="highs").status == 0


def states_matrix(n, pred=None):
    states = [x for x in itertools.product((0, 1), repeat=n) if pred is None or pred(x)]
    return states, np.array([G.moment_vector(x) for x in states], float).T


def moment_rhs(p, P=None):
    n = len(p)
    pairs = list(itertools.combinations(range(n), 2))
    return np.array([1.0] + list(p) + [(P[i][j] if P is not None else p[i] * p[j]) for i, j in pairs])


def certain_feasible(p, k, P=None):
    _, A = states_matrix(len(p), lambda x: sum(x) >= k)
    return lp_feasible(A, moment_rhs(p, P))


# ------------------------------------------------------------------ certainty

def certainty_random():
    """Conjecture C on random p pushed towards the boundary (n = 4..6, all k)."""
    rng = np.random.default_rng(1)
    bad = tested = 0
    for n in (4, 5, 6):
        for k in range(1, n + 1):
            for _ in range(150):
                p = rng.uniform(0, 1, n)
                if min(p.sum() - x for x in p) <= 0:
                    continue
                target = k + rng.uniform(-0.15, 0.15)
                for _ in range(50):
                    lo = min(p.sum() - x for x in p)
                    p = np.clip(p * (target / lo) if lo > 0 else p, 0, 1)
                free = [x for x in p if x < 1 - 1e-12]
                lo = min(p.sum() - x for x in free) if free else np.inf
                val = G.float_tight(p, k)[0]
                tested += 1
                if (lo >= k - 1e-9) != (val > 1 - 1e-7):
                    bad += 1
    print(f"certainty-random: tested {tested}, mismatches {bad}")


def certainty_boundary():
    """Points with min_j LOO_j = k + delta, delta in {+1e-3, -1e-3, 0} (n = 4..7)."""
    rng = np.random.default_rng(7)
    stats = Counter()
    for n in (4, 5, 6, 7):
        for k in range(1, n):
            for _ in range(60 if n < 7 else 15):
                p = np.sort(rng.uniform(0.05, 0.999, n))
                for delta in (1e-3, -1e-3, 0.0):
                    rest, need = p[:-1], k + delta
                    f = lambda t: np.clip(1 - (1 - rest) * t, 0, 1).sum() - need
                    if f(0.0) < 0 or f(1e6) > 0:
                        continue
                    a, b = 0.0, 1e6
                    for _ in range(200):
                        m = (a + b) / 2
                        a, b = (m, b) if f(m) > 0 else (a, m)
                    newrest = np.clip(1 - (1 - rest) * a, 0, 1)
                    q = np.concatenate([newrest, [max(p[-1], newrest.max())]])
                    loo = [q.sum() - x for x in q if x < 1 - 1e-12]
                    lo = min(loo) if loo else np.inf
                    val = G.float_tight(q, k)[0]
                    if lo >= k - 1e-12:
                        stats["inside_ok" if val > 1 - 1e-7 else "inside_bad"] += 1
                    elif val < 1 - 1e-9:
                        stats["outside_ok"] += 1
                    else:
                        stats["outside_within_tolerance"] += 1
    print("certainty-boundary:", dict(stats))


def certainty_minimal():
    """Minimal points (two largest equal M, S1 - M = k) and points just outside (n = 5..9)."""
    rng = np.random.default_rng(99)
    res = Counter()
    for n in (5, 6, 7, 8, 9):
        for k in range(2, n - 1):
            for _ in range(40 if n <= 7 else 12):
                p = np.sort(rng.uniform(0, 1, n) ** rng.choice([0.3, 1, 3]))
                r = p[: n - 2]
                need = k - r.sum()
                if r.max() <= need < 1:
                    M = need
                else:
                    M = rng.uniform(k / (n - 1), 1.0)
                    r = r / r.sum() * (k - M)
                    if r.max() > M:
                        continue
                q = np.concatenate([r, [M, M]])
                res["minimal_feasible" if certain_feasible(q, k) else "minimal_infeasible"] += 1
                q2 = q.copy()
                q2[1:n - 2] *= 0.99
                if q2.sum() - q2.max() < k - 1e-6:
                    res["outside_feasible" if certain_feasible(q2, k) else "outside_infeasible"] += 1
    print("certainty-minimal:", dict(res))


# ------------------------------------------------------------------ BP regimes

def regimes():
    """Exactness by BP regime against the criteria (n = 4..6, heterogeneous p)."""
    rng = np.random.default_rng(11)
    cnt = Counter()
    for n in (4, 5, 6):
        for k in range(2, n + 1):
            for _ in range(200):
                base, spread = rng.uniform(0.02, 0.98), rng.choice([0.01, 0.05, 0.2, 0.6])
                p = np.clip(base + spread * rng.uniform(-1, 1, n), 0.005, 0.995)
                bp, verdict, reason = G.bp_exactness_verdict(list(p), k)
                exact = abs(G.float_tight(p, k)[0] - float(bp)) < 1e-7
                tag = reason.split(":")[0] if verdict == "not exact" else "open"
                cnt[(tag, exact)] += 1
    for key in sorted(cnt, key=str):
        print("regimes:", key, cnt[key])


def split_ok(p, K):
    n = len(p)
    for r in range(1, n // 2 + 1):
        for G1 in itertools.combinations(range(n), r):
            G2 = [i for i in range(n) if i not in G1]
            a1, b1 = sum(p[i] for i in G1), sum(p[i] for i in G2)
            a2 = 2 * sum(p[i] * p[j] for i, j in itertools.combinations(G1, 2))
            b2 = 2 * sum(p[i] * p[j] for i, j in itertools.combinations(G2, 2))
            pts = [(a, b) for a in range(len(G1) + 1) for b in range(len(G2) + 1) if a + b in K]
            A = np.array([[1] * len(pts), [a for a, _ in pts], [b for _, b in pts],
                          [a * (a - 1) for a, _ in pts], [b * (b - 1) for _, b in pts],
                          [a * b for a, b in pts]], float)
            if not lp_feasible(A, np.array([1, a1, b1, a2, b2, a1 * b1])):
                return False
    return True


def split():
    """All 2-partition aggregated tests vs exactness, when E1-E4 do not decide."""
    import random
    rng = random.Random(5)
    cnt = Counter()
    for _ in range(6000):
        n, k = rng.choice([4, 5, 6]), None
        k = rng.randint(2, n)
        p = [rng.random() ** rng.choice([0.5, 1, 2]) for _ in range(n)]
        bp, verdict, _ = G.bp_exactness_verdict(p, k)
        if bp == 1 or verdict != "open":
            continue
        K = set(sorted(G.bp_optimum(n, k, *G.moments(p))[1][0]))
        exact = G.float_tight(p, k)[0] > float(bp) - 1e-8
        cnt[(n, "split-ok" if split_ok(p, K) else "split-fails", "exact" if exact else "not exact")] += 1
    for key in sorted(cnt):
        print("split:", key, cnt[key])


# ------------------------------------------------------------------ failed proof routes

def positivstellensatz():
    """Do the 2n conditional-mean inequalities cut out conv{phi(x): |x| >= k} for general
    (non-product) moment points? Random laws on the cube."""
    rng = np.random.default_rng(4)
    for n, k in ((5, 2), (5, 3), (6, 2), (6, 3), (6, 4)):
        states, A = states_matrix(n)
        _, Ak = states_matrix(n, lambda x: sum(x) >= k)
        tried = found = 0
        for _ in range(3000):
            w = rng.dirichlet(np.ones(len(states)) * rng.choice([0.05, 0.2, 1.0]))
            b = A @ w
            p, P = b[1:1 + n], b[1 + n:]
            Pm = np.zeros((n, n))
            for r, (i, j) in enumerate(itertools.combinations(range(n), 2)):
                Pm[i, j] = Pm[j, i] = P[r]
            ok = all(p[j] + Pm[j].sum() - k * p[j] >= -1e-12 and
                     (p.sum() - k) - (p[j] + Pm[j].sum() - k * p[j]) >= -1e-12 for j in range(n))
            if not ok:
                continue
            tried += 1
            found += not lp_feasible(Ak, b)
        print(f"positivstellensatz: n={n} k={k} points satisfying the inequalities {tried}, not representable {found}")


def productform():
    """Higher moments mu_T = lam_|T| prod q_T on the ball |y| <= m at boundary points."""
    rng = np.random.default_rng(12)
    cnt = Counter()
    for n in (5, 6, 7, 8):
        for m in range(3, n - 1):
            for _ in range(60):
                q = np.sort(rng.uniform(0.05, 1, n) ** rng.choice([0.5, 1, 2]))
                mu = rng.uniform(0.02, 0.6)
                need = m - 1 - mu
                rest = q[2:]
                if need <= 0 or need > len(rest):
                    continue
                rest = rest / rest.sum() * need
                if rest.max() > 1 or rest.min() < mu:
                    continue
                qq = np.concatenate([[mu, mu], rest])
                subsets = [T for s in range(m + 1) for T in itertools.combinations(range(n), s)]
                a0, rows = [], []
                for y in subsets:
                    rest_idx = [i for i in range(n) if i not in y]
                    py = np.prod([qq[i] for i in y]) if y else 1.0
                    base, coef = 0.0, np.zeros(m - 2)
                    for t in range(m - len(y) + 1):
                        for U in itertools.combinations(rest_idx, t):
                            val = (-1) ** t * py * (np.prod([qq[i] for i in U]) if U else 1.0)
                            if len(y) + t <= 2:
                                base += val
                            else:
                                coef[len(y) + t - 3] += val
                    a0.append(base)
                    rows.append(coef)
                r = linprog(np.zeros(m - 2), A_ub=-np.array(rows), b_ub=np.array(a0),
                            bounds=[(None, None)] * (m - 2), method="highs")
                cnt[r.status == 0] += 1
    print("productform: feasible ->", dict(cnt))


def scaled():
    """Marginals p, pairs c p_i p_j (c != 1): is certainty decided by the 2n conditional means?"""
    rng = np.random.default_rng(17)
    cnt = Counter()
    for n in (4, 5, 6):
        _, A = states_matrix(n)
        for k in range(1, n):
            for _ in range(150):
                p = rng.uniform(0.05, 0.95, n)
                c = rng.uniform(0.3, 1.8)
                P = c * np.outer(p, p)
                if not lp_feasible(A, moment_rhs(p, P)):
                    cnt["not realisable"] += 1
                    continue
                S1 = p.sum()
                cond = all(1 + c * (S1 - p[j]) >= k - 1e-12 and
                           (S1 - p[j]) * (1 - c * p[j]) / (1 - p[j]) >= k - 1e-12 for j in range(n))
                cnt[(cond, certain_feasible(p, k, P))] += 1
    print("scaled: (conditions hold, certain law exists) ->", dict(cnt))


def twovalued():
    """Two-valued certainty: B ~ law maximising P(B = beta), A = k - B below, 1-D moment fit on top."""
    rng = np.random.default_rng(2)
    cnt = Counter()
    for _ in range(20000):
        alpha, beta = int(rng.integers(1, 9)), int(rng.integers(2, 9))
        k = int(rng.integers(1, alpha + beta))
        b = rng.uniform(0.01, 0.999)
        a = (k - (beta - 1) * b) / alpha
        if not 0 < a <= b:
            continue
        best = None
        for supp in itertools.combinations(range(beta + 1), 3):
            if beta not in supp:
                continue
            M = np.array([[1, 1, 1], list(supp), [s * (s - 1) for s in supp]], float)
            if abs(np.linalg.det(M)) < 1e-12:
                continue
            w = np.linalg.solve(M, [1, beta * b, beta * (beta - 1) * b * b])
            if w.min() >= -1e-12 and (best is None or w[-1] > best[1][-1]):
                best = (supp, w)
        supp, w = best
        okA = all(0 <= k - s <= alpha for s, x in zip(supp, w) if s < beta and x > 1e-12)
        r1 = alpha * a - sum(x * (k - s) for s, x in zip(supp, w) if s < beta)
        r2 = alpha * (alpha - 1) * a * a - sum(x * (k - s) * (k - s - 1) for s, x in zip(supp, w) if s < beta)
        L, U, top = max(0, k - beta), alpha, w[-1]
        mu, f2 = r1 / top, r2 / top
        lo_x = math.floor(mu)
        hi_x = min(lo_x + 1, U)
        lower = lo_x * (lo_x - 1) + (mu - lo_x) * (hi_x * (hi_x - 1) - lo_x * (lo_x - 1)) if hi_x > lo_x else lo_x * (lo_x - 1)
        upper = L * (L - 1) + (mu - L) * ((U * (U - 1) - L * (L - 1)) / (U - L)) if U > L else L * (L - 1)
        cnt[bool(okA and L - 1e-12 <= mu <= U + 1e-12 and lower - 1e-9 <= f2 <= upper + 1e-9)] += 1
    print("twovalued: construction works ->", dict(cnt))


def twovalued_reduced():
    """Proposition C3: at a two-valued minimal point the certainty question is the joint
    feasibility of two 1-D moment problems (W) and (N) sharing omega = P(all b's = 1)."""
    import random
    rng = random.Random(1)
    cnt = Counter()
    for _ in range(20000):
        alpha, beta = rng.randint(1, 10), rng.randint(2, 10)
        n = alpha + beta
        k = rng.randint(1, n - 1)
        b = rng.uniform(0.001, 0.999)
        a = (k - (beta - 1) * b) / alpha
        if not 0 < a <= b:
            continue
        s_lo, s_hi = max(0, k - alpha), min(k, beta - 1)
        Sw = list(range(s_lo, s_hi + 1)) + [beta]
        Sn = list(range(max(0, k - beta), alpha + 1))
        nw, nn = len(Sw), len(Sn)
        C = k - alpha * a * a + 2 * b * (k - beta) - (beta - 1) * b * b
        rows = [[1] * nw + [0] * nn, Sw + [0] * nn, [s * (s - 1) for s in Sw] + [0] * nn]
        rhs = [1, beta * b, beta * (beta - 1) * b * b]
        for coeffs, shift, r in (([1] * nn, 1, 0), (Sn, k - beta, b),
                                  ([x * (x - 1) for x in Sn], (k - beta) * (k - beta - 1), C)):
            row = [0] * nw + list(coeffs)
            row[nw - 1] = -shift
            rows.append(row)
            rhs.append(r)
        cnt[lp_feasible(np.array(rows, float), np.array(rhs, float))] += 1
    print("twovalued-reduced: (W) and (N) jointly feasible ->", dict(cnt))


def gap():
    """Proposition G: lower bounds on BP - P in the {0,k,n} regime (crude and best linear
    combination of the F_j) against the true gap (HiGHS)."""
    from fractions import Fraction as Fr
    import random

    def bounds(p, k):
        n = len(p)
        s1, s2 = (float(x) for x in G.moments(p))
        sig = lambda s: s * (n + k - s) / (k * n) - (1.0 if s >= k else 0.0)
        delta = [float(d) for d in G.rigidity_defects(p, k)]
        states = [x for x in itertools.product((0, 1), repeat=n) if sum(x) not in (0, k, n)]
        Fm = np.array([[x[j] * (sum(x) - k) - sum(x) * (sum(x) - k) / n for j in range(n)] for x in states])
        sg = np.array([sig(sum(x)) for x in states])
        r = linprog(-np.array(delta), A_ub=np.vstack([Fm, -Fm]), b_ub=np.concatenate([sg, sg]),
                    bounds=[(None, None)] * n, method="highs")
        true = float(G.bp_value(p, k)) - G.float_tight(p, k)[0]
        return true, -r.fun, float(G.rigidity_gap_lower_bound(p, k))

    for pp, qq in ((Fr(3, 5), Fr(4, 5)), (Fr(1, 2), Fr(5, 8)), (Fr(2, 5), Fr(3, 5)), (Fr(2, 7), Fr(5, 7))):
        print("gap: (p,q)=(%s,%s) true %.5f  best-linear %.5f  prop-G %.5f" % ((pp, qq) + bounds([pp] * 2 + [qq] * 3, 3)))
    rng = random.Random(3)
    for _ in range(6):
        p = [Fr(rng.randint(40, 75), 100) for _ in range(6)]
        if [sorted(l) for l in G.bp_optimum(6, 3, *G.moments(p))[1]] != [[0, 3, 6]]:
            continue
        print("gap: n=6 p=%s true %.5f  best-linear %.5f  prop-G %.5f" % (([str(x) for x in p],) + bounds(p, 3)))


# ------------------------------------------------------------------ misc

def k2():
    """k = 2 in the {0,1,2} BP regime: simple candidate formulas for P(n,2,p)."""
    rng = np.random.default_rng(8)
    cnt = Counter()
    for n in (3, 4, 5, 6):
        for _ in range(300):
            p = rng.uniform(0, 1, n) ** rng.choice([0.5, 1, 2])
            s1, s2 = (float(x) for x in G.moments(p))
            if not (1 - s1 + s2 >= 0 and s1 - 2 * s2 >= 0):
                continue
            T = G.float_tight(p, 2)[0]
            viol = [x * (s1 - x - 1) for x in p]
            c1 = s2 - 2 * max(0, max(viol))
            c2 = s2 - 2 * sum(max(0, v) for v in viol)
            cnt[(n, abs(T - c1) < 1e-8, abs(T - c2) < 1e-8)] += 1
    for key in sorted(cnt):
        print("k2: (n, max-formula ok, sum-formula ok)", key, cnt[key])


def decomp():
    """Rank-one K_k-decomposability (condition (II)) vs vertex capacity conditions."""
    rng = np.random.default_rng(41)
    cnt = Counter()
    for n in (5, 6, 7, 8):
        for k in range(3, n - 1):
            pairs = list(itertools.combinations(range(n), 2))
            subs = list(itertools.combinations(range(n), k))
            A = np.array([[1.0 if (i in T and j in T) else 0.0 for T in subs] for i, j in pairs])
            for _ in range(200 if n < 8 else 60):
                p = rng.uniform(0, 1, n) ** rng.choice([0.3, 1, 3])
                S1 = p.sum()
                S2 = (S1 ** 2 - (p ** 2).sum()) / 2
                cap = all(x * (S1 - x) / (k - 1) <= S2 / (k * (k - 1) / 2) + 1e-12 for x in p)
                d = lp_feasible(A, np.array([p[i] * p[j] for i, j in pairs]))
                cnt[(cap, d)] += 1
    print("decomp: (capacity ok, decomposable) ->", dict(cnt))


def kernels():
    """Lemma L1 at n = 8 (exact ranks): exceptional 3-layer unions."""
    n = 8
    bad = {K: G.layer_kernel_dim(n, K) for K in itertools.combinations(range(n + 1), 3)}
    print("kernels n=8: not full ->", {K: d for K, d in bad.items() if d})


RUNS = {"certainty-random": certainty_random, "certainty-boundary": certainty_boundary,
        "certainty-minimal": certainty_minimal, "regimes": regimes, "split": split,
        "positivstellensatz": positivstellensatz, "productform": productform, "scaled": scaled,
        "twovalued": twovalued, "twovalued-reduced": twovalued_reduced, "gap": gap, "k2": k2, "decomp": decomp, "kernels": kernels}

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    for name in (RUNS if names == ["all"] else names):
        RUNS[name]()
