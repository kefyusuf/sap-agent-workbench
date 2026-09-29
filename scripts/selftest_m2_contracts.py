#!/usr/bin/env python3
"""Self-test the deterministic M2 contract validator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_m2_contracts.py"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("validate_m2_contracts", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M2 validator")
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
    failures: list[str] = []

    case_paths = {
        case_id: ROOT / "evals" / "m2" / "abap-development" / f"{case_id}.json"
        for case_id in ("ABAP-001", "ABAP-002", "ABAP-003", "ABAP-004")
    }

    for case_id, path in case_paths.items():
        case = load_json(path)
        errors, metadata = validator.validate_input(case["input"])
        ok = not errors and metadata.get("input_fingerprint")
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {case_id}-input")
        if not ok:
            failures.append(f"{case_id}-input")
            for error in errors:
                print(f"      {error}")

    scenarios = [
        {
            "name": "valid-ready-abap001",
            "case": case_paths["ABAP-001"],
            "result": ROOT / "evals" / "m2" / "result-examples" / "valid-ready-abap001.json",
            "expected_valid": True,
        },
        {
            "name": "valid-blocked-abap002",
            "case": case_paths["ABAP-002"],
            "result": ROOT / "evals" / "m2" / "result-examples" / "valid-blocked-abap002.json",
            "expected_valid": True,
        },
        {
            "name": "invalid-atc-pass-with-document",
            "case": case_paths["ABAP-001"],
            "result": ROOT / "evals" / "m2" / "result-examples" / "invalid-atc-pass-with-document.json",
            "expected_valid": False,
        },
    ]

    for scenario in scenarios:
        case = load_json(scenario["case"])
        result = load_json(scenario["result"])

        input_errors, metadata = validator.validate_input(case["input"])
        result_errors = (
            validator.validate_result(result, case, metadata)
            if not input_errors
            else []
        )
        actual_valid = not input_errors and not result_errors
        status = "PASS" if actual_valid == scenario["expected_valid"] else "FAIL"

        print(f"{status}  {scenario['name']}")

        if status == "FAIL":
            failures.append(scenario["name"])
            for error in input_errors + result_errors:
                print(f"      {error}")

    if failures:
        print(f"Self-test failed: {', '.join(failures)}", file=sys.stderr)
        return 1

    print("Summary: 7/7 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
