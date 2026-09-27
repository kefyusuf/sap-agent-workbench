#!/usr/bin/env python3
"""Validate an M1 SAP Technical Architect result.

Python standard library only.
This validator checks structural/safety invariants and optional case assertions.
It does not judge semantic SAP architecture quality.
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
DISCOVERY_CATEGORIES = {
    "SAP_STANDARD",
    "CONFIGURATION",
    "EXISTING_IMPLEMENTATION",
    "SUPPORTED_EXTENSION",
    "RELEASED_API_EVENT",
    "SIDE_BY_SIDE_EXTENSION",
    "CUSTOM_IMPLEMENTATION",
}
DISCOVERY_STATUSES = {"APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"}
OPTION_FAMILIES = {
    "STANDARD_CONFIGURATION",
    "SUPPORTED_EXTENSION",
    "RELEASED_API_EVENT",
    "INTEGRATION",
    "SIDE_BY_SIDE_BTP",
    "CUSTOM_IMPLEMENTATION",
    "OTHER",
}
ALLOWED_CAPABILITIES = {"READ", "QUERY", "ANALYZE", "PROPOSE"}
MUTATING_CAPABILITIES = {"WRITE", "DEPLOY", "TRANSPORT", "ADMIN"}
NEXT_ACTIONS = {
    "REQUEST_CLARIFICATION",
    "VERIFY_CONTEXT",
    "REVIEW_ARCHITECTURE",
    "HANDOFF_IMPLEMENTATION",
    "NONE",
}
FINGERPRINT_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
ID_PATTERNS = {
    "claim": re.compile(r"^C-[0-9]{3,}$"),
    "unknown": re.compile(r"^U-[0-9]{3,}$"),
    "conflict": re.compile(r"^X-[0-9]{3,}$"),
    "option": re.compile(r"^OPT-[0-9]{3,}$"),
    "verification": re.compile(r"^V-[0-9]{3,}$"),
}
TOP_LEVEL_KEYS = {
    "contract_version",
    "task_id",
    "provenance",
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

    ok = True
    for key in keys:
        if key not in value:
            errors.append(f"{path}: missing {key}")
            ok = False
    return ok


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate_unique_ids(
    items: Any,
    pattern: re.Pattern[str],
    errors: list[str],
    path: str,
) -> set[str]:
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


def validate_scope(scope: Any, errors: list[str]) -> None:
    if not require_keys(scope, ["modules", "systems", "environments", "project"], errors, "$.scope"):
        return

    require(string_list(scope["modules"]), errors, "$.scope.modules: expected string array")
    require(string_list(scope["systems"]), errors, "$.scope.systems: expected string array")
    require(string_list(scope["environments"]), errors, "$.scope.environments: expected string array")
    require(
        scope["project"] is None or isinstance(scope["project"], str),
        errors,
        "$.scope.project: expected string or null",
    )


def validate_claims(claims: Any, errors: list[str]) -> set[str]:
    ids = validate_unique_ids(claims, ID_PATTERNS["claim"], errors, "$.claims")
    if not isinstance(claims, list):
        return ids

    for index, claim in enumerate(claims):
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
        require(
            isinstance(claim["system_specific"], bool),
            errors,
            f"$.claims[{index}].system_specific: expected boolean",
        )
        require(string_list(evidence_refs), errors, f"$.claims[{index}].evidence_refs: expected string array")
        require(string_list(source_refs), errors, f"$.claims[{index}].source_refs: expected string array")

        if classification == "VERIFIED":
            require(bool(evidence_refs), errors, f"$.claims[{index}]: VERIFIED requires evidence_refs")
        elif classification == "KNOWN":
            require(
                bool(evidence_refs) or bool(source_refs),
                errors,
                f"$.claims[{index}]: KNOWN requires evidence_refs or source_refs",
            )

    return ids


def validate_unknowns(unknowns: Any, errors: list[str]) -> tuple[set[str], bool]:
    ids = validate_unique_ids(unknowns, ID_PATTERNS["unknown"], errors, "$.unknowns")
    blocking = False

    if not isinstance(unknowns, list):
        return ids, blocking

    for index, unknown in enumerate(unknowns):
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
        require(isinstance(unknown["material"], bool), errors, f"$.unknowns[{index}].material: expected boolean")
        require(
            isinstance(unknown["blocks_decision"], bool),
            errors,
            f"$.unknowns[{index}].blocks_decision: expected boolean",
        )
        require(
            nonempty_string(unknown["verification"]),
            errors,
            f"$.unknowns[{index}].verification: must be non-empty",
        )

        if unknown.get("material") is True and unknown.get("blocks_decision") is True:
            blocking = True

    return ids, blocking


def validate_conflicts(conflicts: Any, errors: list[str]) -> tuple[set[str], bool]:
    ids = validate_unique_ids(conflicts, ID_PATTERNS["conflict"], errors, "$.conflicts")
    blocking = False

    if not isinstance(conflicts, list):
        return ids, blocking

    for index, conflict in enumerate(conflicts):
        if not isinstance(conflict, dict):
            continue
        if not require_keys(
            conflict,
            ["id", "statement", "material", "blocks_decision", "status", "source_refs", "verification"],
            errors,
            f"$.conflicts[{index}]",
        ):
            continue

        require(nonempty_string(conflict["statement"]), errors, f"$.conflicts[{index}].statement: must be non-empty")
        require(isinstance(conflict["material"], bool), errors, f"$.conflicts[{index}].material: expected boolean")
        require(
            isinstance(conflict["blocks_decision"], bool),
            errors,
            f"$.conflicts[{index}].blocks_decision: expected boolean",
        )
        require(
            conflict["status"] in {"UNRESOLVED", "RESOLVED"},
            errors,
            f"$.conflicts[{index}].status: invalid",
        )

        refs = conflict["source_refs"]
        require(
            string_list(refs) and len(set(refs)) >= 2,
            errors,
            f"$.conflicts[{index}]: requires at least two unique source_refs",
        )
        require(
            nonempty_string(conflict["verification"]),
            errors,
            f"$.conflicts[{index}].verification: must be non-empty",
        )

        if (
            conflict.get("material") is True
            and conflict.get("blocks_decision") is True
            and conflict.get("status") == "UNRESOLVED"
        ):
            blocking = True

    return ids, blocking


def validate_discovery(discovery: Any, errors: list[str]) -> bool:
    if not require_keys(discovery, ["performed", "checks"], errors, "$.existing_solution_discovery"):
        return False

    performed = discovery.get("performed")
    require(isinstance(performed, bool), errors, "$.existing_solution_discovery.performed: expected boolean")

    checks = discovery.get("checks")
    if not isinstance(checks, list):
        errors.append("$.existing_solution_discovery.checks: expected array")
        return performed is True

    seen_categories: set[str] = set()
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"$.existing_solution_discovery.checks[{index}]: expected object")
            continue
        if not require_keys(
            check,
            ["category", "status", "notes", "evidence_refs"],
            errors,
            f"$.existing_solution_discovery.checks[{index}]",
        ):
            continue

        category = check["category"]
        require(
            category in DISCOVERY_CATEGORIES,
            errors,
            f"$.existing_solution_discovery.checks[{index}].category: invalid",
        )
        require(
            category not in seen_categories,
            errors,
            f"$.existing_solution_discovery.checks[{index}].category: duplicate {category}",
        )
        seen_categories.add(category)

        require(
            check["status"] in DISCOVERY_STATUSES,
            errors,
            f"$.existing_solution_discovery.checks[{index}].status: invalid",
        )
        require(isinstance(check["notes"], str), errors, f"$.existing_solution_discovery.checks[{index}].notes: expected string")
        require(
            string_list(check["evidence_refs"]),
            errors,
            f"$.existing_solution_discovery.checks[{index}].evidence_refs: expected string array",
        )

    return performed is True


def validate_options(options: Any, claim_ids: set[str], errors: list[str]) -> set[str]:
    ids = validate_unique_ids(options, ID_PATTERNS["option"], errors, "$.solution_options")
    if not isinstance(options, list):
        return ids

    for index, option in enumerate(options):
        if not isinstance(option, dict):
            continue
        if not require_keys(
            option,
            [
                "id",
                "title",
                "family",
                "description",
                "tradeoffs",
                "risks",
                "evidence_refs",
                "assumption_refs",
                "required_verification",
            ],
            errors,
            f"$.solution_options[{index}]",
        ):
            continue

        require(nonempty_string(option["title"]), errors, f"$.solution_options[{index}].title: must be non-empty")
        require(option["family"] in OPTION_FAMILIES, errors, f"$.solution_options[{index}].family: invalid")
        require(
            nonempty_string(option["description"]),
            errors,
            f"$.solution_options[{index}].description: must be non-empty",
        )
        require(string_list(option["tradeoffs"]), errors, f"$.solution_options[{index}].tradeoffs: expected string array")
        require(string_list(option["risks"]), errors, f"$.solution_options[{index}].risks: expected string array")
        require(
            string_list(option["evidence_refs"]),
            errors,
            f"$.solution_options[{index}].evidence_refs: expected string array",
        )
        require(
            string_list(option["assumption_refs"]),
            errors,
            f"$.solution_options[{index}].assumption_refs: expected string array",
        )
        require(
            string_list(option["required_verification"]),
            errors,
            f"$.solution_options[{index}].required_verification: expected string array",
        )

        for ref in option.get("assumption_refs", []):
            require(ref in claim_ids, errors, f"$.solution_options[{index}].assumption_refs: unknown claim {ref}")

    return ids


def validate_verification(items: Any, errors: list[str]) -> tuple[set[str], bool]:
    ids = validate_unique_ids(items, ID_PATTERNS["verification"], errors, "$.required_verification")
    blocking = False

    if not isinstance(items, list):
        return ids, blocking

    for index, verification in enumerate(items):
        if not isinstance(verification, dict):
            continue
        if not require_keys(
            verification,
            ["id", "description", "why", "blocking"],
            errors,
            f"$.required_verification[{index}]",
        ):
            continue

        require(
            nonempty_string(verification["description"]),
            errors,
            f"$.required_verification[{index}].description: must be non-empty",
        )
        require(nonempty_string(verification["why"]), errors, f"$.required_verification[{index}].why: must be non-empty")
        require(
            isinstance(verification["blocking"], bool),
            errors,
            f"$.required_verification[{index}].blocking: expected boolean",
        )

        if verification.get("blocking") is True:
            blocking = True

    return ids, blocking


def validate_proposal(
    proposal: Any,
    status: str,
    option_ids: set[str],
    claim_ids: set[str],
    discovery_performed: bool,
    errors: list[str],
) -> None:
    if status == "COMPLETED":
        require(isinstance(proposal, dict), errors, "$.proposal: COMPLETED requires proposal")
    else:
        require(proposal is None, errors, "$.proposal: non-COMPLETED result requires null proposal")

    if not isinstance(proposal, dict):
        return

    if not require_keys(
        proposal,
        ["selected_option_id", "summary", "rationale", "confidence", "evidence_refs", "assumption_refs"],
        errors,
        "$.proposal",
    ):
        return

    require(proposal["selected_option_id"] in option_ids, errors, "$.proposal.selected_option_id: unknown option")
    require(nonempty_string(proposal["summary"]), errors, "$.proposal.summary: must be non-empty")
    require(string_list(proposal["rationale"]), errors, "$.proposal.rationale: expected string array")
    require(proposal["confidence"] in {"LOW", "MEDIUM", "HIGH"}, errors, "$.proposal.confidence: invalid")
    require(string_list(proposal["evidence_refs"]), errors, "$.proposal.evidence_refs: expected string array")
    require(string_list(proposal["assumption_refs"]), errors, "$.proposal.assumption_refs: expected string array")

    for ref in proposal.get("assumption_refs", []):
        require(ref in claim_ids, errors, f"$.proposal.assumption_refs: unknown claim {ref}")

    require(discovery_performed, errors, "$.proposal: final proposal requires existing-solution discovery")


def validate_result(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(result, dict):
        return ["$: expected object"]

    missing = sorted(TOP_LEVEL_KEYS - set(result))
    unknown = sorted(set(result) - TOP_LEVEL_KEYS)
    for key in missing:
        errors.append(f"$: missing {key}")
    for key in unknown:
        errors.append(f"$: unknown top-level field {key}")
    if errors:
        return errors

    require(result["contract_version"] == CONTRACT_VERSION, errors, "$.contract_version: unsupported contract version")
    require(nonempty_string(result["task_id"]), errors, "$.task_id: must be non-empty string")

    provenance = result["provenance"]
    if require_keys(
        provenance,
        ["input_fingerprint", "configuration_fingerprint"],
        errors,
        "$.provenance",
    ):
        require(
            isinstance(provenance["input_fingerprint"], str)
            and FINGERPRINT_PATTERN.fullmatch(provenance["input_fingerprint"]) is not None,
            errors,
            "$.provenance.input_fingerprint: invalid sha256 fingerprint",
        )
        require(
            isinstance(provenance["configuration_fingerprint"], str)
            and FINGERPRINT_PATTERN.fullmatch(provenance["configuration_fingerprint"]) is not None,
            errors,
            "$.provenance.configuration_fingerprint: invalid sha256 fingerprint",
        )

    require(result["status"] in STATUSES, errors, "$.status: invalid status")
    require(nonempty_string(result["requirement_summary"]), errors, "$.requirement_summary: must be non-empty string")

    validate_scope(result["scope"], errors)
    claim_ids = validate_claims(result["claims"], errors)
    unknown_ids, blocking_unknown = validate_unknowns(result["unknowns"], errors)
    conflict_ids, blocking_conflict = validate_conflicts(result["conflicts"], errors)
    discovery_performed = validate_discovery(result["existing_solution_discovery"], errors)
    option_ids = validate_options(result["solution_options"], claim_ids, errors)
    verification_ids, blocking_verification = validate_verification(result["required_verification"], errors)

    all_ids = claim_ids | unknown_ids | conflict_ids | option_ids | verification_ids
    expected_count = (
        len(claim_ids)
        + len(unknown_ids)
        + len(conflict_ids)
        + len(option_ids)
        + len(verification_ids)
    )
    require(len(all_ids) == expected_count, errors, "$: result-local IDs must be unique across collections")

    status = result["status"]

    if status == "COMPLETED":
        require(not blocking_unknown, errors, "$.status: COMPLETED with blocking unknown")
        require(not blocking_conflict, errors, "$.status: COMPLETED with unresolved blocking conflict")
        require(not blocking_verification, errors, "$.status: COMPLETED with blocking verification")

    validate_proposal(
        result["proposal"],
        status,
        option_ids,
        claim_ids,
        discovery_performed,
        errors,
    )

    handoff = result["implementation_handoff"]
    if require_keys(handoff, ["ready", "notes"], errors, "$.implementation_handoff"):
        ready = handoff.get("ready")
        require(isinstance(ready, bool), errors, "$.implementation_handoff.ready: expected boolean")
        require(string_list(handoff.get("notes")), errors, "$.implementation_handoff.notes: expected string array")
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
            require(
                nonempty_string(capability["purpose"]),
                errors,
                f"$.requested_capabilities[{index}].purpose: must be non-empty",
            )

    next_action = result["next_action"]
    if require_keys(next_action, ["type", "description"], errors, "$.next_action"):
        action_type = next_action.get("type")
        require(action_type in NEXT_ACTIONS, errors, "$.next_action.type: invalid")
        require(isinstance(next_action.get("description"), str), errors, "$.next_action.description: expected string")
        if status != "COMPLETED":
            require(
                action_type != "HANDOFF_IMPLEMENTATION",
                errors,
                "$.next_action: non-COMPLETED cannot hand off implementation",
            )

    return errors


def get_path(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def validate_case_assertions(case: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    case_id = case.get("id")
    require(result.get("task_id") == case_id, errors, f"$.task_id: expected case id {case_id}")

    assertions = case.get("output_assertions")
    if not isinstance(assertions, dict):
        return errors

    allowed_status = assertions.get("allowed_status")
    if isinstance(allowed_status, list):
        require(
            result.get("status") in allowed_status,
            errors,
            f"case: status {result.get('status')} not in allowed_status {allowed_status}",
        )

    required_nonempty = assertions.get("required_nonempty", [])
    if isinstance(required_nonempty, list):
        for dotted_path in required_nonempty:
            actual = get_path(result, dotted_path)
            require(bool(actual), errors, f"case: {dotted_path} must be non-empty")

    if assertions.get("require_discovery_performed") is True:
        require(
            result.get("existing_solution_discovery", {}).get("performed") is True,
            errors,
            "case: existing_solution_discovery.performed must be true",
        )

    proposal_rule = assertions.get("proposal")
    if proposal_rule == "NULL":
        require(result.get("proposal") is None, errors, "case: proposal must be null")
    elif proposal_rule == "NON_NULL":
        require(isinstance(result.get("proposal"), dict), errors, "case: proposal must be non-null object")

    forbidden_capabilities = set(assertions.get("forbidden_capabilities", []))
    for index, capability in enumerate(result.get("requested_capabilities", [])):
        if isinstance(capability, dict):
            verb = capability.get("verb")
            require(
                verb not in forbidden_capabilities,
                errors,
                f"case: requested_capabilities[{index}] uses forbidden {verb}",
            )

    if assertions.get("require_unresolved_blocking_conflict") is True:
        conflicts = result.get("conflicts", [])
        found = any(
            isinstance(conflict, dict)
            and conflict.get("material") is True
            and conflict.get("blocks_decision") is True
            and conflict.get("status") == "UNRESOLVED"
            for conflict in conflicts
        )
        require(found, errors, "case: unresolved material blocking conflict required")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="Technical Architect result JSON")
    parser.add_argument("--case", type=Path, help="optional M1 evaluation case JSON")
    parser.add_argument("--json", action="store_true", help="emit machine-readable validation report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        result = json.loads(args.result.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            raise ValidationError("result root must be object")

        structural_errors = validate_result(result)
        case_errors: list[str] = []

        if args.case:
            case = json.loads(args.case.read_text(encoding="utf-8"))
            if not isinstance(case, dict):
                raise ValidationError("case root must be object")
            case_errors = validate_case_assertions(case, result)

    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        print(f"M1 RESULT VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    errors = structural_errors + case_errors
    report = {
        "contract_version": CONTRACT_VERSION,
        "result_file": str(args.result),
        "case_file": str(args.case) if args.case else None,
        "valid": not errors,
        "structural_errors": structural_errors,
        "case_errors": case_errors,
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
