"""Run P65-P79 through fixed, fail-closed handoffs with no LLM intervention."""
from __future__ import annotations

import importlib.abc
import json
import os
from pathlib import Path
import subprocess
import sys

from proofs.augment import DEFAULT_OUT, ROOT, MODEL_CLIENTS, canonical, digest


def main() -> None:
    python = sys.executable
    commands = [
        [python, "-m", "proofs.augment", "--record"],
        ["node", "tests/test_augmentation_ui.mjs"],
        [python, "-m", "proofs.presentation_pdf"],
        [python, "-m", "proofs.record_presentation_checks"],
        [python, "-m", "proofs.operations"],
        ["node", "tests/test_operations_ui.mjs"],
        [python, "-m", "proofs.record_operations"],
        [python, "-m", "proofs.operations_print"],
        [python, "-m", "proofs.record_extensions", "print"],
        [python, "-m", "proofs.gallery"],
        ["node", "tests/test_gallery_ui.mjs"],
        [python, "-m", "proofs.gallery_print"],
        [python, "-m", "pytest", "tests/test_augmentation.py", "tests/test_operations.py", "--junitxml=proofs/cache/workflow-tests.xml"],
    ]
    final = [python, "-m", "proofs.record_extensions", "gallery"]
    allowed = {tuple(command) for command in commands + [final]}
    attempts = []
    class BlockModels(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split(".")[0] in MODEL_CLIENTS:
                attempts.append("model import: " + fullname)
                raise RuntimeError("Model reasoning is forbidden in the workflow")
    def audit(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "os.system", "os.exec", "os.posix_spawn"}:
            attempts.append(event)
            raise RuntimeError("External execution is forbidden")
        if event == "subprocess.Popen" and tuple(args[1]) not in allowed:
            attempts.append("unexpected worker command")
            raise RuntimeError("Only named workflow workers can execute")
    if MODEL_CLIENTS.intersection(sys.modules):
        raise RuntimeError("Model client loaded before workflow guard")
    sys.meta_path.insert(0, BlockModels())
    sys.addaudithook(audit)
    env = {**os.environ, "PROOFS_AMEND_REASON": os.environ.get("PROOFS_AMEND_REASON", "Reproduce the complete augmentation workflow through fixed function handoffs")}
    completed = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError(f"Workflow stopped at {command[1:]}: {result.stderr[-1800:]} {result.stdout[-1800:]}")
        completed.append({"command": ["python" if value == python else value for value in command], "exit_code": result.returncode})
        print(json.dumps({"completed_step": len(completed), "command": completed[-1]["command"]}), flush=True)
    from xml.etree import ElementTree as ET
    suite = ET.parse(ROOT / "proofs/cache/workflow-tests.xml").getroot().find("testsuite")
    counts = {key: int(suite.get(key, "0")) for key in ["tests", "failures", "errors", "skipped"]}
    if counts["failures"] or counts["errors"] or counts["skipped"] or attempts:
        raise ValueError("Workflow validation did not complete cleanly")
    reports = ["verification.json", "dom-verification.json", "print-verification.json", "operations-verification.json", "operations-dom-verification.json", "operations-print-verification.json", "gallery-verification.json", "gallery-dom-verification.json", "gallery-print-verification.json"]
    report = {"completed": True, "runtime_llm_intervention": "forbidden", "sequencing": "fixed commands; fail on the first failed handoff", "steps": completed,
              "coordinator_boundary_attempts": attempts, "coordinator_scope": "Model imports and network calls forbidden; only named worker subprocesses allowed",
              "worker_scope": "Source transformations and rendering reject model imports, sockets, and child execution; documented native initialization precedes worker guards",
              "tests": counts, "evidence": {name: digest((DEFAULT_OUT / name).read_bytes()) for name in reports}, "implementation_sha256": digest(Path(__file__).read_bytes())}
    (DEFAULT_OUT / "workflow-verification.json").write_bytes(canonical(report))
    result = subprocess.run(final, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError("Final evidence registration failed: " + result.stderr)
    print(json.dumps({"completed_steps": len(completed) + 1, "tests": counts, "llm_intervention": "none", "checkpoint": "P79"}))


if __name__ == "__main__":
    main()
