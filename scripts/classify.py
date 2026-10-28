"""Exact piece classification of M(p, q) on 0 <= p <= q <= 1.

    python -m scripts.classify

Writes
  results/regions/region_certificate.json   (pw5-region/v1, checked by verifier/verify.py)
  results/regions/REGIONS.md                (human-readable formulas, regions, maximizers)
and runs the independent verifier on the certificate.
"""
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

from pwbound import model, parametric, poly, trimin
from pwbound.cert import dumps
from pwbound.region_cert import build_region_certificate, maximizer_bases, redundant_facets

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "results" / "regions"
P, Q = sp.symbols("p q")


def to_sym(f):
    return sum(sp.Rational(c.numerator, c.denominator) * P**i * Q**j for (i, j), c in f.items())


def from_sym(expr):
    out = {}
    for (i, j), c in sp.Poly(sp.expand(expr), P, Q).terms():
        out[(i, j)] = Fraction(int(c.p), int(c.q))
    return out


def tex(expr):
    return str(expr).replace("**", "^").replace("*", "")


def linear_text(f):
    """Render a linear polynomial f = a p + b q + c >= 0 solved for q (or p)."""
    a, b, c = (Fraction(f.get(m, 0)) for m in ((1, 0), (0, 1), (0, 0)))
    if b != 0:
        rhs = to_sym({(1, 0): -a / b, (0, 0): -c / b})
        return f"q {'>=' if b > 0 else '<='} {tex(rhs)}"
    rhs = to_sym({(0, 0): -c / a})
    return f"p {'>=' if a > 0 else '<='} {tex(rhs)}"


def formula_text(f):
    expanded, factored = sp.expand(to_sym(f)), sp.factor(to_sym(f))
    return tex(expanded) if factored == expanded else f"{tex(expanded)} = {tex(factored)}"


def simplify_on_domain(g):
    """Divide out factors of fixed sign on int D (linear ones and constants)."""
    expr = sp.factor(to_sym(g))
    const, factors = sp.factor_list(expr)
    sign = 1 if const > 0 else -1
    kept = []
    for fac, mult in factors:
        f = from_sym(fac)
        degree = max(i + j for i, j in f)
        if degree == 1:
            lo = trimin.minimum(f, parametric.DOMAIN)[0]
            hi = -trimin.minimum({m: -c for m, c in f.items()}, parametric.DOMAIN)[0]
            if lo >= 0 or hi <= 0:
                if hi <= 0 and mult % 2 == 1:
                    sign = -sign
                continue           # nonzero on int D, so it does not affect the sign there
        kept.append((fac, mult))
    if not kept:
        return None                # positive (or negative) on the whole interior
    if len(kept) == 1 and kept[0][1] == 1:
        f = from_sym(sign * kept[0][0])
        if max(i + j for i, j in f) == 1:
            return linear_text(f)
        return f"{tex(sp.expand(sign * kept[0][0]))} >= 0"
    prod = sign
    for fac, mult in kept:
        prod *= fac**mult
    return f"{tex(prod)} >= 0"


def write_markdown(cert):
    lines = ["# M(p,q)의 조각별 정확 공식과 영역 (0 ≤ p ≤ q ≤ 1)", "",
             "_`python -m scripts.classify`가 생성한 파일이다. 손으로 고치지 않는다._", "",
             "- 근거 증서: `results/regions/region_certificate.json` (`python -I verifier/verify.py`로 검증)",
             "- 정리와 증명 구조: `notes/proofs/theorem_AB.md`",
             "- 조각 경계의 교점: `results/regions/JUNCTIONS.md`",
             "- 표기: A = X1+X2, B = X3+X4+X5. 달성분포는 (A,B)의 법칙 π(a,b)이며, 32상태 분포는 각 (a,b) 궤도 안에서 균등하게 나눠 얻는다.",
             "- 영역 D 안에서 부호가 고정된 선형 인수는 약분해 단순한 형태로 적었다(내부에서 동치). 전체 facet 부등식은 증서에 있다.",
             ""]
    act = {a["id"]: a["witness"] for a in cert["active"]}
    lines += ["## 요약", "", "| 조각 | M(p,q) | 목격점 (p,q) |", "|---|---|---|"]
    for vid, w in act.items():
        v = parametric.vertex_by_id(vid)
        lines.append(f"| {vid} | {tex(sp.factor(to_sym(v['Q'])))} | ({w[0]}, {w[1]}) |")
    lines.append("")
    for vid, w in act.items():
        v = parametric.vertex_by_id(vid)
        lines += [f"## {vid}", "",
                  f"- **M(p,q)** = {formula_text(v['Q'])}",
                  f"- **쌍대 다항식** f(a,b) = {tex(sp.expand(sum(sp.Rational(c.numerator, c.denominator) * t for c, t in zip(v['y'], (1, sp.Symbol('a'), sp.Symbol('b'), sp.Symbol('a') * (sp.Symbol('a') - 1), sp.Symbol('b') * (sp.Symbol('b') - 1), sp.Symbol('a') * sp.Symbol('b'))))))}",
                  f"- **목격점**: ({w[0]}, {w[1]})에서 21개 이차식 중 유일한 최소",
                  f"- **tight 상태** T = {{{', '.join(f'({a},{b})' for a, b in parametric.tight_states(v['y']))}}} "
                  f"(|T| = {len(parametric.tight_states(v['y']))}, 기저 {len(v['bases'])}개)",
                  "- **영역** {(p,q) ∈ D : M = 이 식} 은 다음 부등식들로 주어진다(D에서 자동 성립하는 facet 제외):", ""]
        redundant = set(redundant_facets(vid))
        shown = 0
        for k, (h, g) in enumerate(parametric.region_polynomials(vid)):
            if k in redundant:
                continue
            simple = simplify_on_domain(g)
            if simple is None:
                continue
            lines.append(f"  - {simple}    (facet h = {list(h)})")
            shown += 1
        if shown == 0:
            lines.append("  - (추가 조건 없음)")
        lines.append("")
        bases = maximizer_bases(vid)
        if len(v["bases"]) == 1:
            lines.append("- **달성분포** (영역 전체에서 유효):")
        else:
            lines.append(f"- **달성분포**: 퇴화 꼭짓점이라 기저마다 유효 범위가 다르다. "
                         f"tight 상태 위의 비음수 해는 모두 최대화 분포다. D 내부에서 쓰이는 기저 {len(bases)}개 중 첫 번째:")
        basis = bases[0]
        lines.append("")
        for j, f in zip(basis, parametric.parametric_primal(basis)):
            lines.append(f"  - π{model.STATES12[j]} = {tex(sp.factor(to_sym(f)))}")
        lines.append("")
    lines += ["## 비활성 꼭짓점 (D 내부 어디에서도 유일 최소가 아님)", "",
              "| 꼭짓점 | Q(p,q) | 덮개 |", "|---|---|---|"]
    for item in cert["inactive"]:
        v = parametric.vertex_by_id(item["id"])
        cover = item["cover"]
        desc = f"D 전체에서 {cover['dominator']} ≤ 이 식" if "dominator" in cover else \
            "4분할: " + ", ".join(c.get("dominator", "split") for c in cover["split"])
        lines.append(f"| {item['id']} | {tex(sp.expand(to_sym(v['Q'])))} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cert = build_region_certificate()
    path = OUT / "region_certificate.json"
    path.write_text(dumps(cert), encoding="utf-8")
    (OUT / "REGIONS.md").write_text(write_markdown(cert), encoding="utf-8")
    print(f"wrote {path.relative_to(REPO)} and results/regions/REGIONS.md")
    proc = subprocess.run([sys.executable, "-I", str(REPO / "verifier" / "verify.py"), str(path)],
                          capture_output=True, text=True)
    lines = proc.stdout.strip().splitlines()
    print(f"verifier: {sum(l.startswith('PASS') for l in lines)}/{sum(l.startswith(('PASS', 'FAIL')) for l in lines)} checks passed; {lines[-1]}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
