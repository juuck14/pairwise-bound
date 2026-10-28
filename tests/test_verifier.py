"""Seed certificate must PASS; each tampering must FAIL with its specific code."""
import json
import subprocess
import sys

import pytest
from fractions import Fraction as F

from pwbound.rational import fmt, parse_rational

from conftest import REPO, VERIFIER_PATH


def run(verifier, cert, allow_outside_scope=False):
    return verifier.verify_text(json.dumps(cert), allow_outside_scope)


def failed_codes(result):
    return {c["code"] for c in result["checks"] if not c["ok"]}


def add(cert, section, key, delta):
    """Add delta to the rational string stored at cert[section...][key]."""
    node = cert
    for part in section:
        node = node[part]
    node[key] = fmt(parse_rational(node[key]) + delta)


# ------------------------------------------------------------------ positive

def test_seed_certificate_passes_in_isolated_subprocess(seed_certificate, tmp_path):
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(seed_certificate))
    proc = subprocess.run([sys.executable, "-I", str(VERIFIER_PATH), str(path)],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip().endswith("VERDICT: PASS")
    assert "FAIL" not in proc.stdout


def test_seed_certificate_value_is_61_over_75(verifier, seed_certificate):
    result = run(verifier, seed_certificate)
    assert result["verdict"] == "PASS"
    assert seed_certificate["claim"]["value"] == "61/75"
    # every SPEC check code (sections 4.2-4.5) is present exactly once
    expected = (["SCOPE", "P_NONNEG", "P_TOTAL"]
                + [f"P_MARGINAL_{i}" for i in range(1, 6)]
                + [f"P_PAIR_{i}_{j}" for i in range(1, 6) for j in range(i + 1, 6)]
                + ["P_OBJECTIVE", "D_DOMINATE", "D_VALUE",
                   "R_NONNEG", "R_MOMENTS", "R_OBJECTIVE", "R_DOMINATE", "R_VALUE",
                   "C_PROJECT", "C_DUAL_LIFT"])
    assert [c["code"] for c in result["checks"]] == expected


# ------------------------------------------------------- primal tampering

def test_broken_marginal_fails(verifier, seed_certificate):
    lifted = ("primal", "lifted")
    add(seed_certificate, lifted, "00000", F(-1, 75))
    add(seed_certificate, lifted, "10000", F(1, 75))
    failed = failed_codes(run(verifier, seed_certificate))
    assert "P_MARGINAL_1" in failed
    assert "P_TOTAL" not in failed


def test_broken_pair_with_correct_marginals_fails(verifier, seed_certificate):
    # move mass 00111 + 00000 -> 00110 + 00001: marginals of X3..X5 unchanged,
    # P(X3=X5=1) and P(X4=X5=1) drop by 1/75.
    lifted = ("primal", "lifted")
    eps = F(1, 75)
    add(seed_certificate, lifted, "00111", -eps)
    add(seed_certificate, lifted, "00000", -eps)
    add(seed_certificate, lifted, "00110", eps)
    add(seed_certificate, lifted, "00001", eps)
    failed = failed_codes(run(verifier, seed_certificate))
    assert {"P_PAIR_3_5", "P_PAIR_4_5"} <= failed
    assert not any(code.startswith("P_MARGINAL") for code in failed)
    assert "P_TOTAL" not in failed and "P_NONNEG" not in failed


def test_negative_entry_from_kernel_shift_fails_only_nonnegativity(verifier, seed_certificate):
    # chi(x) = (-1)^(x3+x4+x5) is orthogonal to every monomial of degree <= 2,
    # so adding t*chi keeps all 16 equality constraints; 11000 has mass 0.
    t = F(-1, 1000)
    for key in list(seed_certificate["primal"]["lifted"]):
        sign = (-1) ** (int(key[2]) + int(key[3]) + int(key[4]))
        add(seed_certificate, ("primal", "lifted"), key, t * sign)
    failed = failed_codes(run(verifier, seed_certificate))
    assert "P_NONNEG" in failed
    assert not any(code.startswith(("P_MARGINAL", "P_PAIR")) for code in failed)
    assert "P_TOTAL" not in failed


def test_bit_reversed_keys_fail_when_p_differs_from_q(verifier, seed_certificate):
    lifted = seed_certificate["primal"]["lifted"]
    seed_certificate["primal"]["lifted"] = {k[::-1]: v for k, v in lifted.items()}
    failed = failed_codes(run(verifier, seed_certificate))
    assert "P_MARGINAL_1" in failed


def test_changed_problem_p_fails(verifier, seed_certificate):
    seed_certificate["problem"]["p"] = "1/2"
    failed = failed_codes(run(verifier, seed_certificate))
    assert "P_MARGINAL_1" in failed and "R_MOMENTS" in failed


# --------------------------------------------------------- dual tampering

def test_lowered_y0_breaks_domination(verifier, seed_certificate):
    add(seed_certificate, ("dual", "reduced"), "y0", F(-1, 10))
    add(seed_certificate, ("dual", "lifted"), "const", F(-1, 10))
    failed = failed_codes(run(verifier, seed_certificate))
    assert {"D_DOMINATE", "R_DOMINATE"} <= failed
    assert "C_DUAL_LIFT" not in failed


def test_raised_y0_leaves_duality_gap(verifier, seed_certificate):
    add(seed_certificate, ("dual", "reduced"), "y0", F(1, 10))
    add(seed_certificate, ("dual", "lifted"), "const", F(1, 10))
    failed = failed_codes(run(verifier, seed_certificate))
    assert {"D_VALUE", "R_VALUE"} <= failed
    assert "D_DOMINATE" not in failed


def test_factor_two_error_in_dual_lift_fails(verifier, seed_certificate):
    xx = seed_certificate["dual"]["lifted"]["xx"]
    y = seed_certificate["dual"]["reduced"]
    xx["1,2"] = y["y3"]                       # should be 2*y3
    for key in ("3,4", "3,5", "4,5"):
        xx[key] = y["y4"]                     # should be 2*y4
    failed = failed_codes(run(verifier, seed_certificate))
    assert "C_DUAL_LIFT" in failed
    assert failed & {"D_DOMINATE", "D_VALUE"}


# ------------------------------------------------------------ claim / scope

def test_claim_off_by_one_billionth_fails(verifier, seed_certificate):
    add(seed_certificate, ("claim",), "value", F(-1, 10**9))
    failed = failed_codes(run(verifier, seed_certificate))
    assert {"P_OBJECTIVE", "D_VALUE", "R_OBJECTIVE", "R_VALUE"} <= failed


def test_swapped_p_and_q_fails_scope(verifier, seed_certificate):
    problem = seed_certificate["problem"]
    problem["p"], problem["q"] = problem["q"], problem["p"]
    assert "SCOPE" in failed_codes(run(verifier, seed_certificate))
    assert "SCOPE" not in failed_codes(run(verifier, seed_certificate, allow_outside_scope=True))


# --------------------------------------------------------------- format

@pytest.mark.parametrize("bad", ["0.4", "1e-3", "nan", "1_000", " 1/2", "1/0", "2/-5", "٣/5"])
def test_non_rational_strings_are_rejected(verifier, seed_certificate, bad):
    seed_certificate["problem"]["p"] = bad
    result = run(verifier, seed_certificate)
    assert result["exit_code"] == 2 and result["error"]["code"] == "E_RATIONAL"


def test_json_float_literal_is_rejected(verifier, seed_certificate):
    text = json.dumps(seed_certificate).replace('"value": "61/75"', '"value": 0.8133')
    result = verifier.verify_text(text)
    assert result["exit_code"] == 2 and result["error"]["code"] == "E_JSON"


def test_json_nan_constant_is_rejected(verifier, seed_certificate):
    text = json.dumps(seed_certificate).replace('"value": "61/75"', '"value": NaN')
    assert verifier.verify_text(text)["error"]["code"] == "E_JSON"


def test_duplicate_key_is_rejected(verifier, seed_certificate):
    text = json.dumps(seed_certificate).replace('"value": "61/75"', '"value": "61/75", "value": "1"')
    assert verifier.verify_text(text)["error"]["code"] == "E_JSON"


def test_missing_and_extra_keys_are_rejected(verifier, seed_certificate):
    del seed_certificate["primal"]["lifted"]["11111"]
    assert run(verifier, seed_certificate)["error"]["code"] == "E_FORMAT"


def test_extra_key_is_rejected(verifier, seed_certificate):
    seed_certificate["dual"]["lifted"]["xx"]["2,1"] = "0"
    assert run(verifier, seed_certificate)["error"]["code"] == "E_FORMAT"


@pytest.mark.parametrize("field, value", [("groups", [[1, 2, 3], [4, 5]]), ("threshold", 4),
                                          ("groups", [[True, 2], [3, 4, 5]])])
def test_problem_definition_mismatch_is_rejected(verifier, seed_certificate, field, value):
    seed_certificate["problem"][field] = value
    assert run(verifier, seed_certificate)["error"]["code"] == "E_PROBLEM"


def test_out_of_range_probability_is_rejected(verifier, seed_certificate):
    seed_certificate["problem"]["q"] = "3/2"
    assert run(verifier, seed_certificate)["error"]["code"] == "E_RANGE"


def test_cli_exit_codes(seed_certificate, tmp_path):
    bad = dict(seed_certificate, claim={"value": "1/2"})
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    proc = subprocess.run([sys.executable, "-I", str(VERIFIER_PATH), str(path), "--json"],
                          capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["verdict"] == "FAIL"
