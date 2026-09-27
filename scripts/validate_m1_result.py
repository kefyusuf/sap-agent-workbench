#!/usr/bin/env python3
"""Validate an M1 SAP Technical Architect result.

Python standard library only.
This validator checks structural/safety invariants, not semantic architecture quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "m1.technical-architect-result.v1"
STATUSES = {"COMPLETED", "NEEDS_CLARIFICATION", "BLOCKED"}
CLAIM_CLASSES = {"VERIFIED", "KNOWN", "INFERRED", "ASSUMED"}
ALLOWED_CAPABILITIES = {"READ", "QUERY", "ANALYZE", "PROPOSE"}
MUTATING_CAPABILITIES = {"WRITE", "DEPLOY", "TRANSPORT", "ADMIN"}
NEXT_ACTIONS = {
    "REQUEST_CLARIFICATION",
    "VERIFY_CONTEXT",
    "REVIEW_ARCHITECTURE",
    "HANDOFF_IMPLEMENTATION",
    "NONE",
}
ID_PATTERNS = {
    "claim": re.compile(r"^C-[0-9]{3,}$"),
    "unknown": re.compile(r"^U-[0-9]{3,}$"),
    "conflict": re.compile(r"^X-[0-9]{3,}$"),
    "option": re.compile(r"^OPT-[0-9]{3,}$"),
    "verification": re.compile(r"^V-[0-9]{3,}$"),
}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def require_keys(value: Any, keys: list[str], errors: list[str], path: str) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return False
    for key in keys:
        if key not in value:
            errors.append(f"{path}: missing {key}")
    return True


def validate_unique_ids(items: Any, pattern: re.Pattern[str], errors: list[str], path: str) -> set[str]:
    ids: set[str] = set()
    if not isinstance(items, list):
        errors.append(f"{path}: expected array")
        return ids

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{path}[{index}]: expected object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or pattern.fullmatch(item_id) is None:
            errors.append(f"{path}[{index}].id: invalid id")
            continue
        if item_id in ids:
            errors.append(f"{path}[{index}].id: duplicate {item_id}")
        ids.add(item_id)
    return ids


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_result(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    top_keys = [
        "contract_version",
        "task_id",
        "status",
        "requirement_summary",
        "scope",
        "claims",
        "unknowns",
        "conflicts",
        "existing_solution_discovery",
        "solution_options",
        "proposal",
        "required_verification",
        "implementation_handoff",
        "requested_capabilities",
        "next_action",
    ]
    require_keys(result, top_keys, errors, "$")

    if errors:
        return errors

    require(result["contract_version"] == CONTRACT_VERSION, errors, "$.contract_version: unsupported contract version")
    require(nonempty_string(result["task_id"]), errors, "$.task_id: must be non-empty string")
    require(result["status"] in STATUSES, errors, "$.status: invalid status")
    require(nonempty_string(result["requirement_summary"]), errors, "$.requirement_summary: must be non-empty string")

    claim_ids = validate_unique_ids(result["claims"], ID_PATTERNS["claim"], errors, "$.claims")
    unknown_ids = validate_unique_ids(result["unknowns"], ID_PATTERNS["unknown"], errors, "$.unknowns")
    conflict_ids = validate_unique_ids(result["conflicts"], ID_PATTERNS["conflict"], errors, "$.conflicts")
    option_ids = validate_unique_ids(result["solution_options"], ID_PATTERNS["option"], errors, "$.solution_options")
    verification_ids = validate_unique_ids(
        result["required_verification"],
        ID_PATTERNS["verification"],
        errors,
        "$.required_verification",
    )

    all_ids = claim_ids | unknown_ids | conflict_ids | option_ids | verification_ids
    expected_count = (
        len(claim_ids) + len(unknown_ids) + len(conflict_ids) + len(option_ids) + len(verification_ids)
    )
    require(len(all_ids) == expected_count, errors, "$: result-local IDs must be unique across collections")

    if isinstance(result["claims"], list):
        for index, claim in enumerate(result["claims"]):
            if not isinstance(claim, dict):
                continue
            if not require_keys(
                claim,
                ["id", "classification", "statement", "system_specific", "evidence_refs", "source_refs"],
                errors,
                f"$.claims[{index}]",
            ):
                continue

            classification = claim["classification"]
            evidence_refs = claim["evidence_refs"]
            source_refs = claim["source_refs"]

            require(classification in CLAIM_CLASSES, errors, f"$.claims[{index}].classification: invalid")
            require(nonempty_string(claim["statement"]), errors, f"$.claims[{index}].statement: must be non-empty")
            require(isinstance(claim["system_specific"], bool), errors, f"$.claims[{index}].system_specific: expected boolean")
            require(isinstance(evidence_refs, list), errors, f"$.claims[{index}].evidence_refs: expected array")
            require(isinstance(source_refs, list), errors, f"$.claims[{index}].source_refs: expected array")

            if classification == "VERIFIED":
                require(bool(evidence_refs), errors, f"$.claims[{index}]: VERIFIED requires evidence_refs")
            if classification == "KNOWN":
                require(bool(evidence_refs) or bool(source_refs), errors, f"$.claims[{index}]: KNOWN requires support")

    blocking_unknown = False
    if isinstance(result["unknowns"], list):
        for index, unknown in enumerate(result["unknowns"]):
            if not isinstance(unknown, dict):
                continue
            if not require_keys(
                unknown,
                ["id", "statement", "material", "blocks_decision", "verification"],
                errors,
                f"$.unknowns[{index}]",
            ):
                continue
            require(nonempty_string(unknown["statement"]), errors, f"$.unknowns[{index}].statement: must be non-empty")
            require(nonempty_string(unknown["verification"]), errors, f"$.unknowns[{index}].verification: must be non-empty")
            if unknown.get("material") is True and unknown.get("blocks_decision") is True:
                blocking_unknown = True

    blocking_conflict = False
    if isinstance(result["conflicts"], list):
        for index, conflict in enumerate(result["conflicts"]):
            if not isinstance(conflict, dict):
                continue
            if not require_keys(
                conflict,
                ["id", "statement", "material", "blocks_decision", "status", "source_refs", "verification"],
                errors,
                f"$.conflicts[{index}]",
            ):
                continue
            require(conflict["status"] in {"UNRESOLVED", "RESOLVED"}, errors, f"$.conflicts[{index}].status: invalid")
            refs = conflict["source_refs"]
            require(isinstance(refs, list) and len(set(refs)) >= 2, errors, f"$.conflicts[{index}]: requires >=2 source_refs")
            if (
                conflict.get("material") is True
                and conflict.get("blocks_decision") is True
                and conflict.get("status") == "UNRESOLVED"
            ):
                blocking_conflict = True

    blocking_verification = False
    if isinstance(result["required_verification"], list):
        for index, verification in enumerate(result["required_verification"]):
            if not isinstance(verification, dict):
                continue
            if not require_keys(
                verification,
                ["id", "description", "why", "blocking"],
                errors,
                f"$.required_verification[{index}]",
            ):
                continue
            if verification.get("blocking") is True:
                blocking_verification = True

    discovery = result["existing_solution_discovery"]
    discovery_performed = False
    if require_keys(discovery, ["performed", "checks"], errors, "$.existing_solution_discovery"):
        discovery_performed = discovery.get("performed") is True
        require(isinstance(discovery.get("checks"), list), errors, "$.existing_solution_discovery.checks: expected array")

    proposal = result["proposal"]
    status = result["status"]

    if status == "COMPLETED":
        require(not blocking_unknown, errors, "$.status: COMPLETED with blocking unknown")
        require(not blocking_conflict, errors, "$.status: COMPLETED with unresolved blocking conflict")
        require(not blocking_verification, errors, "$.status: COMPLETED with blocking verification")
        require(isinstance(proposal, dict), errors, "$.proposal: COMPLETED requires proposal")
    else:
        require(proposal is None, errors, "$.proposal: non-COMPLETED result requires null proposal")

    if isinstance(proposal, dict):
        if require_keys(
            proposal,
            ["selected_option_id", "summary", "rationale", "confidence", "evidence_refs", "assumption_refs"],
            errors,
            "$.proposal",
        ):
            require(proposal["selected_option_id"] in option_ids, errors, "$.proposal.selected_option_id: unknown option")
            require(proposal["confidence"] in {"LOW", "MEDIUM", "HIGH"}, errors, "$.proposal.confidence: invalid")
            require(discovery_performed, errors, "$.proposal: final proposal requires existing-solution discovery")

    handoff = result["implementation_handoff"]
    if require_keys(handoff, ["ready", "notes"], errors, "$.implementation_handoff"):
        ready = handoff.get("ready")
        require(isinstance(ready, bool), errors, "$.implementation_handoff.ready: expected boolean")
        if status != "COMPLETED":
            require(ready is False, errors, "$.implementation_handoff.ready: non-COMPLETED must be false")

    capabilities = result["requested_capabilities"]
    if not isinstance(capabilities, list):
        errors.append("$.requested_capabilities: expected array")
    else:
        for index, capability in enumerate(capabilities):
            if not isinstance(capability, dict):
                errors.append(f"$.requested_capabilities[{index}]: expected object")
                continue
            if not require_keys(capability, ["verb", "purpose"], errors, f"$.requested_capabilities[{index}]"):
                continue
            verb = capability["verb"]
            require(verb in ALLOWED_CAPABILITIES, errors, f"$.requested_capabilities[{index}].verb: forbidden {verb}")
            require(verb not in MUTATING_CAPABILITIES, errors, f"$.requested_capabilities[{index}].verb: mutation forbidden")
            require(nonempty_string(capability["purpose"]), errors, f"$.requested_capabilities[{index}].purpose: must be non-empty")

    next_action = result["next_action"]
    if require_keys(next_action, ["type", "description"], errors, "$.next_action"):
        action_type = next_action.get("type")
        require(action_type in NEXT_ACTIONS, errors, "$.next_action.type: invalid")
        if status != "COMPLETED":
            require(action_type != "HANDOFF_IMPLEMENTATION", errors, "$.next_action: non-COMPLETED cannot hand off implementation")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="Technical Architect result JSON")
    parser.add_argument("--json", action="store_true", help="emit machine-readable validation report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        result = json.loads(args.result.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            raise ValidationError("result root must be object")
        errors = validate_result(result)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"M1 RESULT VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    report = {
        "contract_version": CONTRACT_VERSION,
        "result_file": str(args.result),
        "valid": not errors,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("PASS" if report["valid"] else "FAIL")
        for error in errors:
            print(f"- {error}")

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
