"""Region certificate (Theorems A and B): reproducibility, PASS, and tampering."""
import copy
import json
import subprocess
import sys
from fractions import Fraction as F

import pytest

from pwbound import parametric
from pwbound.cert import dumps
from pwbound.region_cert import build_region_certificate

from conftest import REPO, VERIFIER_PATH

CERT_PATH = REPO / "results" / "regions" / "region_certificate.json"
ACTIVE = ["V02", "V10", "V11", "V12", "V14", "V15", "V16", "V18", "V19", "V20", "V21"]


@pytest.fixture(scope="module")
def region_cert():
    return json.loads(CERT_PATH.read_text(encoding="utf-8"))


def failed(verifier, cert):
    result = verifier.verify_text(json.dumps(cert))
    assert result["error"] is None, result["error"]
    return {c["code"] for c in result["checks"] if not c["ok"]}


def test_committed_region_certificate_is_reproducible():
    assert CERT_PATH.read_text(encoding="utf-8") == dumps(build_region_certificate())


def test_region_certificate_passes_in_isolated_subprocess(tmp_path):
    proc = subprocess.run([sys.executable, "-I", str(VERIFIER_PATH), str(CERT_PATH)],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout
    assert proc.stdout.strip().endswith("VERDICT: PASS")


def test_active_pieces(region_cert):
    assert [a["id"] for a in region_cert["active"]] == ACTIVE
    assert len(region_cert["dual_vertices"]) == 21


def test_representative_point_lies_in_piece_v12():
    assert parametric.minimizers(F(2, 5), F(3, 5)) == (F(61, 75), ["V12"])
    assert parametric.in_region("V12", F(2, 5), F(3, 5))


def test_cone_description_matches_min_of_quadratics_on_grid():
    n = 24
    for i in range(n + 1):
        for j in range(n + 1):
            p, q = F(i, n), F(j, n)
            _, ids = parametric.minimizers(p, q)
            in_cone = sorted(v["id"] for v in parametric.vertices() if parametric.in_region(v["id"], p, q))
            assert ids == in_cone, (p, q)


# ---------------------------------------------------------------- tampering

def test_missing_vertex_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["dual_vertices"] = [v for v in cert["dual_vertices"] if v["id"] != "V03"]
    cert["inactive"] = [v for v in cert["inactive"] if v["id"] != "V03"]
    assert "RG_VERTICES" in failed(verifier, cert)


def test_perturbed_vertex_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["dual_vertices"][0]["y"][0] = "1/1000"
    assert "RG_VERTICES" in failed(verifier, cert)


def test_bad_witness_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    witness_v02 = next(a["witness"] for a in cert["active"] if a["id"] == "V02")
    for a in cert["active"]:
        if a["id"] == "V12":
            a["witness"] = witness_v02
    assert "RG_ACTIVE_V12" in failed(verifier, cert)


def test_witness_outside_open_domain_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["active"][0]["witness"] = ["1/2", "1/2"]
    assert f"RG_ACTIVE_{cert['active'][0]['id']}" in failed(verifier, cert)


def test_inactive_vertex_claimed_active_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["inactive"] = [v for v in cert["inactive"] if v["id"] != "V01"]
    cert["active"].append({"id": "V01", "witness": ["1/4", "1/2"]})
    codes = failed(verifier, cert)
    assert "RG_ACTIVE_V01" in codes and "RG_REGION_LIST" in codes


def test_wrong_dominator_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    for v in cert["inactive"]:
        if v["id"] == "V01":
            v["cover"] = {"dominator": "V18"}
    assert "RG_INACTIVE_V01" in failed(verifier, cert)


def test_dropping_a_vertex_from_partition_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["inactive"] = cert["inactive"][1:]
    assert "RG_PARTITION" in failed(verifier, cert)


def test_tampered_facet_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["regions"][0]["facets"][0][0] += 1
    assert f"RG_REGION_{cert['regions'][0]['id']}" in failed(verifier, cert)


def test_missing_facet_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    region = next(r for r in cert["regions"] if r["id"] == "V16")
    region["facets"].pop()
    region["redundant_in_domain"] = [k for k in region["redundant_in_domain"] if k < len(region["facets"])]
    assert "RG_REGION_V16" in failed(verifier, cert)


def test_false_redundancy_claim_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    region = next(r for r in cert["regions"] if r["id"] == "V12")
    needed = [k for k in range(len(region["facets"])) if k not in region["redundant_in_domain"]]
    region["redundant_in_domain"].append(needed[0])
    assert "RG_REGION_V12" in failed(verifier, cert)


def test_tampered_maximizer_fails(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    m = next(m for m in cert["maximizers"] if m["id"] == "V12")
    m["x"][0]["0,0"] = "0"
    assert "RG_MAXIMIZER_V12_1" in failed(verifier, cert)


def test_region_format_errors(verifier, region_cert):
    cert = copy.deepcopy(region_cert)
    cert["domain"] = [["0", "0"], ["1", "0"], ["1", "1"]]
    assert verifier.verify_text(json.dumps(cert))["error"]["code"] == "E_PROBLEM"
    cert = copy.deepcopy(region_cert)
    cert["regions"][0]["facets"][0][0] = "1"
    assert verifier.verify_text(json.dumps(cert))["error"]["code"] == "E_FORMAT"
    text = CERT_PATH.read_text(encoding="utf-8").replace('"witness": [\n        "1/4"',
                                                          '"witness": [\n        0.25', 1)
    assert verifier.verify_text(text)["error"]["code"] == "E_JSON"


def test_certainty_region():
    """In D: M(p, q) = 1  iff  q = 1, or (q >= 3/2 - p and q >= 1 - p/3).
    (notes/presentation_content.md slide 9)"""
    from pwbound import exact_lp
    n = 60
    for i in range(n + 1):
        for j in range(i, n + 1):
            p, q = F(i, n), F(j, n)
            claimed = q == 1 or (q >= F(3, 2) - p and q >= 1 - p / 3)
            assert (exact_lp.envelope(p, q) == 1) == claimed, (p, q)
