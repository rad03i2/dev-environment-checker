from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

_VERSION_RE = re.compile(r"(\d+(?:\.\d+){0,3})")

@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    required: str | None
    detected: str | None
    path: str | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _version_tuple(value: str) -> tuple[int, ...]:
    m = _VERSION_RE.search(value)
    if not m:
        return ()
    return tuple(int(x) for x in m.group(1).split("."))

def _satisfies(found: str, spec: str | None) -> bool:
    if not spec:
        return True
    current = _version_tuple(found)
    if not current:
        return False
    for raw in spec.split(","):
        raw = raw.strip()
        m = re.fullmatch(r"(>=|<=|==|>|<)\s*(\d+(?:\.\d+){0,3})", raw)
        if not m:
            raise ValueError(f"Unsupported version constraint: {raw}")
        op, wanted = m.groups()
        target = _version_tuple(wanted)
        width = max(len(current), len(target))
        a = current + (0,) * (width - len(current)); b = target + (0,) * (width - len(target))
        ok = {">=": a >= b, "<=": a <= b, "==": a == b, ">": a > b, "<": a < b}[op]
        if not ok:
            return False
    return True

def check_tool(name: str, command: str, version_args: list[str], constraint: str | None = None) -> CheckResult:
    path = shutil.which(command)
    if not path:
        return CheckResult(name, "missing", constraint, None, None, f"{command} was not found on PATH")
    try:
        proc = subprocess.run([path, *version_args], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CheckResult(name, "error", constraint, None, path, f"Could not query version: {exc}")
    text = (proc.stdout + "\n" + proc.stderr).strip()
    version = _VERSION_RE.search(text)
    detected = version.group(1) if version else None
    if proc.returncode != 0 or not detected:
        return CheckResult(name, "error", constraint, detected, path, "Version command failed or returned no parseable version")
    try:
        ok = _satisfies(detected, constraint)
    except ValueError as exc:
        return CheckResult(name, "error", constraint, detected, path, str(exc))
    return CheckResult(name, "ok" if ok else "mismatch", constraint, detected, path, "Requirement satisfied" if ok else "Version does not satisfy requirement")

def load_policy(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tools", []), list):
        raise ValueError("Policy must be a JSON object with a 'tools' array")
    for tool in data.get("tools", []):
        if not isinstance(tool, dict) or not all(k in tool for k in ("name", "command")):
            raise ValueError("Each tool requires 'name' and 'command'")
        if not isinstance(tool.get("version_args", ["--version"]), list):
            raise ValueError("version_args must be an array")
    return data

def audit(policy: dict[str, Any]) -> dict[str, Any]:
    results = [check_tool(t["name"], t["command"], t.get("version_args", ["--version"]), t.get("version")) for t in policy.get("tools", [])]
    required_env = policy.get("environment", [])
    env_results = []
    for name in required_env:
        present = bool(os.environ.get(name))
        env_results.append({"name": name, "status": "ok" if present else "missing", "value_exposed": False})
    healthy = all(r.status == "ok" for r in results) and all(e["status"] == "ok" for e in env_results)
    return {"healthy": healthy, "system": {"os": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": platform.python_version()}, "tools": [r.to_dict() for r in results], "environment": env_results}
