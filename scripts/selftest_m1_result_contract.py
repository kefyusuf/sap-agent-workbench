#!/usr/bin/env python3
"""Self-test the deterministic M1 Technical Architect result validator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_m1_result.py"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("validate_m1_result", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M1 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected object root")
    return value


def main() -> int:
    validator = load_validator()

    scenarios = [
        {
            "name": "valid-blocked-ta003",
            "result": ROOT / "evals" / "m1" / "result-examples" / "valid-blocked.json",
            "case": ROOT / "evals" / "m1" / "technical-architect" / "TA-003.json",
            "expected_valid": True,
        },
        {
            "name": "valid-completed-ta002",
            "result": ROOT / "evals" / "m1" / "result-examples" / "valid-completed.json",
            "case": ROOT / "evals" / "m1" / "technical-architect" / "TA-002.json",
            "expected_valid": True,
        },
        {
            "name": "invalid-completed-with-blocker",
            "result": ROOT / "evals" / "m1" / "result-examples" / "invalid-completed-with-blocker.json",
            "case": ROOT / "evals" / "m1" / "technical-architect" / "TA-003.json",
            "expected_valid": False,
        },
    ]

    failures: list[str] = []

    for scenario in scenarios:
        result = load_json(scenario["result"])
        case = load_json(scenario["case"])

        structural_errors = validator.validate_result(result)
        case_errors = validator.validate_case_assertions(case, result)
        actual_valid = not structural_errors and not case_errors

        status = "PASS" if actual_valid == scenario["expected_valid"] else "FAIL"
        print(f"{status}  {scenario['name']}")

        if status == "FAIL":
            failures.append(scenario["name"])
            for error in structural_errors + case_errors:
                print(f"      {error}")

    if failures:
        print(f"Self-test failed: {', '.join(failures)}", file=sys.stderr)
        return 1

    print(f"Summary: {len(scenarios)}/{len(scenarios)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
