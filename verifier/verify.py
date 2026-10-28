#!/usr/bin/env python3
"""Independent verifier for `pw5-point/v1` certificates.

Implements verifier/SPEC.md. Uses the Python standard library only and never
imports the optimization package, so a bug in the solver cannot silently
propagate into the check. Every number is an exact Fraction.

Usage:
    python -I verifier/verify.py CERT.json [--json] [--allow-outside-scope]

Exit codes: 0 = all checks pass, 1 = some check fails, 2 = malformed input.
"""
import argparse
import json
import re
import sys
from fractions import Fraction
from itertools import combinations, product

FORMAT = "pw5-point/v1"
GROUPS = [[1, 2], [3, 4, 5]]
THRESHOLD = 3
VARS = (1, 2, 3, 4, 5)
G1 = (1, 2)
G2 = (3, 4, 5)
PAIRS = tuple(combinations(VARS, 2))
BITSTRINGS = tuple("".join(bits) for bits in product("01", repeat=5))
REDUCED_KEYS = tuple(f"{a},{b}" for a in range(3) for b in range(4))
Y_KEYS = ("y0", "y1", "y2", "y3", "y4", "y5")
RATIONAL_RE = re.compile(r"-?[0-9]+(/[1-9][0-9]*)?", re.ASCII)


class FormatError(Exception):
    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------- parsing

def _reject_float(literal):
    raise FormatError("E_JSON", f"floating-point literal {literal!r} is not allowed")


def _reject_constant(literal):
    raise FormatError("E_JSON", f"constant {literal!r} is not allowed")


def _object_without_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise FormatError("E_JSON", f"duplicate key {key!r}")
        obj[key] = value
    return obj


def load_json(text):
    try:
        return json.loads(
            text,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
            object_pairs_hook=_object_without_duplicates,
        )
    except json.JSONDecodeError as exc:
        raise FormatError("E_JSON", str(exc)) from None


def rational(value, where):
    if not isinstance(value, str) or not RATIONAL_RE.fullmatch(value):
        raise FormatError("E_RATIONAL", f"{where}: {value!r} is not a rational string")
    num, _, den = value.partition("/")
    return Fraction(int(num), int(den) if den else 1)


def expect_keys(obj, keys, where):
    if not isinstance(obj, dict):
        raise FormatError("E_FORMAT", f"{where}: expected an object")
    missing = sorted(set(keys) - set(obj))
    extra = sorted(set(obj) - set(keys))
    if missing or extra:
        raise FormatError("E_FORMAT", f"{where}: missing keys {missing}, unexpected keys {extra}")


def _is_plain_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def parse_certificate(cert):
    """Validate the structure and return all numbers as Fractions."""
    expect_keys(cert, ("format", "problem", "claim", "primal", "dual", "provenance"), "top level")
    if cert["format"] != FORMAT:
        raise FormatError("E_FORMAT", f"format is {cert['format']!r}, expected {FORMAT!r}")

    problem = cert["problem"]
    expect_keys(problem, ("p", "q", "groups", "threshold"), "problem")
    groups = problem["groups"]
    groups_ok = (
        isinstance(groups, list)
        and all(isinstance(g, list) and all(_is_plain_int(v) for v in g) for g in groups)
        and groups == GROUPS
    )
    threshold = problem["threshold"]
    if not groups_ok or not _is_plain_int(threshold) or threshold != THRESHOLD:
        raise FormatError("E_PROBLEM", f"groups={groups!r}, threshold={threshold!r}")
    p = rational(problem["p"], "problem.p")
    q = rational(problem["q"], "problem.q")
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise FormatError("E_RANGE", f"p={p}, q={q} must lie in [0,1]")

    expect_keys(cert["claim"], ("value",), "claim")
    value = rational(cert["claim"]["value"], "claim.value")

    primal = cert["primal"]
    expect_keys(primal, ("reduced", "lifted"), "primal")
    expect_keys(primal["reduced"], REDUCED_KEYS, "primal.reduced")
    expect_keys(primal["lifted"], BITSTRINGS, "primal.lifted")
    pi = {}
    for key in REDUCED_KEYS:
        a, b = (int(t) for t in key.split(","))
        pi[(a, b)] = rational(primal["reduced"][key], f"primal.reduced[{key}]")
    mu = {k: rational(primal["lifted"][k], f"primal.lifted[{k}]") for k in BITSTRINGS}

    dual = cert["dual"]
    expect_keys(dual, ("reduced", "lifted"), "dual")
    expect_keys(dual["reduced"], Y_KEYS, "dual.reduced")
    y = tuple(rational(dual["reduced"][k], f"dual.reduced[{k}]") for k in Y_KEYS)
    lifted = dual["lifted"]
    expect_keys(lifted, ("const", "x", "xx"), "dual.lifted")
    expect_keys(lifted["x"], tuple(str(i) for i in VARS), "dual.lifted.x")
    expect_keys(lifted["xx"], tuple(f"{i},{j}" for i, j in PAIRS), "dual.lifted.xx")
    u0 = rational(lifted["const"], "dual.lifted.const")
    u = {i: rational(lifted["x"][str(i)], f"dual.lifted.x[{i}]") for i in VARS}
    uu = {(i, j): rational(lifted["xx"][f"{i},{j}"], f"dual.lifted.xx[{i},{j}]") for i, j in PAIRS}

    return {"p": p, "q": q, "value": value, "pi": pi, "mu": mu, "y": y, "u0": u0, "u": u, "uu": uu}


# ----------------------------------------------------------------- checks

def _bit(state, i):
    return int(state[i - 1])


def _weight(state):
    return state.count("1")


def run_checks(c, allow_outside_scope=False):
    p, q, value = c["p"], c["q"], c["value"]
    pi, mu, y, u0, u, uu = c["pi"], c["mu"], c["y"], c["u0"], c["u"], c["uu"]
    target = {1: p, 2: p, 3: q, 4: q, 5: q}
    checks = []

    def record(code, ok, detail=""):
        checks.append({"code": code, "ok": bool(ok), "detail": "" if ok else detail})

    record("SCOPE", p <= q or allow_outside_scope, f"p={p} > q={q} (outside 0 <= p <= q <= 1)")

    # 32-state primal
    negative = [f"mu({k}) = {mu[k]}" for k in BITSTRINGS if mu[k] < 0]
    record("P_NONNEG", not negative, "; ".join(negative))
    total = sum(mu.values())
    record("P_TOTAL", total == 1, f"sum = {total}")
    for i in VARS:
        marginal = sum(mu[k] for k in BITSTRINGS if _bit(k, i) == 1)
        record(f"P_MARGINAL_{i}", marginal == target[i],
               f"P(X{i}=1) = {marginal}, expected {target[i]}")
    for i, j in PAIRS:
        bad = []
        for s, t in product((0, 1), repeat=2):
            joint = sum(mu[k] for k in BITSTRINGS if _bit(k, i) == s and _bit(k, j) == t)
            ps = target[i] if s == 1 else 1 - target[i]
            pt = target[j] if t == 1 else 1 - target[j]
            if joint != ps * pt:
                bad.append(f"P(X{i}={s},X{j}={t}) = {joint}, expected {ps * pt}")
        record(f"P_PAIR_{i}_{j}", not bad, "; ".join(bad))
    objective = sum(mu[k] for k in BITSTRINGS if _weight(k) >= THRESHOLD)
    record("P_OBJECTIVE", objective == value, f"P(S>=3) = {objective}, claimed {value}")

    # 32-state dual
    violations = []
    for k in BITSTRINGS:
        g = u0 + sum(u[i] for i in VARS if _bit(k, i) == 1)
        g += sum(uu[(i, j)] for i, j in PAIRS if _bit(k, i) == 1 and _bit(k, j) == 1)
        need = 1 if _weight(k) >= THRESHOLD else 0
        if g < need:
            violations.append(f"g({k}) = {g} < {need}")
    record("D_DOMINATE", not violations, "; ".join(violations))
    dual_value = u0 + sum(u[i] * target[i] for i in VARS)
    dual_value += sum(uu[(i, j)] * target[i] * target[j] for i, j in PAIRS)
    record("D_VALUE", dual_value == value, f"dual value = {dual_value}, claimed {value}")

    # 12-state primal and dual
    negative = [f"pi({a},{b}) = {v}" for (a, b), v in pi.items() if v < 0]
    record("R_NONNEG", not negative, "; ".join(negative))
    moments = [
        ("sum pi", sum(pi.values()), Fraction(1)),
        ("E[A]", sum(a * v for (a, b), v in pi.items()), 2 * p),
        ("E[B]", sum(b * v for (a, b), v in pi.items()), 3 * q),
        ("E[A(A-1)]", sum(a * (a - 1) * v for (a, b), v in pi.items()), 2 * p * p),
        ("E[B(B-1)]", sum(b * (b - 1) * v for (a, b), v in pi.items()), 6 * q * q),
        ("E[AB]", sum(a * b * v for (a, b), v in pi.items()), 6 * p * q),
    ]
    bad = [f"{name} = {got}, expected {want}" for name, got, want in moments if got != want]
    record("R_MOMENTS", not bad, "; ".join(bad))
    reduced_objective = sum(v for (a, b), v in pi.items() if a + b >= THRESHOLD)
    record("R_OBJECTIVE", reduced_objective == value,
           f"P(A+B>=3) = {reduced_objective}, claimed {value}")
    y0, y1, y2, y3, y4, y5 = y
    violations = []
    for a in range(3):
        for b in range(4):
            f = y0 + y1 * a + y2 * b + y3 * a * (a - 1) + y4 * b * (b - 1) + y5 * a * b
            need = 1 if a + b >= THRESHOLD else 0
            if f < need:
                violations.append(f"f({a},{b}) = {f} < {need}")
    record("R_DOMINATE", not violations, "; ".join(violations))
    reduced_value = y0 + 2 * p * y1 + 3 * q * y2 + 2 * p * p * y3 + 6 * q * q * y4 + 6 * p * q * y5
    record("R_VALUE", reduced_value == value, f"reduced dual value = {reduced_value}, claimed {value}")

    # consistency between the two levels
    bad = []
    for (a, b), v in pi.items():
        mass = sum(mu[k] for k in BITSTRINGS
                   if _bit(k, 1) + _bit(k, 2) == a and _bit(k, 3) + _bit(k, 4) + _bit(k, 5) == b)
        if mass != v:
            bad.append(f"({a},{b}): lifted mass {mass} != reduced {v}")
    record("C_PROJECT", not bad, "; ".join(bad))
    expected_x = {i: (y1 if i in G1 else y2) for i in VARS}
    expected_xx = {}
    for i, j in PAIRS:
        if i in G1 and j in G1:
            expected_xx[(i, j)] = 2 * y3
        elif i in G2 and j in G2:
            expected_xx[(i, j)] = 2 * y4
        else:
            expected_xx[(i, j)] = y5
    bad = []
    if u0 != y0:
        bad.append(f"const {u0} != y0 {y0}")
    bad += [f"x[{i}] {u[i]} != {expected_x[i]}" for i in VARS if u[i] != expected_x[i]]
    bad += [f"xx[{i},{j}] {uu[(i, j)]} != {expected_xx[(i, j)]}" for i, j in PAIRS
            if uu[(i, j)] != expected_xx[(i, j)]]
    record("C_DUAL_LIFT", not bad, "; ".join(bad))

    return checks


# ============================================================ region mode
# SPEC section 8. Everything below is recomputed from the problem definition.

REGION_FORMAT = "pw5-region/v1"
STATES12 = tuple((a, b) for a in range(3) for b in range(4))
MONOMIALS = ((0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (1, 1))
RHS_SCALE = (1, 2, 3, 2, 6, 6)
DOMAIN = ((Fraction(0), Fraction(0)), (Fraction(0), Fraction(1)), (Fraction(1), Fraction(1)))
MAX_COVER_DEPTH = 30


def col12(a, b):
    return (1, a, b, a * (a - 1), b * (b - 1), a * b)


def ind12(a, b):
    return 1 if a + b >= THRESHOLD else 0


def dot(u, v):
    return sum(x * y for x, y in zip(u, v))


# polynomials in (p, q): {(i, j): Fraction} for p^i q^j

def p_clean(f):
    return {m: c for m, c in f.items() if c != 0}


def p_add(f, g, scale=1):
    out = dict(f)
    for m, c in g.items():
        out[m] = out.get(m, 0) + scale * c
    return p_clean(out)


def p_mul(f, g):
    out = {}
    for (i1, j1), c1 in f.items():
        for (i2, j2), c2 in g.items():
            key = (i1 + i2, j1 + j2)
            out[key] = out.get(key, 0) + c1 * c2
    return p_clean(out)


def p_eval(f, p, q):
    return sum(c * p ** i * q ** j for (i, j), c in f.items())


def rhs_combination(h):
    """sum_r h_r * b_r(p, q) where b(p, q) = (1, 2p, 3q, 2p^2, 6q^2, 6pq)."""
    return p_clean({m: Fraction(s) * Fraction(c) for m, s, c in zip(MONOMIALS, RHS_SCALE, h)})


def parse_poly(obj, where):
    if not isinstance(obj, dict):
        raise FormatError("E_FORMAT", f"{where}: expected a polynomial object")
    out = {}
    for key, value in obj.items():
        m = re.fullmatch(r"([0-2]),([0-2])", key, re.ASCII)
        if not m or int(m.group(1)) + int(m.group(2)) > 2:
            raise FormatError("E_FORMAT", f"{where}: bad monomial key {key!r}")
        out[(int(m.group(1)), int(m.group(2)))] = rational(value, f"{where}[{key}]")
    return p_clean(out)


# exact linear algebra

def lin_solve(matrix, rhs):
    n = len(matrix)
    aug = [[Fraction(v) for v in row] + [Fraction(rhs[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        piv = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if piv is None:
            return None
        aug[col], aug[piv] = aug[piv], aug[col]
        lead = aug[col][col]
        aug[col] = [v / lead for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [vr - factor * vc for vr, vc in zip(aug[r], aug[col])]
    return [aug[i][n] for i in range(n)]


def row_reduce(rows):
    """Reduced row echelon form; returns (matrix, pivot columns)."""
    m = [[Fraction(v) for v in r] for r in rows]
    pivots, r = [], 0
    for c in range(len(m[0]) if m else 0):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        lead = m[r][c]
        m[r] = [v / lead for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                factor = m[i][c]
                m[i] = [vi - factor * vr for vi, vr in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
    return m, pivots


def lin_rank(rows):
    return len(row_reduce(rows)[1])


def null_vector(rows, n):
    """Nonzero h with rows @ h = 0 when the nullspace is 1-dimensional, else None."""
    m, pivots = row_reduce(rows)
    free = [c for c in range(n) if c not in pivots]
    if len(free) != 1:
        return None
    h = [Fraction(0)] * n
    h[free[0]] = Fraction(1)
    for i, c in enumerate(pivots):
        h[c] = -m[i][free[0]]
    return h


def _gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def primitive(h):
    den = 1
    for v in h:
        den = den * v.denominator // _gcd(den, v.denominator)
    ints = [int(v * den) for v in h]
    g = 0
    for v in ints:
        g = _gcd(g, v)
    return tuple(v // g for v in ints)


# exact minimum of a quadratic over a triangle (SPEC 8.4)

def tri_min(f, tri):
    get = lambda m: Fraction(f.get(m, 0))
    a, b, c, d, e = get((2, 0)), get((0, 2)), get((1, 1)), get((1, 0)), get((0, 1))
    pts = [tuple(Fraction(v) for v in vertex) for vertex in tri]
    for i in range(3):
        u, v = pts[i], pts[(i + 1) % 3]
        dx, dy = v[0] - u[0], v[1] - u[1]
        alpha = a * dx * dx + b * dy * dy + c * dx * dy
        beta = 2 * a * u[0] * dx + 2 * b * u[1] * dy + c * (u[0] * dy + u[1] * dx) + d * dx + e * dy
        if alpha > 0:
            t = -beta / (2 * alpha)
            if 0 < t < 1:
                pts.append((u[0] + t * dx, u[1] + t * dy))
    det = 4 * a * b - c * c
    if det > 0 and a > 0:
        p0 = (c * e - 2 * b * d) / det
        q0 = (c * d - 2 * a * e) / det
        (x1, y1), (x2, y2), (x3, y3) = tri
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        l1 = ((y2 - y3) * (p0 - x3) + (x3 - x2) * (q0 - y3)) / den
        l2 = ((y3 - y1) * (p0 - x3) + (x1 - x3) * (q0 - y3)) / den
        if l1 >= 0 and l2 >= 0 and 1 - l1 - l2 >= 0:
            pts.append((p0, q0))
    return min(p_eval(f, x, y) for x, y in pts)


def split_triangle(tri):
    (a, b, c) = tri
    mid = lambda u, v: ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)
    ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
    return ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))


# problem-derived objects

def enumerate_dual_vertices():
    found = set()
    for basis in combinations(range(12), 6):
        states = [STATES12[j] for j in basis]
        y = lin_solve([list(col12(*s)) for s in states], [ind12(*s) for s in states])
        if y is None:
            continue
        if all(dot(y, col12(*s)) >= ind12(*s) for s in STATES12):
            found.add(tuple(y))
    return found


def tight_set(y):
    return tuple(s for s in STATES12 if dot(y, col12(*s)) == ind12(*s))


def facets_of(states):
    gens = [col12(*s) for s in states]
    out = set()
    for subset in combinations(range(len(gens)), 5):
        h = null_vector([gens[i] for i in subset], 6)
        if h is None:
            continue
        values = [dot(h, g) for g in gens]
        if any(v > 0 for v in values) and any(v < 0 for v in values):
            continue
        if any(v < 0 for v in values):
            h = [-v for v in h]
        out.add(primitive(h))
    return out


def parse_state(text, where):
    if not isinstance(text, str) or not re.fullmatch(r"[0-2],[0-3]", text, re.ASCII):
        raise FormatError("E_FORMAT", f"{where}: bad state {text!r}")
    a, b = text.split(",")
    return (int(a), int(b))


def parse_tree(node, where, depth=0):
    if depth > MAX_COVER_DEPTH:
        raise FormatError("E_FORMAT", f"{where}: cover tree deeper than {MAX_COVER_DEPTH}")
    if isinstance(node, dict) and set(node) == {"dominator"} and isinstance(node["dominator"], str):
        return node
    if isinstance(node, dict) and set(node) == {"split"} and isinstance(node["split"], list) \
            and len(node["split"]) == 4:
        return {"split": [parse_tree(c, where, depth + 1) for c in node["split"]]}
    raise FormatError("E_FORMAT", f"{where}: bad cover tree node")


def _list_of_objects(value, keys, where):
    if not isinstance(value, list):
        raise FormatError("E_FORMAT", f"{where}: expected a list")
    for i, item in enumerate(value):
        expect_keys(item, keys, f"{where}[{i}]")
    return value


def parse_region_certificate(cert):
    expect_keys(cert, ("format", "domain", "dual_vertices", "active", "inactive", "regions",
                       "maximizers", "provenance"), "top level")
    if cert["domain"] != [["0", "0"], ["0", "1"], ["1", "1"]]:
        raise FormatError("E_PROBLEM", f"domain must be the triangle (0,0),(0,1),(1,1)")
    verts = {}
    for i, item in enumerate(_list_of_objects(cert["dual_vertices"], ("id", "y"), "dual_vertices")):
        if not isinstance(item["id"], str) or item["id"] in verts:
            raise FormatError("E_FORMAT", f"dual_vertices[{i}]: missing or repeated id")
        if not isinstance(item["y"], list) or len(item["y"]) != 6:
            raise FormatError("E_FORMAT", f"dual_vertices[{i}]: y must have 6 entries")
        verts[item["id"]] = tuple(rational(v, f"dual_vertices[{i}].y") for v in item["y"])
    active = []
    for i, item in enumerate(_list_of_objects(cert["active"], ("id", "witness"), "active")):
        w = item["witness"]
        if not isinstance(w, list) or len(w) != 2:
            raise FormatError("E_FORMAT", f"active[{i}]: witness must be [p, q]")
        active.append((item["id"], rational(w[0], f"active[{i}]"), rational(w[1], f"active[{i}]")))
    inactive = [(item["id"], parse_tree(item["cover"], f"inactive[{i}]"))
                for i, item in enumerate(_list_of_objects(cert["inactive"], ("id", "cover"), "inactive"))]
    regions = []
    for i, item in enumerate(_list_of_objects(cert["regions"], ("id", "tight_states", "facets",
                                                                 "redundant_in_domain"), "regions")):
        if not isinstance(item["tight_states"], list) or not isinstance(item["facets"], list):
            raise FormatError("E_FORMAT", f"regions[{i}]: lists expected")
        states = tuple(parse_state(s, f"regions[{i}]") for s in item["tight_states"])
        facets = []
        for h in item["facets"]:
            if not isinstance(h, list) or len(h) != 6 or not all(_is_plain_int(v) for v in h):
                raise FormatError("E_FORMAT", f"regions[{i}]: facet must be 6 integers")
            facets.append(tuple(h))
        redundant = item["redundant_in_domain"]
        if not isinstance(redundant, list) or not all(_is_plain_int(v) and 0 <= v < len(facets)
                                                      for v in redundant):
            raise FormatError("E_FORMAT", f"regions[{i}]: bad redundant_in_domain")
        regions.append((item["id"], states, facets, redundant))
    maximizers = []
    for i, item in enumerate(_list_of_objects(cert["maximizers"], ("id", "basis", "x"), "maximizers")):
        if not isinstance(item["basis"], list) or not isinstance(item["x"], list) \
                or len(item["basis"]) != 6 or len(item["x"]) != 6:
            raise FormatError("E_FORMAT", f"maximizers[{i}]: basis and x need 6 entries")
        basis = tuple(parse_state(s, f"maximizers[{i}]") for s in item["basis"])
        xs = [parse_poly(f, f"maximizers[{i}].x") for f in item["x"]]
        maximizers.append((item["id"], basis, xs))
    return {"vertices": verts, "active": active, "inactive": inactive,
            "regions": regions, "maximizers": maximizers}


def run_region_checks(c):
    checks = []

    def record(code, ok, detail=""):
        checks.append({"code": code, "ok": bool(ok), "detail": "" if ok else detail})

    verts = c["vertices"]
    Q = {vid: rhs_combination(y) for vid, y in verts.items()}

    # Theorem A premises
    columns = [col12(*s) for s in STATES12]
    rank = lin_rank([[col[r] for col in columns] for r in range(6)])
    record("RG_RANK", rank == 6, f"rank = {rank}")
    p_var, q_var = {(1, 0): Fraction(1)}, {(0, 1): Fraction(1)}
    one = {(0, 0): Fraction(1)}
    one_minus_p, one_minus_q = p_add(one, p_var, -1), p_add(one, q_var, -1)

    def power(f, k):
        out = dict(one)
        for _ in range(k):
            out = p_mul(out, f)
        return out

    law = {}
    for a, b in STATES12:
        ca = (1, 2, 1)[a]
        cb = (1, 3, 3, 1)[b]
        law[(a, b)] = p_mul(p_mul(power(p_var, a), power(one_minus_p, 2 - a)),
                            p_mul(power(q_var, b), power(one_minus_q, 3 - b)))
        law[(a, b)] = {m: v * ca * cb for m, v in law[(a, b)].items()}
    bad = []
    for r in range(6):
        lhs = {}
        for s in STATES12:
            lhs = p_add(lhs, law[s], col12(*s)[r])
        target = rhs_combination([1 if k == r else 0 for k in range(6)])
        if p_add(lhs, target, -1):
            bad.append(f"row {r}")
    record("RG_FEASIBLE", not bad, "product law violates " + ", ".join(bad))
    enumerated = enumerate_dual_vertices()
    claimed = set(verts.values())
    record("RG_VERTICES", enumerated == claimed and len(claimed) == len(verts),
           f"enumerated {len(enumerated)} vertices, certificate lists {len(verts)}; "
           f"missing {len(enumerated - claimed)}, spurious {len(claimed - enumerated)}")

    # Theorem B (i), (ii)
    act_ids = [vid for vid, _, _ in c["active"]]
    inact_ids = [vid for vid, _ in c["inactive"]]
    all_listed = act_ids + inact_ids
    record("RG_PARTITION", sorted(all_listed) == sorted(verts) and len(set(all_listed)) == len(all_listed),
           "active and inactive ids must partition the vertex ids")
    for vid, p, q in c["active"]:
        ok = vid in Q and 0 < p < q < 1
        detail = f"witness ({p}, {q}) is not inside 0<p<q<1 or id unknown"
        if ok:
            here = p_eval(Q[vid], p, q)
            beaten = [w for w in Q if w != vid and p_eval(Q[w], p, q) <= here]
            ok = not beaten
            detail = f"at ({p}, {q}) Q_{vid} = {here} is not below {beaten}"
        record(f"RG_ACTIVE_{vid}", ok, detail)
    for vid, tree in c["inactive"]:
        failures = []

        def walk(node, tri):
            if "dominator" in node:
                w = node["dominator"]
                if vid not in Q or w not in Q or w == vid:
                    failures.append(f"bad dominator {w}")
                    return
                m = tri_min(p_add(Q[vid], Q[w], -1), tri)
                if m < 0:
                    failures.append(f"Q_{vid} - Q_{w} reaches {m} on triangle {tri}")
            else:
                for child, sub in zip(node["split"], split_triangle(tri)):
                    walk(child, sub)

        walk(tree, DOMAIN)
        record(f"RG_INACTIVE_{vid}", not failures, "; ".join(map(str, failures[:3])))

    # Theorem B (iii)
    region_ids = [vid for vid, _, _, _ in c["regions"]]
    record("RG_REGION_LIST", sorted(region_ids) == sorted(act_ids),
           "regions must list each active id exactly once")
    for vid, states, facets, redundant in c["regions"]:
        problems = []
        if vid not in verts:
            record(f"RG_REGION_{vid}", False, "unknown id")
            continue
        tight = tight_set(verts[vid])
        if tuple(sorted(states)) != tuple(sorted(tight)):
            problems.append(f"tight states {sorted(tight)} != claimed {sorted(states)}")
        if lin_rank([col12(*s) for s in tight]) != 6:
            problems.append("tight columns do not span R^6")
        computed = facets_of(tight)
        if set(facets) != computed or len(set(facets)) != len(facets):
            problems.append(f"facets differ: computed {len(computed)}, claimed {len(facets)}")
        for k in redundant:
            if tri_min(rhs_combination(facets[k]), DOMAIN) < 0:
                problems.append(f"facet {k} is not redundant on the domain")
        record(f"RG_REGION_{vid}", not problems, "; ".join(problems))

    # Theorem B (iv)
    counter = {}
    for vid, basis, xs in c["maximizers"]:
        n = counter[vid] = counter.get(vid, 0) + 1
        problems = []
        if vid not in verts:
            record(f"RG_MAXIMIZER_{vid}_{n}", False, "unknown id")
            continue
        tight = tight_set(verts[vid])
        if len(set(basis)) != 6 or not set(basis) <= set(tight):
            problems.append("basis must be 6 distinct tight states")
        if lin_rank([col12(*s) for s in basis]) != 6:
            problems.append("basis columns are singular")
        for r in range(6):
            lhs = {}
            for s, x in zip(basis, xs):
                lhs = p_add(lhs, x, col12(*s)[r])
            if p_add(lhs, rhs_combination([1 if k == r else 0 for k in range(6)]), -1):
                problems.append(f"constraint {r} is not an identity")
        objective = {}
        for s, x in zip(basis, xs):
            objective = p_add(objective, x, ind12(*s))
        if p_add(objective, Q[vid], -1):
            problems.append("objective is not identically Q")
        if len(tight) == 6 and not problems:
            facet_polys = [rhs_combination(h) for h in facets_of(tight)]
            used = set()
            for x in xs:
                match = None
                for k, g in enumerate(facet_polys):
                    if k in used or not g or set(g) != set(x):
                        continue
                    ratios = {x[m] / g[m] for m in g}
                    if len(ratios) == 1 and ratios.pop() > 0:
                        match = k
                        break
                if match is None or not x:
                    problems.append("a component is not a positive multiple of a distinct facet")
                    break
                used.add(match)
        record(f"RG_MAXIMIZER_{vid}_{n}", not problems, "; ".join(problems))
    return checks


# ------------------------------------------------------------------ entry

def verify_text(text, allow_outside_scope=False):
    """Return {"exit_code", "verdict", "checks", "error"} for a certificate text."""
    try:
        cert = load_json(text)
        if isinstance(cert, dict) and cert.get("format") == REGION_FORMAT:
            checks = run_region_checks(parse_region_certificate(cert))
        else:
            checks = run_checks(parse_certificate(cert), allow_outside_scope)
    except FormatError as exc:
        return {"exit_code": 2, "verdict": "ERROR", "checks": [],
                "error": {"code": exc.code, "detail": exc.detail}}
    ok = all(c["ok"] for c in checks)
    return {"exit_code": 0 if ok else 1, "verdict": "PASS" if ok else "FAIL",
            "checks": checks, "error": None}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify a pw5-point/v1 certificate.")
    parser.add_argument("certificate")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--allow-outside-scope", action="store_true",
                        help="accept p > q (used for asymmetry comparisons)")
    args = parser.parse_args(argv)
    try:
        with open(args.certificate, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"ERROR E_IO: {exc}", file=sys.stderr)
        return 2
    result = verify_text(text, args.allow_outside_scope)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["error"] is not None:
        print(f"ERROR {result['error']['code']}: {result['error']['detail']}")
        print("VERDICT: ERROR")
    else:
        for c in result["checks"]:
            print(f"PASS {c['code']}" if c["ok"] else f"FAIL {c['code']}: {c['detail']}")
        print(f"VERDICT: {result['verdict']}")
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
