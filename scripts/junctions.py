"""Junctions of the piece map: points of D where >= 3 pieces (or 2 pieces and an
edge of D) meet. Writes results/regions/JUNCTIONS.md.

    python -m scripts.junctions

Coordinates are exact (sympy solves Q_i = Q_j = Q_k, or Q_i = Q_j on an edge).
Which pieces actually border a candidate point is decided numerically by
sampling a small circle around it (exploration level, not part of the verifier):
along the diagonal V10 = V11 and along p = 0 several pieces coincide with q^2,
so pure equation solving produces spurious candidates there.
"""
import itertools
import math
from pathlib import Path

import sympy as sp

from pwbound import parametric

REPO = Path(__file__).resolve().parents[1]
P_, Q_ = sp.symbols("p q", real=True)
EDGES = {"p=0": P_, "q=1": Q_ - 1, "p=q": P_ - Q_}
EPS = 1e-4
DIRECTIONS = 96


def to_sym(f):
    return sum(sp.Rational(c.numerator, c.denominator) * P_**i * Q_**j for (i, j), c in f.items())


def float_pieces():
    return [(v["id"], [(float(c), i, j) for (i, j), c in v["Q"].items()]) for v in parametric.vertices()]


def argmin_piece(pieces, x, y):
    best, best_id = math.inf, None
    for vid, terms in pieces:
        val = sum(c * x**i * y**j for c, i, j in terms)
        if val < best - 1e-12:
            best, best_id = val, vid
    return best_id


def neighbours(pieces, x, y):
    found = set()
    for t in range(DIRECTIONS):
        a = 2 * math.pi * t / DIRECTIONS
        xs, ys = x + EPS * math.cos(a), y + EPS * math.sin(a)
        # strictly inside D: on an edge several pieces coincide (e.g. q^2 on p = 0)
        if xs > EPS / 10 and ys - xs > EPS / 10 and 1 - ys > EPS / 10:
            found.add(argmin_piece(pieces, xs, ys))
    return sorted(found)


def candidates(active):
    qs = {vid: sp.expand(to_sym(parametric.vertex_by_id(vid)["Q"])) for vid in active}
    systems = [[qs[i] - qs[j], qs[i] - qs[k]] for i, j, k in itertools.combinations(active, 3)]
    systems += [[qs[i] - qs[j], e] for i, j in itertools.combinations(active, 2) for e in EDGES.values()]
    systems += [[e1, e2] for e1, e2 in itertools.combinations(EDGES.values(), 2)]
    out = {}
    for eqs in systems:
        for sol in sp.solve(eqs, [P_, Q_], dict=True):
            if P_ not in sol or Q_ not in sol or not (sol[P_].is_real and sol[Q_].is_real):
                continue
            pv, qv = sp.nsimplify(sol[P_]), sp.nsimplify(sol[Q_])
            x, y = float(pv), float(qv)
            if -1e-12 <= x <= y + 1e-12 and y <= 1 + 1e-12:
                out[(pv, qv)] = (x, y)
    return out


def main():
    cert_active = [v["id"] for v in parametric.vertices()
                   if v["id"] in parametric.find_witnesses(60)]
    pieces = float_pieces()
    rows = []
    for (pv, qv), (x, y) in sorted(candidates(cert_active).items(), key=lambda t: (t[1][0], t[1][1])):
        on = [n for n, e in EDGES.items() if sp.simplify(e.subs({P_: pv, Q_: qv})) == 0]
        near = neighbours(pieces, x, y)
        corner = len(on) >= 2
        if corner or len(near) + (1 if on else 0) >= 3:
            rows.append((pv, qv, x, y, near, on))
    lines = ["# 조각 지도의 교점 (0 ≤ p ≤ q ≤ 1)", "",
             "_`python -m scripts.junctions`가 생성한 파일이다._", "",
             "- 좌표: sympy로 Q_i = Q_j = Q_k (또는 변 위의 Q_i = Q_j)를 정확히 푼 값",
             f"- 맞닿은 조각: 점 주변 반지름 {EPS:g}의 원을 {DIRECTIONS}방향으로 표본추출해 각 표본에서 최소인 조각을 모은 것(수치, 탐색 수준)",
             "- 검증기 대상이 아니다. 주장 상태는 `notes/claims.md` C11을 따른다.", "",
             "| p | q | (근삿값) | 맞닿은 조각 | D의 변 |", "|---|---|---|---|---|"]
    for pv, qv, x, y, near, on in rows:
        lines.append(f"| {sp.sstr(pv)} | {sp.sstr(qv)} | ({x:.4f}, {y:.4f}) | {', '.join(near)} | {', '.join(on) or '-'} |")
    out = REPO / "results" / "regions" / "JUNCTIONS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[8:]))
    print(f"wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
