#!/usr/bin/env python3
"""Validate and fingerprint an M1 SAP Technical Architect input envelope.

Python standard library only.
This validator checks structural/safety invariants, evidence references, secret isolation,
and the M1 capability boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "m1.technical-architect-input.v1"
RESULT_CONTRACT_VERSION = "m1.technical-architect-result.v1"
REQUESTED_OUTCOME = "ARCHITECTURE_ASSESSMENT"

CLAIM_CLASSES = {"VERIFIED", "KNOWN", "INFERRED", "ASSUMED"}
ALLOWED_CAPABILITIES = {"READ", "QUERY", "ANALYZE", "PROPOSE"}
MUTATING_CAPABILITIES = {"WRITE", "DEPLOY", "TRANSPORT", "ADMIN"}
AUTHORITIES = {
    "SYSTEM_VERIFIED",
    "PROJECT_APPROVED",
    "ORGANIZATION_APPROVED",
    "OFFICIAL_VENDOR",
    "INTERNAL_REFERENCE",
    "USER_PROVIDED",
}
EVIDENCE_TYPES = {
    "LIVE_SYSTEM",
    "SOURCE_CODE",
    "EXECUTION_RESULT",
    "TEST_RESULT",
    "STATIC_ANALYSIS",
    "LOG",
    "CONFIGURATION",
    "APPROVED_DOCUMENT",
    "DECISION_RECORD",
    "OFFICIAL_DOCUMENTATION",
    "USER_CONFIRMATION",
}
FINGERPRINT_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
ID_PATTERNS = {
    "constraint": re.compile(r"^K-[0-9]{3,}$"),
    "claim": re.compile(r"^IC-[0-9]{3,}$"),
    "unknown": re.compile(r"^IU-[0-9]{3,}$"),
    "conflict": re.compile(r"^IX-[0-9]{3,}$"),
    "evidence": re.compile(r"^E-[0-9]{3,}$"),
}
TOP_LEVEL_KEYS = {
    "contract_version",
    "task",
    "scope",
    "constraints",
    "context",
    "evidence_catalog",
    "capability_boundary",
    "resolved_configuration_fingerprint",
    "requested_result_contract",
}
FORBIDDEN_SECRET_KEYS = {
    "password",
    "client_secret",
    "api_key",
    "private_key",
    "access_token",
    "refresh_token",
}


class ValidationError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def input_fingerprint(value: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


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


def contains_raw_secret(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []

    if isinstance(value, dict):
        for key, nested in value.items():
            child = f"{path}.{key}"
            if key.lower() in FORBIDDEN_SECRET_KEYS and nested not in (None, ""):
                errors.append(f"{child}: raw secret material forbidden")
            errors.extend(contains_raw_secret(nested, child))

    elif isinstance(value, list):
        for index, nested in enumerate(value):
            errors.extend(contains_raw_secret(nested, f"{path}[{index}]"))

    return errors


def validate_input(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(value, dict):
        return ["$: expected object"]

    missing = sorted(TOP_LEVEL_KEYS - set(value))
    unknown = sorted(set(value) - TOP_LEVEL_KEYS)
    for key in missing:
        errors.append(f"$: missing {key}")
    for key in unknown:
        errors.append(f"$: unknown top-level field {key}")
    if errors:
        return errors

    require(value["contract_version"] == CONTRACT_VERSION, errors, "$.contract_version: unsupported")
    require(
        value["requested_result_contract"] == RESULT_CONTRACT_VERSION,
        errors,
        "$.requested_result_contract: unsupported",
    )

    config_fingerprint = value["resolved_configuration_fingerprint"]
    require(
        isinstance(config_fingerprint, str)
        and FINGERPRINT_PATTERN.fullmatch(config_fingerprint) is not None,
        errors,
        "$.resolved_configuration_fingerprint: invalid sha256 fingerprint",
    )

    task = value["task"]
    if require_keys(task, ["id", "requirement", "requested_outcome"], errors, "$.task"):
        require(nonempty_string(task["id"]), errors, "$.task.id: must be non-empty")
        require(nonempty_string(task["requirement"]), errors, "$.task.requirement: must be non-empty")
        require(
            task["requested_outcome"] == REQUESTED_OUTCOME,
            errors,
            "$.task.requested_outcome: unsupported",
        )

    scope = value["scope"]
    if require_keys(
        scope,
        ["modules", "systems", "environments", "project", "landscape"],
        errors,
        "$.scope",
    ):
        require(string_list(scope["modules"]), errors, "$.scope.modules: expected string array")
        require(string_list(scope["systems"]), errors, "$.scope.systems: expected string array")
        require(string_list(scope["environments"]), errors, "$.scope.environments: expected string array")
        require(
            scope["project"] is None or isinstance(scope["project"], str),
            errors,
            "$.scope.project: expected string or null",
        )
        require(
            scope["landscape"] is None or isinstance(scope["landscape"], str),
            errors,
            "$.scope.landscape: expected string or null",
        )

    constraint_ids = validate_unique_ids(
        value["constraints"],
        ID_PATTERNS["constraint"],
        errors,
        "$.constraints",
    )
    if isinstance(value["constraints"], list):
        for index, constraint in enumerate(value["constraints"]):
            if not isinstance(constraint, dict):
                continue
            if not require_keys(
                constraint,
                ["id", "statement", "authority", "source_refs"],
                errors,
                f"$.constraints[{index}]",
            ):
                continue
            require(
                nonempty_string(constraint["statement"]),
                errors,
                f"$.constraints[{index}].statement: must be non-empty",
            )
            require(
                constraint["authority"] in AUTHORITIES,
                errors,
                f"$.constraints[{index}].authority: invalid",
            )
            require(
                string_list(constraint["source_refs"]),
                errors,
                f"$.constraints[{index}].source_refs: expected string array",
            )

    evidence_ids = validate_unique_ids(
        value["evidence_catalog"],
        ID_PATTERNS["evidence"],
        errors,
        "$.evidence_catalog",
    )
    if isinstance(value["evidence_catalog"], list):
        for index, evidence in enumerate(value["evidence_catalog"]):
            if not isinstance(evidence, dict):
                continue
            if not require_keys(
                evidence,
                ["id", "type", "source_ref", "revision", "summary"],
                errors,
                f"$.evidence_catalog[{index}]",
            ):
                continue
            require(
                evidence["type"] in EVIDENCE_TYPES,
                errors,
                f"$.evidence_catalog[{index}].type: invalid",
            )
            require(
                nonempty_string(evidence["source_ref"]),
                errors,
                f"$.evidence_catalog[{index}].source_ref: must be non-empty",
            )
            require(
                evidence["revision"] is None or isinstance(evidence["revision"], str),
                errors,
                f"$.evidence_catalog[{index}].revision: expected string or null",
            )
            require(
                nonempty_string(evidence["summary"]),
                errors,
                f"$.evidence_catalog[{index}].summary: must be non-empty",
            )

    context = value["context"]
    claim_ids: set[str] = set()
    unknown_ids: set[str] = set()
    conflict_ids: set[str] = set()

    if require_keys(context, ["claims", "unknowns", "conflicts"], errors, "$.context"):
        claim_ids = validate_unique_ids(
            context["claims"],
            ID_PATTERNS["claim"],
            errors,
            "$.context.claims",
        )
        unknown_ids = validate_unique_ids(
            context["unknowns"],
            ID_PATTERNS["unknown"],
            errors,
            "$.context.unknowns",
        )
        conflict_ids = validate_unique_ids(
            context["conflicts"],
            ID_PATTERNS["conflict"],
            errors,
            "$.context.conflicts",
        )

        if isinstance(context["claims"], list):
            for index, claim in enumerate(context["claims"]):
                if not isinstance(claim, dict):
                    continue
                if not require_keys(
                    claim,
                    ["id", "classification", "statement", "system_specific", "evidence_refs", "source_refs"],
                    errors,
                    f"$.context.claims[{index}]",
                ):
                    continue

                classification = claim["classification"]
                evidence_refs = claim["evidence_refs"]
                source_refs = claim["source_refs"]

                require(
                    classification in CLAIM_CLASSES,
                    errors,
                    f"$.context.claims[{index}].classification: invalid",
                )
                require(
                    nonempty_string(claim["statement"]),
                    errors,
                    f"$.context.claims[{index}].statement: must be non-empty",
                )
                require(
                    isinstance(claim["system_specific"], bool),
                    errors,
                    f"$.context.claims[{index}].system_specific: expected boolean",
                )
                require(
                    string_list(evidence_refs),
                    errors,
                    f"$.context.claims[{index}].evidence_refs: expected string array",
                )
                require(
                    string_list(source_refs),
                    errors,
                    f"$.context.claims[{index}].source_refs: expected string array",
                )

                for evidence_ref in evidence_refs if isinstance(evidence_refs, list) else []:
                    require(
                        evidence_ref in evidence_ids,
                        errors,
                        f"$.context.claims[{index}].evidence_refs: unknown {evidence_ref}",
                    )

                if classification == "VERIFIED":
                    require(
                        bool(evidence_refs),
                        errors,
                        f"$.context.claims[{index}]: VERIFIED requires catalogued evidence",
                    )
                elif classification == "KNOWN":
                    require(
                        bool(evidence_refs) or bool(source_refs),
                        errors,
                        f"$.context.claims[{index}]: KNOWN requires evidence or source provenance",
                    )

        if isinstance(context["unknowns"], list):
            for index, unknown_item in enumerate(context["unknowns"]):
                if not isinstance(unknown_item, dict):
                    continue
                if not require_keys(
                    unknown_item,
                    ["id", "statement", "material", "blocks_decision", "verification"],
                    errors,
                    f"$.context.unknowns[{index}]",
                ):
                    continue
                require(
                    nonempty_string(unknown_item["statement"]),
                    errors,
                    f"$.context.unknowns[{index}].statement: must be non-empty",
                )
                require(
                    isinstance(unknown_item["material"], bool),
                    errors,
                    f"$.context.unknowns[{index}].material: expected boolean",
                )
                require(
                    isinstance(unknown_item["blocks_decision"], bool),
                    errors,
                    f"$.context.unknowns[{index}].blocks_decision: expected boolean",
                )
                require(
                    nonempty_string(unknown_item["verification"]),
                    errors,
                    f"$.context.unknowns[{index}].verification: must be non-empty",
                )

        if isinstance(context["conflicts"], list):
            for index, conflict in enumerate(context["conflicts"]):
                if not isinstance(conflict, dict):
                    continue
                if not require_keys(
                    conflict,
                    ["id", "statement", "material", "blocks_decision", "source_refs", "verification"],
                    errors,
                    f"$.context.conflicts[{index}]",
                ):
                    continue
                refs = conflict["source_refs"]
                require(
                    nonempty_string(conflict["statement"]),
                    errors,
                    f"$.context.conflicts[{index}].statement: must be non-empty",
                )
                require(
                    isinstance(conflict["material"], bool),
                    errors,
                    f"$.context.conflicts[{index}].material: expected boolean",
                )
                require(
                    isinstance(conflict["blocks_decision"], bool),
                    errors,
                    f"$.context.conflicts[{index}].blocks_decision: expected boolean",
                )
                require(
                    string_list(refs) and len(set(refs)) >= 2,
                    errors,
                    f"$.context.conflicts[{index}]: requires at least two unique source_refs",
                )
                require(
                    nonempty_string(conflict["verification"]),
                    errors,
                    f"$.context.conflicts[{index}].verification: must be non-empty",
                )

    all_ids = constraint_ids | evidence_ids | claim_ids | unknown_ids | conflict_ids
    expected_count = (
        len(constraint_ids)
        + len(evidence_ids)
        + len(claim_ids)
        + len(unknown_ids)
        + len(conflict_ids)
    )
    require(len(all_ids) == expected_count, errors, "$: input-local IDs must be unique across collections")

    capabilities = value["capability_boundary"]
    if not isinstance(capabilities, list):
        errors.append("$.capability_boundary: expected array")
    else:
        require(
            len(capabilities) == len(set(capabilities)),
            errors,
            "$.capability_boundary: duplicate capability",
        )
        for index, verb in enumerate(capabilities):
            require(
                verb in ALLOWED_CAPABILITIES,
                errors,
                f"$.capability_boundary[{index}]: forbidden capability {verb}",
            )
            require(
                verb not in MUTATING_CAPABILITIES,
                errors,
                f"$.capability_boundary[{index}]: mutation/admin capability forbidden",
            )

    errors.extend(contains_raw_secret(value))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Technical Architect input JSON")
    parser.add_argument("--json", action="store_true", help="emit machine-readable validation report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        value = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValidationError("input root must be object")
        errors = validate_input(value)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        print(f"M1 INPUT VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    report = {
        "contract_version": CONTRACT_VERSION,
        "input_file": str(args.input),
        "valid": not errors,
        "input_fingerprint": input_fingerprint(value) if not errors else None,
        "resolved_configuration_fingerprint": value.get("resolved_configuration_fingerprint"),
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("PASS" if report["valid"] else "FAIL")
        if report["input_fingerprint"]:
            print(f"input_fingerprint: {report['input_fingerprint']}")
        for error in errors:
            print(f"- {error}")

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
