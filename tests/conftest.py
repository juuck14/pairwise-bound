import copy
import importlib.util
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

from pwbound.cert import build_certificate

REPO = Path(__file__).resolve().parents[1]
VERIFIER_PATH = REPO / "verifier" / "verify.py"

# Plan-stage exploration values for (p, q) = (2/5, 3/5) (notes/journal.md, J2),
# entered by hand. The verifier decides whether they are valid.
SEED_P, SEED_Q, SEED_VALUE = F(2, 5), F(3, 5), F(61, 75)
SEED_PI = {(a, b): F(0) for a in range(3) for b in range(4)}
SEED_PI.update({(0, 0): F(8, 75), (0, 1): F(2, 25), (0, 3): F(13, 75),
                (1, 2): F(12, 25), (2, 1): F(2, 25), (2, 2): F(2, 25)})
SEED_Y = (F(0), F(1), F(0), F(-1, 3), F(1, 6), F(-1, 6))


def load_verifier():
    spec = importlib.util.spec_from_file_location("pw5_verify", VERIFIER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pw5_verify"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def verifier():
    return load_verifier()


@pytest.fixture
def seed_certificate():
    cert = build_certificate(SEED_P, SEED_Q, SEED_VALUE, SEED_PI, SEED_Y,
                             provenance={"source": "plan-stage exploration values (journal J2)"})
    return copy.deepcopy(cert)
