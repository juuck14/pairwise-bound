"""Pairwise independent Bernoulli vectors with arbitrary marginals p (general n).

Tools for notes/proofs/exactness.md (when is the two-moment bound exact?):
  * moments S1, S2 and the leave-one-out sums sum_{l != j} p_l
  * the univariate Boros-Prekopa LP: exact optimum and all optimal vertex laws
  * exact verification of a joint law on {0,1}^n
  * the dimension of the quadratics vanishing on a union of layers
  * explicit laws used in proofs, exact reconstruction of a law from a support
  * a float HiGHS solver of the 2^n LP (exploration and cross-checks only)

Everything except float_* is exact (Fraction).
"""
from fractions import Fraction
from itertools import combinations, product
from math import comb

from .rational import rank


def as_fractions(p):
    return [Fraction(x) for x in p]


def moments(p):
    """S1 = sum p_i, S2 = sum_{i<j} p_i p_j."""
    p = as_fractions(p)
    s1 = sum(p)
    s2 = sum(a * b for a, b in combinations(p, 2))
    return s1, s2


def leave_one_out(p):
    """[sum_{l != j} p_l for j]: E[S | X_j = 0] (and E[S | X_j = 1] - 1) under pairwise independence."""
    p = as_fractions(p)
    s1 = sum(p)
    return [s1 - x for x in p]


# ------------------------------------------------------------ univariate LP

def _solve3(rows, rhs):
    from .rational import solve
    return solve(rows, rhs)


def bp_optimum(n, k, s1, s2):
    """max P(xi >= k) over laws of xi on {0..n} with E xi = s1, E C(xi,2) = s2.

    Returns (value, laws) where laws are all optimal *vertex* laws as dicts
    {s: v_s} with v_s > 0 (support size <= 3). None if infeasible.
    """
    s1, s2 = Fraction(s1), Fraction(s2)
    feasible = []
    if n <= 1:                         # xi in {0,1}: C(xi,2) = 0, so the law is (1-s1, s1)
        if s2 != 0 or not 0 <= s1 <= 1 or (n == 0 and s1 != 0):
            return None
        feasible.append({s: x for s, x in ((0, 1 - s1), (1, s1)) if x != 0})
    for basis in combinations(range(n + 1), 3):
        v = _solve3([[1, 1, 1], list(basis), [comb(s, 2) for s in basis]], [1, s1, s2])
        if v is None or min(v) < 0:
            continue
        law = {s: x for s, x in zip(basis, v) if x != 0}
        feasible.append(law)
    if not feasible:
        return None
    value = max(sum(x for s, x in law.items() if s >= k) for law in feasible)
    laws = []
    for law in feasible:
        if sum(x for s, x in law.items() if s >= k) == value and law not in laws:
            laws.append(law)
    return value, laws


def bp_value(p, k):
    n = len(p)
    return bp_optimum(n, k, *moments(p))[0]


# ------------------------------------------------------------ layers

def moment_vector(x):
    """(1, x_1..x_n, x_i x_j for i<j) for a 0/1 vector x."""
    n = len(x)
    return [1] + list(x) + [x[i] * x[j] for i, j in combinations(range(n), 2)]


def layer_kernel_dim(n, layers):
    """Dimension of {multilinear quadratics vanishing on all x with |x| in layers}.

    0 means the moment vectors of those states affinely span R^(n + C(n,2)).
    """
    rows = []
    for s in layers:
        for ones in combinations(range(n), s):
            x = [1 if i in ones else 0 for i in range(n)]
            rows.append(moment_vector(x))
    return 1 + n + comb(n, 2) - rank(rows)


# ------------------------------------------------------------ joint laws

def verify_law(p, law):
    """Exact check that `law` ({0/1 tuple: Fraction}) is a pairwise independent law with
    marginals p. Returns the law of S = |x| as a dict; raises AssertionError otherwise."""
    p = as_fractions(p)
    n = len(p)
    assert all(len(x) == n and set(x) <= {0, 1} for x in law), "bad state"
    assert all(Fraction(w) >= 0 for w in law.values()), "negative mass"
    assert sum(law.values()) == 1, "total mass"
    for i in range(n):
        assert sum(w for x, w in law.items() if x[i]) == p[i], f"marginal {i}"
    for i, j in combinations(range(n), 2):
        assert sum(w for x, w in law.items() if x[i] and x[j]) == p[i] * p[j], f"pair {i},{j}"
    s_law = {}
    for x, w in law.items():
        if w:
            s_law[sum(x)] = s_law.get(sum(x), 0) + Fraction(w)
    return s_law


def tail(s_law, k):
    return sum(w for s, w in s_law.items() if s >= k)


def top2_complement_law(p):
    """Explicit law with S >= n-2 a.s. when sum_{l != j} p_l >= n-2 for every j with p_j < 1.

    In complements q = 1 - p, at most two of Y = 1 - X are 1:
    P(Y = e_i + e_j) = q_i q_j, P(Y = e_i) = q_i (1 - sum_{l != i} q_l), P(Y = 0) = rest.
    Returns None if some mass would be negative (i.e. the condition fails).
    """
    p = as_fractions(p)
    n = len(p)
    q = [1 - x for x in p]
    law = {}
    ones = tuple(1 for _ in range(n))

    def flip(idx):
        return tuple(0 if t in idx else 1 for t in range(n))

    for i, j in combinations(range(n), 2):
        if q[i] * q[j]:
            law[flip((i, j))] = q[i] * q[j]
    for i in range(n):
        w = q[i] * (1 - (sum(q) - q[i]))
        if w < 0:
            return None
        if w:
            law[flip((i,))] = w
    rest = 1 - sum(law.values())
    if rest < 0:
        return None
    if rest:
        law[ones] = rest
    return law


def second_moment_layer_law(p, k, rho):
    """The law of Theorem S on layers {0, 1, k}: rho is a measure on k-subsets (dict
    {tuple: Fraction}) with sum_{T >= {i,j}} rho(T) = p_i p_j. Returns the joint law, or
    None if a single-atom or the empty-atom mass would be negative."""
    p = as_fractions(p)
    n = len(p)
    law = {}
    for T, r in rho.items():
        if r < 0:
            return None
        if r:
            law[tuple(1 if i in T else 0 for i in range(n))] = Fraction(r)
    loo = leave_one_out(p)
    for i in range(n):
        w = p[i] - p[i] * loo[i] / (k - 1)
        if w < 0:
            return None
        if w:
            e = tuple(1 if t == i else 0 for t in range(n))
            law[e] = law.get(e, 0) + w
    rest = 1 - sum(law.values())
    if rest < 0:
        return None
    if rest:
        law[tuple(0 for _ in range(n))] = rest
    return law


def solve_exact_on_support(p, states):
    """Solve the pairwise-independence moment equations exactly on the given states.

    Returns a law {state: Fraction} (possibly with negative entries) or None if the
    system is inconsistent or the solution is not unique on these states.
    """
    p = as_fractions(p)
    n = len(p)
    states = [tuple(x) for x in states]
    target = [Fraction(1)] + p + [p[i] * p[j] for i, j in combinations(range(n), 2)]
    cols = [moment_vector(x) for x in states]
    m = len(target)
    # augmented system: rows = moments, columns = states
    aug = [[Fraction(cols[c][r]) for c in range(len(states))] + [target[r]] for r in range(m)]
    ncol = len(states)
    piv_cols, row = [], 0
    for col in range(ncol):
        pivot = next((r for r in range(row, m) if aug[r][col] != 0), None)
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        pv = aug[row][col]
        aug[row] = [v / pv for v in aug[row]]
        for r in range(m):
            if r != row and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [a - f * b for a, b in zip(aug[r], aug[row])]
        piv_cols.append(col)
        row += 1
    if any(aug[r][ncol] != 0 for r in range(row, m)):
        return None                       # inconsistent
    if len(piv_cols) < ncol:
        return None                       # not unique
    return {states[c]: aug[i][ncol] for i, c in enumerate(piv_cols)}


def layered_law_status(p, layers):
    """Decide exactly whether a pairwise independent law with marginals p can live on the
    union of the given layers, when the moment system on those states has at most one
    solution. Returns "none" (inconsistent, or the unique solution has a negative mass),
    "exists", or None when the system is underdetermined (not decided here)."""
    p = as_fractions(p)
    n = len(p)
    states = [tuple(1 if i in T else 0 for i in range(n))
              for s in layers for T in combinations(range(n), s)]
    if rank([moment_vector(x) for x in states]) < len(states):
        return None
    sol = solve_exact_on_support(p, states)
    if sol is None:
        return "none"
    return "none" if min(sol.values()) < 0 else "exists"


def rigidity_defects(p, k):
    """Delta_j = p_j (S1 - p_j - k + 1) - (2 S2 - (k-1) S1) / n (all zero iff the E3 condition holds)."""
    p = as_fractions(p)
    n = len(p)
    s1, s2 = moments(p)
    mean = (2 * s2 - (k - 1) * s1) / n
    return [x * (s1 - x - k + 1) - mean for x in p]


def rigidity_constant(n, k):
    """kappa(n,k) of Proposition G: max over s not in {0,k,n} of |s-k| max(s, n-s)/n / sigma(s),
    sigma(s) = s(n+k-s)/(kn) - 1[s >= k] (slack of the {0,k,n} dual)."""
    best = Fraction(0)
    for s in range(1, n):
        if s == k:
            continue
        sigma = Fraction(s * (n + k - s), k * n) - (1 if s >= k else 0)
        best = max(best, Fraction(abs(s - k) * max(s, n - s), n) / sigma)
    return best


def rigidity_gap_lower_bound(p, k):
    """Proposition G: if {0,k,n} is an optimal BP basis then BP - P >= max_j |Delta_j| / kappa(n,k)."""
    return max(abs(d) for d in rigidity_defects(p, k)) / rigidity_constant(len(p), k)


def bp_exactness_verdict(p, k):
    """Necessary-condition test for P(n,k,p) = BP (notes/proofs/exactness.md).

    Returns (BP value, verdict, reason) with verdict in
      "not exact" : a necessary condition E1, E2, E3 or E4 fails (exact arithmetic);
      "open"      : all tested necessary conditions hold (exactness must be shown by a law).
    """
    p = as_fractions(p)
    n = len(p)
    s1, s2 = moments(p)
    bp, laws = bp_optimum(n, k, s1, s2)
    loo = leave_one_out(p)
    free = [j for j in range(n) if 0 < p[j] < 1]
    below_one = [j for j in range(n) if p[j] < 1]
    if bp == 1:
        if below_one and min(loo[j] for j in below_one) < k:
            lo = min(loo[j] for j in below_one)
            return bp, "not exact", f"E1: min_j sum_(l!=j) p_l = {float(lo):.4f} < k = {k}"
        return bp, "open", "E1 holds"
    if len(laws) != 1:
        return bp, "open", "BP optimum not unique (criteria not applied)"
    K = sorted(laws[0])
    # E2: E[S | X_j = 0] = loo_j (if p_j < 1) and E[S | X_j = 1] = 1 + loo_j (if p_j > 0) lie in [min K, max K]
    for j in range(n):
        means = ([loo[j]] if p[j] < 1 else []) + ([1 + loo[j]] if p[j] > 0 else [])
        if any(not K[0] <= m <= K[-1] for m in means):
            lo = min(loo[t] for t in free) if free else None
            hi = max(loo[t] for t in free) if free else None
            rng = f"[{float(lo):.4f}, {float(hi):.4f}]" if free else "n/a"
            return bp, "not exact", (f"E2: support {K} needs {K[0]} <= sum_(l!=j) p_l <= {K[-1] - 1}, "
                                     f"range is {rng}")
    if len(K) == 3 and K[0] == 0 and K[2] == n:
        c = {x * (s1 - x - k + 1) for x in p}
        if len(c) > 1:
            return bp, "not exact", (f"E3: support {{0,{k},{n}}} needs p_j(S1 - p_j - k + 1) equal for all j, "
                                     f"got {len(c)} values")
    if layered_law_status(p, K) == "none":
        return bp, "not exact", f"E4: no pairwise independent law on layers {K} (exact solve)"
    return bp, "open", f"E2-E4 hold for support {K}"


# ------------------------------------------------------------ certainty: the peeling law (exactness.md §2)

def certainty_condition(p, k):
    """Condition of Theorem C1: sum_{l != j} p_l >= k for every j with p_j < 1."""
    p = as_fractions(p)
    s1 = sum(p)
    return all(s1 - x >= k for x in p if x < 1)


def minimal_point_below(p, k):
    """Reduction of Theorem C4's proof: drop coordinates equal to 1 (lowering k), lower a
    unique maximum to the second largest value, then scale down until the leave-one-out sum
    of a maximal coordinate is exactly the threshold.

    Returns (kept, p_min, k_min): kept indices, a minimal point p_min <= p[kept] (at least
    two coordinates equal to max(p_min), sum - max = k_min) and the reduced threshold.
    Returns (kept, None, k_min) when the reduced problem is trivial (k_min <= 0) and None
    when the certainty condition fails. Exact (Fraction).
    """
    p = as_fractions(p)
    if not certainty_condition(p, k):
        return None
    kept = [i for i, x in enumerate(p) if x < 1]
    k_min = k - (len(p) - len(kept))
    if k_min <= 0:
        return kept, None, k_min
    q = sorted((p[i], i) for i in kept)
    vals = [p[i] for i in kept]
    top, second = q[-1][1], q[-2][1]
    vals[kept.index(top)] = p[second]          # LOO of the old maximum is unchanged
    b = max(vals)
    t = Fraction(k_min) / (sum(vals) - b)      # sum(vals) - b >= k_min > 0 by the condition
    return kept, [t * v for v in vals], k_min


def peeling_y(s, b, a):
    """Lemma P1: the root in [0,1] of (1 - y)(b - s y) = (1 - a)(b - a), for 0 < s <= b < 1."""
    import math
    rhs = (1 - a) * (b - a)
    disc = (b + s) ** 2 - 4 * s * (b - rhs)
    return ((b + s) - math.sqrt(disc)) / (2 * s)


def peeling_parameters(p, k, iters=200):
    """Float: (B, A, b, s, z) for a minimal point p with threshold k.

    B = coordinates equal to b = max p, A = the others, s in (0, b^2] a root of
    Phi(s) = sum_A y_s(a_i) - (k - |B| + b/s) (Lemma P2, bisection), z = 1 on B and
    y_s(a_i) on A.
    """
    pf = [float(x) for x in p]
    b = max(pf)
    B = [i for i, x in enumerate(pf) if x == b]
    A = [i for i, x in enumerate(pf) if x != b]

    def phi(s):
        return sum(peeling_y(s, b, pf[i]) for i in A) - (k - len(B) + b / s)

    lo, hi = 0.0, b * b
    assert phi(hi) >= -1e-12, "Phi(b^2) < 0: p is not a minimal point"
    for _ in range(iters):
        mid = (lo + hi) / 2
        if phi(mid) >= 0:
            hi = mid
        else:
            lo = mid
    s = hi
    z = [1.0 if i in B else peeling_y(s, b, pf[i]) for i in range(len(pf))]
    return B, A, b, s, z


def peeling_design_moments(p, s, z):
    """First and second order inclusion probabilities of the k-design D in
    L = (1-s) D + s R (Proposition C5): pi_l = (p_l - s z_l)/(1-s),
    Pi_lt = (p_l p_t - s z_l z_t)/(1-s). Works with Fractions or floats."""
    n = len(p)
    pi = [(p[l] - s * z[l]) / (1 - s) for l in range(n)]
    Pi = {(l, t): (p[l] * p[t] - s * z[l] * z[t]) / (1 - s) for l, t in combinations(range(n), 2)}
    return pi, Pi


def peeling_law_k2(p, s, z):
    """Theorem C4: the law (1-s) D + s R with S >= 2 a.s., for threshold k = 2.

    D puts mass Pi_lt on the 2-set {l,t}; R has X_l = 1 where z_l = 1 and the other
    coordinates independent Bernoulli(z_l). Exact when p, s, z are Fractions satisfying
    the equations of Lemmas P1-P2; returns a dict {0/1 tuple: mass}.
    """
    n = len(p)
    _, Pi = peeling_design_moments(p, s, z)
    law = {}
    for (l, t), w in Pi.items():
        if w:
            x = tuple(1 if i in (l, t) else 0 for i in range(n))
            law[x] = law.get(x, 0) + (1 - s) * w
    free = [i for i in range(n) if z[i] != 1]
    for bits in product((0, 1), repeat=len(free)):
        x = [1] * n
        w = s
        for i, bit in zip(free, bits):
            x[i] = bit
            w = w * (z[i] if bit else 1 - z[i])
        if w:
            law[tuple(x)] = law.get(tuple(x), 0) + w
    return law


def two_valued_peeling_s(alpha, beta, k, b):
    """Theorem C8 (float): at the two-valued minimal point (beta coordinates b, alpha
    coordinates a = (k - (beta-1) b)/alpha) the peeling parameter is s* = b/u_+, where u_+
    is the largest root of G(u) = b(n-k-u)((alpha-1)u - (k-beta)) - alpha^2 (1-a)(b-a) u."""
    import math
    n = alpha + beta
    a = (k - (beta - 1) * b) / alpha
    c = alpha ** 2 * (1 - a) * (b - a)
    q2 = -b * (alpha - 1)
    q1 = b * ((n - k) * (alpha - 1) + (k - beta)) - c
    q0 = -b * (n - k) * (k - beta)
    if q2 == 0:
        return b / (-q0 / q1)
    disc = math.sqrt(q1 * q1 - 4 * q2 * q0)
    return b / max((-q1 + disc) / (2 * q2), (-q1 - disc) / (2 * q2))


def two_valued_k2_instance(alpha, b):
    """Exact instance of Theorem C4 with |B| = 2 and alpha equal coordinates a < b:
    a = (2 - b)/alpha, y = 1 - alpha (1-a)(b-a) / (b (alpha-1)), s = b / (alpha y).
    Returns (p, s, z) with Fractions (valid for 2/(alpha+1) < b < 1)."""
    b = Fraction(b)
    a = (2 - b) / alpha
    y = 1 - alpha * (1 - a) * (b - a) / (b * (alpha - 1))
    s = b / (alpha * y)
    return [b, b] + [a] * alpha, s, [Fraction(1)] * 2 + [y] * alpha


# ------------------------------------------------------------ float LP (exploration only)

_STRUCT = {}


def _structure(n):
    if n not in _STRUCT:
        import numpy as np
        states = list(product((0, 1), repeat=n))
        A = np.array([moment_vector(x) for x in states], dtype=float).T
        _STRUCT[n] = (states, A)
    return _STRUCT[n]


def float_tight(p, k, states_filter=None):
    """HiGHS optimum of max P(S >= k) over pairwise independent laws with marginals p.

    Returns (value, {state: float mass}) or (None, None) if infeasible. Float: use only
    to explore or to locate a support for solve_exact_on_support.
    """
    import numpy as np
    from scipy.optimize import linprog
    n = len(p)
    states, A = _structure(n)
    keep = [c for c, x in enumerate(states) if states_filter is None or states_filter(x)]
    pf = [float(x) for x in p]
    b = np.array([1.0] + pf + [pf[i] * pf[j] for i, j in combinations(range(n), 2)])
    c = -np.array([1.0 if sum(states[t]) >= k else 0.0 for t in keep])
    res = linprog(c, A_eq=A[:, keep], b_eq=b, bounds=(0, None), method="highs")
    if res.status != 0:
        return None, None
    law = {states[keep[t]]: res.x[t] for t in range(len(keep)) if res.x[t] > 1e-12}
    return -res.fun, law
