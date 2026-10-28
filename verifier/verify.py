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


# ------------------------------------------------------------------ entry

def verify_text(text, allow_outside_scope=False):
    """Return {"exit_code", "verdict", "checks", "error"} for a certificate text."""
    try:
        parsed = parse_certificate(load_json(text))
    except FormatError as exc:
        return {"exit_code": 2, "verdict": "ERROR", "checks": [],
                "error": {"code": exc.code, "detail": exc.detail}}
    checks = run_checks(parsed, allow_outside_scope)
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
