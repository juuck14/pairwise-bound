"""Print the execution environment (Python, packages, platform, git commit) as JSON.

Used by run logs so every recorded result names the environment it came from.
"""
import json
import platform
import subprocess
import sys
from importlib import metadata

PACKAGES = ["numpy", "scipy", "sympy", "matplotlib", "pytest"]


def git_commit():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip() + ("+dirty" if dirty.stdout.strip() else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def env_report():
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": versions,
        "git_commit": git_commit(),
    }


if __name__ == "__main__":
    print(json.dumps(env_report(), indent=2))
