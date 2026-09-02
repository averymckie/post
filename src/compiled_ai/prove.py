"""Step 7, prove: the type checker and the property tests. Symbolic.

Honest naming: mypy rejects a malformed function, and Hypothesis searches for
a counterexample to every invariant and runs every confirmed example as a
permanent test. That is checking and testing, not proof. The only proving
component in the chain is the solver in reconcile.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .model import Strict


class ProveReport(Strict):
    mypy_ok: bool
    mypy_output: str
    tests_ok: bool
    tests_output: str

    @property
    def ok(self) -> bool:
        return self.mypy_ok and self.tests_ok


def prove(pack_dir: Path, repo_root: Path) -> ProveReport:
    env_args = [sys.executable, "-m"]
    mypy = subprocess.run(
        [*env_args, "mypy", "--strict", str(pack_dir), "src/compiled_ai"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    tests = subprocess.run(
        [*env_args, "pytest", "-q", "-p", "no:cacheprovider", str(pack_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
        env={"HYPOTHESIS_PROFILE": "ci", "PYTHONHASHSEED": "0", "PATH": "", "PYTHONPATH": "src"},
    )
    return ProveReport(
        mypy_ok=mypy.returncode == 0,
        mypy_output=(mypy.stdout + mypy.stderr).strip(),
        tests_ok=tests.returncode == 0,
        tests_output=(tests.stdout + tests.stderr).strip(),
    )
