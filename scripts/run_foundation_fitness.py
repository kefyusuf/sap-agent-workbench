#!/usr/bin/env python3
"""Deterministic M0 foundation fitness runner.

Python standard library only.
This harness does not select or constrain the product runtime language.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any, Callable

RUNNER_CONTRACT_VERSION = "m0-foundation-runner-v1"
POLICY_ORDER = {
    "AUTO_EXECUTE": 0,
    "EXECUTE_AND_RECORD": 1,
    "REQUEST_APPROVAL": 2,
    "MUST_NOT_PROCEED": 3,
}
SIDE_EFFECTING_VERBS = {"WRITE", "DEPLOY", "TRANSPORT", "ADMIN"}
MUTATION_VERBS = {"WRITE", "DEPLOY", "TRANSPORT", "ADMIN"}


class RunnerError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def validate_scalar(value: Any, rule: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected_type = rule.get("type")

    if expected_type == "string" and not isinstance(value, str):
        return [f"{path}: expected string"]
    if expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        return [f"{path}: expected integer"]
    if expected_type == "array" and not isinstance(value, list):
        return [f"{path}: expected array"]
    if expected_type == "object" and not isinstance(value, dict):
        return [f"{path}: expected object"]

    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: value not in enum {rule['enum']}")

    if isinstance(value, str):
        if "minLength" in rule and len(value) < rule["minLength"]:
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
            errors.append(f"{path}: does not match pattern {rule['pattern']}")

    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in rule and value < rule["minimum"]:
            errors.append(f"{path}: below minimum")

    if isinstance(value, list):
        if "minItems" in rule and len(value) < rule["minItems"]:
            errors.append(f"{path}: fewer than minItems")
        if rule.get("uniqueItems"):
            encoded = [canonical_json(item) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate array items")
        item_rule = rule.get("items")
        if isinstance(item_rule, dict):
            for index, item in enumerate(value):
                errors.extend(validate_scalar(item, item_rule, f"{path}[{index}]"))

    return errors


def validate_fixture(fixture: dict[str, Any], schema: dict[str, Any], source: Path) -> list[str]:
    errors: list[str] = []

    if not isinstance(fixture, dict):
        return [f"{source}: fixture root must be object"]

    required = schema.get("required", [])
    for key in required:
        if key not in fixture:
            errors.append(f"{source}: missing required field {key}")

    properties = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        unknown = sorted(set(fixture) - set(properties))
        for key in unknown:
            errors.append(f"{source}: unknown top-level field {key}")

    for key, value in fixture.items():
        rule = properties.get(key)
        if isinstance(rule, dict):
            errors.extend(validate_scalar(value, rule, f"{source}:{key}"))

    return errors


def subset_matches(expected: Any, observed: Any, path: str = "$") -> list[str]:
    errors: list[str] = []

    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return [f"{path}: expected object, observed {type(observed).__name__}"]
        for key, expected_value in expected.items():
            if key not in observed:
                errors.append(f"{path}.{key}: missing from observed result")
                continue
            errors.extend(subset_matches(expected_value, observed[key], f"{path}.{key}"))
        return errors

    if isinstance(expected, list):
        if expected != observed:
            errors.append(f"{path}: expected {expected!r}, observed {observed!r}")
        return errors

    if expected != observed:
        errors.append(f"{path}: expected {expected!r}, observed {observed!r}")

    return errors


def handle_agent_tool_boundary(fixture: dict[str, Any]) -> dict[str, Any]:
    direct_path = fixture["when"].get("path") == "agent-direct-to-tool"
    return {
        "result": "FAIL" if direct_path else "PASS",
        "direct_execution_allowed": not direct_path,
        "required_path": [
            "ActionIntent",
            "Orchestrator",
            "CapabilityResolver",
            "PolicyEngine",
            "ToolRuntime",
        ],
    }


def most_restrictive(decisions: list[str]) -> str:
    unknown = [decision for decision in decisions if decision not in POLICY_ORDER]
    if unknown:
        raise RunnerError(f"unknown policy decision(s): {unknown}")
    return max(decisions, key=POLICY_ORDER.__getitem__)


def handle_policy_resolution(fixture: dict[str, Any]) -> dict[str, Any]:
    decisions = fixture["given"].get("applicable_decisions", [])
    if not decisions:
        raise RunnerError("policy-resolution requires applicable_decisions")
    return {"effective_decision": most_restrictive(decisions)}


def handle_policy_layering(fixture: dict[str, Any]) -> dict[str, Any]:
    org = fixture["given"]["organization_policy"]
    project = fixture["given"]["project_policy"]
    effective = most_restrictive([org, project])
    return {
        "effective_decision": effective,
        "project_override_applied": effective == project and POLICY_ORDER[project] >= POLICY_ORDER[org],
    }


def handle_side_effect_target_resolution(fixture: dict[str, Any]) -> dict[str, Any]:
    action = fixture["given"]["action"]
    side_effecting = action.get("verb") in SIDE_EFFECTING_VERBS
    target_unknown = action.get("target_environment") in {None, "", "UNKNOWN"}
    if side_effecting and target_unknown:
        return {
            "policy_evaluation_status": "INSUFFICIENT_CONTEXT",
            "execution_eligible": False,
        }
    return {
        "policy_evaluation_status": "RESOLVED",
        "execution_eligible": True,
    }


def handle_evidence_source_validation(fixture: dict[str, Any]) -> dict[str, Any]:
    source_type = fixture["given"]["candidate_evidence"].get("source_type")
    return {"accepted_as_system_evidence": source_type != "MODEL_OUTPUT"}


def handle_verified_claim_validation(fixture: dict[str, Any]) -> dict[str, Any]:
    claim = fixture["given"]["claim"]
    if claim.get("classification") == "VERIFIED" and not claim.get("evidence_refs"):
        return {"valid": False, "reason": "MISSING_SUPPORTING_EVIDENCE"}
    return {"valid": True, "reason": None}


def handle_revision_bound_evidence(fixture: dict[str, Any]) -> dict[str, Any]:
    evidence = fixture["given"]["evidence"]
    work_product = fixture["given"]["work_product"]
    same_subject = evidence.get("subject") == work_product.get("subject")
    same_revision = evidence.get("revision") == work_product.get("revision")
    valid = same_subject and same_revision
    return {
        "verification_valid": valid,
        "reason": None if valid else "REVISION_MISMATCH",
    }


def handle_approval_fingerprint_binding(fixture: dict[str, Any]) -> dict[str, Any]:
    approval = fixture["given"]["approval"]
    execution = fixture["given"]["execution_action"]
    valid = (
        approval.get("status") == "APPROVED"
        and approval.get("action_fingerprint") == execution.get("action_fingerprint")
    )
    return {
        "approval_valid": valid,
        "reason": None if valid else "ACTION_FINGERPRINT_MISMATCH",
    }


def handle_approval_deny_precedence(fixture: dict[str, Any]) -> dict[str, Any]:
    decision = fixture["given"]["policy_decision"]
    if decision == "MUST_NOT_PROCEED":
        return {
            "execution_eligible": False,
            "effective_decision": "MUST_NOT_PROCEED",
        }
    approval = fixture["given"].get("approval", {})
    eligible = decision != "REQUEST_APPROVAL" or approval.get("status") == "APPROVED"
    return {"execution_eligible": eligible, "effective_decision": decision}


def handle_workflow_customization(fixture: dict[str, Any]) -> dict[str, Any]:
    base_step = fixture["given"]["base_step"]
    customization = fixture["given"]["customization"]
    invalid = base_step.get("mandatory") is True and customization.get("operation") == "DISABLE"
    return {
        "customization_valid": not invalid,
        "resolution": "INVALID" if invalid else "RESOLVED",
    }


def handle_protected_field_customization(fixture: dict[str, Any]) -> dict[str, Any]:
    field = fixture["given"]["field"]
    customization = fixture["given"]["customization"]
    invalid = (
        field.get("customization") == "protected"
        and customization.get("operation") in {"REPLACE", "DISABLE"}
    )
    return {
        "customization_valid": not invalid,
        "resolution": "INVALID" if invalid else "RESOLVED",
    }


def handle_capability_registry(fixture: dict[str, Any]) -> dict[str, Any]:
    registered = set(fixture["given"].get("registered_verbs", []))
    forbidden = sorted(registered & MUTATION_VERBS)
    return {
        "forbidden_registered_verbs": forbidden,
        "must_not_include": sorted(MUTATION_VERBS),
    }


HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "agent-tool-boundary": handle_agent_tool_boundary,
    "policy-resolution": handle_policy_resolution,
    "policy-layering": handle_policy_layering,
    "side-effect-target-resolution": handle_side_effect_target_resolution,
    "evidence-source-validation": handle_evidence_source_validation,
    "verified-claim-validation": handle_verified_claim_validation,
    "revision-bound-evidence": handle_revision_bound_evidence,
    "approval-fingerprint-binding": handle_approval_fingerprint_binding,
    "approval-deny-precedence": handle_approval_deny_precedence,
    "workflow-customization": handle_workflow_customization,
    "protected-field-customization": handle_protected_field_customization,
    "capability-registry": handle_capability_registry,
}


def configuration_fingerprint(
    schema: dict[str, Any],
    fixtures: list[tuple[Path, dict[str, Any]]],
) -> str:
    digest = hashlib.sha256()
    digest.update(RUNNER_CONTRACT_VERSION.encode("utf-8"))
    digest.update(b"\0")
    digest.update(canonical_json(schema).encode("utf-8"))

    for path, fixture in fixtures:
        digest.update(b"\0")
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(canonical_json(fixture).encode("utf-8"))

    return f"sha256:{digest.hexdigest()}"


def load_inputs(root: Path) -> tuple[dict[str, Any], list[tuple[Path, dict[str, Any]]]]:
    schema_path = root / "evals" / "foundation" / "scenario.schema.json"
    fixture_dir = root / "evals" / "foundation" / "safety-kernel"

    if not schema_path.is_file():
        raise RunnerError(f"schema not found: {schema_path}")
    if not fixture_dir.is_dir():
        raise RunnerError(f"fixture directory not found: {fixture_dir}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    fixtures: list[tuple[Path, dict[str, Any]]] = []

    for path in sorted(fixture_dir.glob("FIT-*.json")):
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixtures.append((path.relative_to(root), fixture))

    if not fixtures:
        raise RunnerError("no foundation fitness fixtures found")

    return schema, fixtures


def run(root: Path) -> dict[str, Any]:
    schema, fixtures = load_inputs(root)

    validation_errors: list[str] = []
    seen_ids: set[str] = set()

    for path, fixture in fixtures:
        validation_errors.extend(validate_fixture(fixture, schema, path))
        scenario_id = fixture.get("id")
        if isinstance(scenario_id, str):
            if scenario_id in seen_ids:
                validation_errors.append(f"{path}: duplicate scenario id {scenario_id}")
            seen_ids.add(scenario_id)

        kind = fixture.get("kind")
        if isinstance(kind, str) and kind not in HANDLERS:
            validation_errors.append(f"{path}: unknown scenario kind {kind}")

    if validation_errors:
        raise RunnerError("\n".join(validation_errors))

    results: list[dict[str, Any]] = []
    critical_failed = False

    for path, fixture in fixtures:
        handler = HANDLERS[fixture["kind"]]
        observed = handler(fixture)
        mismatches = subset_matches(fixture["then"], observed)
        status = "PASS" if not mismatches else "FAIL"

        if fixture["criticality"] == "CRITICAL" and status != "PASS":
            critical_failed = True

        results.append(
            {
                "id": fixture["id"],
                "revision": fixture["revision"],
                "criticality": fixture["criticality"],
                "kind": fixture["kind"],
                "title": fixture["title"],
                "status": status,
                "source": path.as_posix(),
                "observed": observed,
                "mismatches": mismatches,
            }
        )

    return {
        "suite": "foundation-safety-kernel",
        "runner_contract_version": RUNNER_CONTRACT_VERSION,
        "python_version": platform.python_version(),
        "configuration_fingerprint": configuration_fingerprint(schema, fixtures),
        "summary": {
            "total": len(results),
            "passed": sum(item["status"] == "PASS" for item in results),
            "failed": sum(item["status"] == "FAIL" for item in results),
            "critical_failed": critical_failed,
        },
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: inferred from script location)",
    )
    parser.add_argument("--json", action="store_true", help="emit full JSON report to stdout")
    parser.add_argument("--report", type=Path, help="write full JSON report to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        report = run(args.root.resolve())
    except (RunnerError, OSError, json.JSONDecodeError) as exc:
        print(f"FOUNDATION FITNESS ERROR: {exc}", file=sys.stderr)
        return 2

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Foundation Safety Kernel — {report['configuration_fingerprint']}")
        for item in report["results"]:
            print(f"{item['status']:4}  {item['id']}  {item['title']}")
            for mismatch in item["mismatches"]:
                print(f"      {mismatch}")
        summary = report["summary"]
        print(
            f"Summary: {summary['passed']}/{summary['total']} PASS, "
            f"{summary['failed']} FAIL"
        )

    return 1 if report["summary"]["critical_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
