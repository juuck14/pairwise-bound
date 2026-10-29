"""Command-line entry points (python -m scripts.<name>).

If the package has not been installed with `pip install -e .`, make `src/`
importable so that `python -m scripts.demo` works from a plain checkout.
"""
import sys
from pathlib import Path

try:
    import pwbound  # noqa: F401
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
