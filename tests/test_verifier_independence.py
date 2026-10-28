"""Static checks that keep verifier/verify.py independent of the solver code."""
import ast
import re

from conftest import REPO, VERIFIER_PATH

ALLOWED_IMPORTS = {"argparse", "collections", "fractions", "itertools", "json", "re", "sys"}
FORBIDDEN_CALLS = {"float", "eval", "exec", "compile", "__import__"}


def tree():
    return ast.parse(VERIFIER_PATH.read_text(encoding="utf-8"))


def test_only_allowlisted_absolute_imports():
    for node in ast.walk(tree()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative import"
            assert node.module.split(".")[0] in ALLOWED_IMPORTS, node.module


def test_no_float_literals_or_forbidden_calls():
    for node in ast.walk(tree()):
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, (float, complex)), node.value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in FORBIDDEN_CALLS, node.func.id


def test_no_reference_to_solver_package():
    assert "pwbound" not in VERIFIER_PATH.read_text(encoding="utf-8")


def test_spec_lists_the_same_allowlist():
    spec = (REPO / "verifier" / "SPEC.md").read_text(encoding="utf-8")
    line = next(l for l in spec.splitlines() if "import 허용 목록" in l)
    assert set(re.findall(r"`(\w+)`", line)) == ALLOWED_IMPORTS
