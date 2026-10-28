"""One-command demo: exact maximum, maximizing distribution, upper-bound certificate,
floating-point cross-check, and the independent verifier's verdict.

    python -m scripts.demo                 # representative case p = 2/5, q = 3/5
    python -m scripts.demo --p 1/5 --q 1/2

No network access or LLM API calls are involved; everything is recomputed locally.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from pwbound import float_lp, model, univariate
from pwbound.cert import certificate_filename, write_certificate
from pwbound.rational import fmt, parse_rational
from pwbound.report import quadratic_string, reduced_dual_string
from scripts.make_certificate import make_certificate

REPO = Path(__file__).resolve().parents[1]
VERIFIER = REPO / "verifier" / "verify.py"


def section(title):
    print()
    print(f"== {title} " + "=" * max(0, 66 - len(title)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--p", type=parse_rational, default=parse_rational("2/5"))
    parser.add_argument("--q", type=parse_rational, default=parse_rational("3/5"))
    parser.add_argument("--out", type=Path, default=REPO / "results" / "certificates")
    args = parser.parse_args(argv)
    p, q = args.p, args.q
    if not (0 <= p <= 1 and 0 <= q <= 1):
        parser.error("p and q must lie in [0, 1]")

    print("Problem: X1..X5 in {0,1}, P(X1)=P(X2)=p, P(X3)=P(X4)=P(X5)=q,")
    print("         all 10 pairs independent (not mutually). Maximize P(X1+...+X5 >= 3).")
    print(f"Input:   p = {fmt(p)}, q = {fmt(q)}" + ("" if p <= q else "   (note: p > q, outside 0<=p<=q<=1)"))

    sol, cert = make_certificate(p, q)
    value = sol["value"]

    section("Maximum")
    print(f"M(p, q) = {fmt(value)}  ~= {float(value):.10f}")

    section("Maximizing distribution, 12-state model (A = X1+X2, B = X3+X4+X5)")
    for (a, b), v in sol["pi"].items():
        if v:
            mark = "  S>=3" if a + b >= 3 else ""
            print(f"  P(A={a}, B={b}) = {fmt(v):>12}{mark}")

    section("Lifted 32-state distribution (uniform inside each (A, B) orbit)")
    mu = model.lift_primal(sol["pi"])
    nonzero = [(model.bitstring(x), v) for x, v in mu.items() if v]
    print(f"  {len(nonzero)} of 32 states have positive probability (key x1x2x3x4x5):")
    for i in range(0, len(nonzero), 4):
        print("  " + "   ".join(f"{k}: {fmt(v):>7}" for k, v in nonzero[i:i + 4]))

    section("Upper-bound certificate (dual polynomial)")
    print(f"  f(a, b) = {reduced_dual_string(sol['y'])}")
    print("  satisfies f(a, b) >= 1[a + b >= 3] at all 12 points, and")
    print(f"  E f(A, B) = Q(p, q) = {quadratic_string(sol['y'])}")
    print(f"           = {fmt(model.reduced_dual_value(sol['y'], p, q))}  (equal to the maximum)")
    lifted = cert["dual"]["lifted"]
    print("  32-state form g(x) = const + sum u_i x_i + sum u_ij x_i x_j with")
    print(f"    const = {lifted['const']}, u = {list(lifted['x'].values())}")
    print("    u_ij = " + ", ".join(f"{k}: {v}" for k, v in lifted["xx"].items()))

    section("Cross-checks")
    full, _ = float_lp.full_lp(p, q)
    reduced, _ = float_lp.reduced_lp(p, q)
    print(f"  HiGHS, 32-state LP (float): {full:.12f}   |diff| = {abs(full - float(value)):.2e}")
    print(f"  HiGHS, 12-state LP (float): {reduced:.12f}   |diff| = {abs(reduced - float(value)):.2e}")
    relax = univariate.relaxation_value(p, q)
    print(f"  Two-moment bound on S only (Boros-Prekopa): {fmt(relax)} ~= {float(relax):.6f}")

    section("Independent verifier (python -I verifier/verify.py)")
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / certificate_filename(p, q)
    write_certificate(cert, path)
    print(f"  certificate: {path.relative_to(REPO) if path.is_relative_to(REPO) else path}")
    cmd = [sys.executable, "-I", str(VERIFIER), str(path)]
    if p > q:
        cmd.append("--allow-outside-scope")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    lines = proc.stdout.strip().splitlines()
    checks = [l for l in lines if l.startswith(("PASS", "FAIL"))]
    failed = [l for l in checks if l.startswith("FAIL")]
    print(f"  {len(checks) - len(failed)}/{len(checks)} checks passed")
    for line in failed:
        print("  " + line)
    print("  " + (lines[-1] if lines else proc.stderr.strip()))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
