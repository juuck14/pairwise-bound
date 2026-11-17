"""LP over 'segment-design' columns (float, exploration).

Sort the marginals ascending. A column is a law on {0,1}^n given by at most r disjoint intervals
[a, b] (in sorted order), each with a count 1 <= c <= b - a + 1; inside each interval a uniformly
random c-subset is chosen, independently across intervals. Its size is the constant sum of the
counts, so P(S >= k) is 0 or 1, and its first and second moments have closed forms:
P(i) = c/L inside an interval, P(i,j) = c(c-1)/(L(L-1)) inside one interval, products across.
c = L gives an ordinary run. The LP mixing such columns to match (p_i, p_i p_j) is a lower bound on
Pbar(n,k,p) with polynomially many columns for fixed r (notes/k2_structure.md §16).
"""
from itertools import combinations


def segment_columns(n, r):
    """Yield columns as lists of (a, b, c): disjoint intervals [a, b] (inclusive) with counts c."""
    yield []
    def rec(start, left, cur):
        if left == 0:
            return
        for a in range(start, n):
            for b in range(a, n):
                L = b - a + 1
                for c in range(1, L + 1):
                    seg = cur + [(a, b, c)]
                    yield seg
                    yield from rec(b + 2, left - 1, seg)   # gap of at least one between intervals
    yield from rec(0, r, [])


def s3a_columns(n):
    """S3a columns: <= 3 intervals, at most one of them a design (c < L), the others full runs; O(n^7) many."""
    for segs in segment_columns(n, 3):
        if sum(1 for a, b, c in segs if c < b - a + 1) <= 1:
            yield segs


def segment_lp(p, k, r, one_design=False):
    """(value, column weights) of the segment-design LP (p sorted inside).

    one_design=True keeps only columns with at most one proper design interval (with r = 3: S3a)."""
    import numpy as np
    from scipy.optimize import linprog
    from scipy.sparse import csc_matrix
    ps = sorted(float(x) for x in p)
    n = len(ps)
    pairs = list(combinations(range(n), 2))
    pos = {pr: 1 + n + t for t, pr in enumerate(pairs)}
    data, rows, cols, cost = [], [], [], []
    cols_list = [s for s in segment_columns(n, r)
                 if not one_design or sum(1 for a, b, c in s if c < b - a + 1) <= 1]
    for col_id, segs in enumerate(cols_list):
        marg = {}
        within = {}
        for a, b, c in segs:
            L = b - a + 1
            for i in range(a, b + 1):
                marg[i] = c / L
            pw = c * (c - 1) / (L * (L - 1)) if L > 1 else 0.0
            for i in range(a, b + 1):
                for j in range(i + 1, b + 1):
                    within[(i, j)] = pw
        entries = {0: 1.0}
        for i, v in marg.items():
            entries[1 + i] = v
        idx = sorted(marg)
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                i, j = idx[x], idx[y]
                v = within.get((i, j), marg[i] * marg[j])
                if v:
                    entries[pos[(i, j)]] = v
        for row, v in entries.items():
            data.append(v); rows.append(row); cols.append(col_id)
        cost.append(-1.0 if sum(c for _, _, c in segs) >= k else 0.0)
    A = csc_matrix((data, (rows, cols)), shape=(1 + n + len(pairs), len(cols_list)))
    b = np.array([1.0] + ps + [ps[i] * ps[j] for i, j in pairs])
    res = linprog(np.array(cost), A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    if res.status != 0:
        return None, None
    return -res.fun, {tuple(cols_list[c]): res.x[c] for c in range(len(cols_list)) if res.x[c] > 1e-12}
