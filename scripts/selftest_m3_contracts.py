#!/usr/bin/env python3
"""Self-test the deterministic M3 Reviewer/Test Engineer contract validator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_m3_contracts.py"


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("validate_m3_contracts", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M3 validator")
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
        case_id: ROOT / "evals" / "m3" / "review-verification" / f"{case_id}.json"
        for case_id in ("REVIEW-001", "REVIEW-002", "TEST-001", "TEST-002")
    }

    for case_id, path in case_paths.items():
        case = load_json(path)
        if case["agent"] == "SAP_REVIEWER":
            errors, metadata = validator.validate_review_input(case["input"])
        else:
            errors, metadata = validator.validate_test_input(case["input"])

        ok = not errors and metadata.get("input_fingerprint")
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {case_id}-input")

        if not ok:
            failures.append(f"{case_id}-input")
            for error in errors:
                print(f"      {error}")

    scenarios = [
        {
            "name": "valid-review-acceptable-review001",
            "case": case_paths["REVIEW-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "valid-review-acceptable-review001.json",
            "expected_valid": True,
        },
        {
            "name": "valid-changes-required-review002",
            "case": case_paths["REVIEW-002"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "valid-changes-required-review002.json",
            "expected_valid": True,
        },
        {
            "name": "invalid-review-acceptable-review002",
            "case": case_paths["REVIEW-002"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "invalid-review-acceptable-review002.json",
            "expected_valid": False,
        },
        {
            "name": "valid-test-plan-test001",
            "case": case_paths["TEST-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "valid-test-plan-test001.json",
            "expected_valid": True,
        },
        {
            "name": "valid-test-plan-test002",
            "case": case_paths["TEST-002"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "valid-test-plan-test002.json",
            "expected_valid": True,
        },
        {
            "name": "invalid-test-plan-missing-critical-coverage",
            "case": case_paths["TEST-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "invalid-test-plan-missing-critical-coverage.json",
            "expected_valid": False,
        },
        {
            "name": "invalid-test-pass-without-evidence",
            "case": case_paths["TEST-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "invalid-test-pass-without-evidence.json",
            "expected_valid": False,
        },
        {
            "name": "invalid-review-compile-with-document",
            "case": case_paths["REVIEW-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "invalid-review-compile-with-document.json",
            "expected_valid": False,
        },
        {
            "name": "invalid-test-atc-with-document",
            "case": case_paths["TEST-001"],
            "result": ROOT / "evals" / "m3" / "result-examples" / "invalid-test-atc-with-document.json",
            "expected_valid": False,
        },
    ]

    for scenario in scenarios:
        case = load_json(scenario["case"])
        result = load_json(scenario["result"])

        if case["agent"] == "SAP_REVIEWER":
            input_errors, metadata = validator.validate_review_input(case["input"])
            result_errors = (
                validator.validate_review_result(result, case, metadata)
                if not input_errors
                else []
            )
        else:
            input_errors, metadata = validator.validate_test_input(case["input"])
            result_errors = (
                validator.validate_test_result(result, case, metadata)
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

    print("Summary: 13/13 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
