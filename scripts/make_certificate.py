"""Solve the 12-state LP exactly at (p, q) and write a pw5-point/v1 certificate.

    python -m scripts.make_certificate --p 2/5 --q 3/5 [--out results/certificates]
"""
import argparse
from pathlib import Path

from pwbound.cert import build_certificate, certificate_filename, write_certificate
from pwbound.exact_lp import solve_point
from pwbound.rational import parse_rational

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "results" / "certificates"


def make_certificate(p, q):
    sol = solve_point(p, q)
    provenance = {
        "generator": "pwbound.exact_lp.solve_point",
        "method": "exhaustive basis enumeration of the 12-state LP in exact rational arithmetic",
        "basis": [f"{a},{b}" for a, b in sol["basis"]],
    }
    return sol, build_certificate(sol["p"], sol["q"], sol["value"], sol["pi"], sol["y"], provenance)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--p", required=True, type=parse_rational)
    parser.add_argument("--q", required=True, type=parse_rational)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    sol, cert = make_certificate(args.p, args.q)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / certificate_filename(args.p, args.q)
    write_certificate(cert, path)
    print(f"M({args.p}, {args.q}) = {sol['value']}  ->  {path}")


if __name__ == "__main__":
    main()
