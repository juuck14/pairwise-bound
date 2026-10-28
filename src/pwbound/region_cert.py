"""Build the `pw5-region/v1` certificate (format: verifier/SPEC.md section 8)."""
from fractions import Fraction

from . import parametric, poly, trimin
from .rational import fmt


def poly_json(f):
    return {f"{i},{j}": fmt(c) for (i, j), c in sorted(f.items())}


def state_json(s):
    return f"{s[0]},{s[1]}"


def redundant_facets(vid):
    """Indices of facets whose polynomial is >= 0 on the whole domain D."""
    return [k for k, (_, g) in enumerate(parametric.region_polynomials(vid))
            if trimin.minimum(g, parametric.DOMAIN)[0] >= 0]


def maximizer_bases(vid, grid=24):
    """Bases of vertex vid whose primal solution is >= 0 somewhere inside D.

    For a nondegenerate vertex this is its unique basis. Each listed basis is
    checked by the verifier through polynomial identities, so the selection
    rule (a grid search) only affects which formulas are reported.
    """
    bases = parametric.vertex_by_id(vid)["bases"]
    if len(bases) == 1:
        return list(bases)
    keep = []
    for basis in bases:
        for i in range(1, grid):
            if any(parametric.in_critical_region(basis, Fraction(i, grid), Fraction(j, grid))
                   for j in range(i + 1, grid)):
                keep.append(basis)
                break
    return keep


def build_region_certificate(witness_denominator=60):
    witnesses = parametric.find_witnesses(witness_denominator)
    verts = parametric.vertices()
    active = [v["id"] for v in verts if v["id"] in witnesses]
    inactive = [v["id"] for v in verts if v["id"] not in witnesses]
    covers = {vid: parametric.dominance_cover(vid) for vid in inactive}
    missing = [vid for vid, c in covers.items() if c is None]
    if missing:
        raise RuntimeError(f"no witness and no dominance cover for {missing}")

    from .model import STATES12
    regions, maximizers = [], []
    for vid in active:
        v = parametric.vertex_by_id(vid)
        regions.append({
            "id": vid,
            "tight_states": [state_json(s) for s in parametric.tight_states(v["y"])],
            "facets": [list(h) for h, _ in parametric.region_polynomials(vid)],
            "redundant_in_domain": redundant_facets(vid),
        })
        for basis in maximizer_bases(vid):
            maximizers.append({
                "id": vid,
                "basis": [state_json(STATES12[j]) for j in basis],
                "x": [poly_json(f) for f in parametric.parametric_primal(basis)],
            })
    return {
        "format": "pw5-region/v1",
        "domain": [["0", "0"], ["0", "1"], ["1", "1"]],
        "dual_vertices": [{"id": v["id"], "y": [fmt(c) for c in v["y"]]} for v in verts],
        "active": [{"id": vid, "witness": [fmt(witnesses[vid][0]), fmt(witnesses[vid][1])]}
                   for vid in active],
        "inactive": [{"id": vid, "cover": covers[vid]} for vid in inactive],
        "regions": regions,
        "maximizers": maximizers,
        "provenance": {
            "generator": "pwbound.region_cert.build_region_certificate",
            "witness_search": f"rational points with denominator <= {witness_denominator}",
            "cover_search": "recursive 4-way midpoint subdivision, first dominating vertex by id",
        },
    }
