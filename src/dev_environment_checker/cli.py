from __future__ import annotations
import argparse, json, sys
from .core import audit, load_policy

VERSION = "1.0.0"

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dev-env-check", description="Audit local developer tools against a JSON policy.")
    p.add_argument("policy", nargs="?", default="dev-environment.json", help="policy file (default: dev-environment.json)")
    p.add_argument("--json", action="store_true", dest="as_json", help="emit machine-readable JSON")
    p.add_argument("--version", action="version", version=f"dev-environment-checker {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    return p

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = audit(load_policy(args.policy))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Development environment: {'READY' if report['healthy'] else 'NOT READY'}")
        for item in report["tools"]:
            version = item["detected"] or "-"
            required = item["required"] or "any"
            print(f"[{item['status'].upper():8}] {item['name']}: {version} (required {required})")
        for item in report["environment"]:
            print(f"[{item['status'].upper():8}] env:{item['name']} (value hidden)")
    return 0 if report["healthy"] else 1

if __name__ == "__main__": raise SystemExit(main())
