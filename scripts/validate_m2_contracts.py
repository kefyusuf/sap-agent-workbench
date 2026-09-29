#!/usr/bin/env python3
"""Validate M2 ABAP Development design fixtures/results.

Python standard library only.
This is deterministic evaluation tooling, not the M2 Agent runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

INPUT_VERSION = "m2.abap-development-input.v1"
RESULT_VERSION = "m2.abap-development-result.v1"

ALLOWED_CAPABILITIES = {"READ", "QUERY", "ANALYZE", "PROPOSE"}
RESULT_STATUSES = {"WORK_PRODUCT_READY", "NEEDS_CLARIFICATION", "BLOCKED"}
ALIGNMENT_STATUSES = {"PRESERVED", "REQUIRES_REVIEW"}
OBJECT_KINDS = {
    "CLASS",
    "INTERFACE",
    "TABLE",
    "STRUCTURE",
    "FUNCTION_MODULE",
    "BADI_DEFINITION",
    "BADI_IMPLEMENTATION",
    "ENHANCEMENT",
    "CDS",
    "RAP_OBJECT",
    "ODATA_SERVICE",
    "FORM",
    "JOB",
    "OTHER",
}
PROPOSED_OBJECT_KINDS = OBJECT_KINDS - {"BADI_DEFINITION", "JOB"} | {"OTHER"}
VERIFICATION_COMPATIBILITY = {
    "COMPILE": {"EXECUTION_RESULT", "STATIC_ANALYSIS"},
    "ATC": {"STATIC_ANALYSIS"},
    "UNIT_TEST": {"TEST_RESULT"},
    "INTEGRATION_TEST": {"TEST_RESULT"},
    "AUTHORIZATION": {"TEST_RESULT", "CONFIGURATION"},
    "PERFORMANCE": {"TEST_RESULT", "EXECUTION_RESULT"},
    "PAYLOAD_CONTRACT": {"TEST_RESULT", "EXECUTION_RESULT"},
    "RUNTIME": {"EXECUTION_RESULT", "LOG"},
}
FORBIDDEN_SECRET_KEYS = {
    "password",
    "client_secret",
    "api_key",
    "private_key",
    "access_token",
    "refresh_token",
}
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")

ID_PATTERNS = {
    "handoff": re.compile(r"^AH-[0-9]{3,}$"),
    "constraint": re.compile(r"^AC-[0-9]{3,}$"),
    "requirement": re.compile(r"^REQ-[0-9]{3,}$"),
    "existing": re.compile(r"^OBJ-[0-9]{3,}$"),
    "input_unknown": re.compile(r"^IU-[0-9]{3,}$"),
    "evidence": re.compile(r"^E-[0-9]{3,}$"),
    "result_unknown": re.compile(r"^U-[0-9]{3,}$"),
    "proposed": re.compile(r"^NEW-[0-9]{3,}$"),
    "plan": re.compile(r"^PLAN-[0-9]{3,}$"),
    "work_product": re.compile(r"^WP-[0-9]{3,}$"),
    "assumption": re.compile(r"^A-[0-9]{3,}$"),
    "risk": re.compile(r"^R-[0-9]{3,}$"),
    "verification": re.compile(r"^V-[0-9]{3,}$"),
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def is_record(value: Any) -> bool:
    return isinstance(value, dict)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_id_items(
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
        if not is_record(item):
            errors.append(f"{path}[{index}]: expected object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or pattern.fullmatch(item_id) is None:
            errors.append(f"{path}[{index}].id: invalid")
            continue
        if item_id in ids:
            errors.append(f"{path}[{index}].id: duplicate {item_id}")
        ids.add(item_id)
    return ids


def secret_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, list):
        for index, nested in enumerate(value):
            errors.extend(secret_errors(nested, f"{path}[{index}]"))
    elif isinstance(value, dict):
        for key, nested in value.items():
            child = f"{path}.{key}"
            if key.lower() in FORBIDDEN_SECRET_KEYS and nested not in (None, ""):
                errors.append(f"{child}: raw secret material forbidden")
            errors.extend(secret_errors(nested, child))
    return errors


def validate_input(value: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    metadata: dict[str, Any] = {}

    if not is_record(value):
        return ["input: expected object"], metadata

    require(value.get("contract_version") == INPUT_VERSION, errors, "input.contract_version: unsupported")
    require(value.get("requested_result_contract") == RESULT_VERSION, errors, "input.requested_result_contract: unsupported")
    require(
        isinstance(value.get("resolved_configuration_fingerprint"), str)
        and FINGERPRINT.fullmatch(value["resolved_configuration_fingerprint"]) is not None,
        errors,
        "input.resolved_configuration_fingerprint: invalid",
    )

    task = value.get("task")
    if not is_record(task):
        errors.append("input.task: expected object")
    else:
        require(is_nonempty_string(task.get("id")), errors, "input.task.id: invalid")
        require(
            is_nonempty_string(task.get("implementation_objective")),
            errors,
            "input.task.implementation_objective: invalid",
        )
        require(
            task.get("requested_outcome") == "IMPLEMENTATION_WORK_PRODUCT",
            errors,
            "input.task.requested_outcome: unsupported",
        )

    handoff = value.get("architecture_handoff")
    constraint_ids: set[str] = set()
    material_constraint_ids: set[str] = set()
    if not is_record(handoff):
        errors.append("input.architecture_handoff: expected object")
    else:
        require(
            isinstance(handoff.get("id"), str)
            and ID_PATTERNS["handoff"].fullmatch(handoff["id"]) is not None,
            errors,
            "input.architecture_handoff.id: invalid",
        )
        require(
            isinstance(handoff.get("fingerprint"), str)
            and FINGERPRINT.fullmatch(handoff["fingerprint"]) is not None,
            errors,
            "input.architecture_handoff.fingerprint: invalid",
        )
        require(
            handoff.get("status") in {"APPROVED", "APPROVED_WITH_VERIFICATION"},
            errors,
            "input.architecture_handoff.status: invalid",
        )
        require(is_nonempty_string(handoff.get("approach")), errors, "input.architecture_handoff.approach: invalid")
        constraint_ids = validate_id_items(
            handoff.get("constraints"),
            ID_PATTERNS["constraint"],
            errors,
            "input.architecture_handoff.constraints",
        )
        if isinstance(handoff.get("constraints"), list):
            for index, constraint in enumerate(handoff["constraints"]):
                if not is_record(constraint):
                    continue
                require(
                    is_nonempty_string(constraint.get("statement")),
                    errors,
                    f"input.architecture_handoff.constraints[{index}].statement: invalid",
                )
                require(
                    isinstance(constraint.get("material"), bool),
                    errors,
                    f"input.architecture_handoff.constraints[{index}].material: expected boolean",
                )
                if constraint.get("material") is True and isinstance(constraint.get("id"), str):
                    material_constraint_ids.add(constraint["id"])

    evidence_ids = validate_id_items(
        value.get("evidence_catalog"),
        ID_PATTERNS["evidence"],
        errors,
        "input.evidence_catalog",
    )
    evidence_types: dict[str, str] = {}
    source_refs: set[str] = set()

    if isinstance(value.get("evidence_catalog"), list):
        for index, evidence in enumerate(value["evidence_catalog"]):
            if not is_record(evidence):
                continue
            evidence_id = evidence.get("id")
            evidence_type = evidence.get("type")
            if isinstance(evidence_id, str) and isinstance(evidence_type, str):
                evidence_types[evidence_id] = evidence_type
            require(
                is_nonempty_string(evidence.get("source_ref")),
                errors,
                f"input.evidence_catalog[{index}].source_ref: invalid",
            )
            if is_nonempty_string(evidence.get("source_ref")):
                source_refs.add(evidence["source_ref"])
            require(
                is_nonempty_string(evidence.get("summary")),
                errors,
                f"input.evidence_catalog[{index}].summary: invalid",
            )

    requirement_ids = validate_id_items(
        value.get("requirements"),
        ID_PATTERNS["requirement"],
        errors,
        "input.requirements",
    )
    if isinstance(value.get("requirements"), list):
        for index, requirement in enumerate(value["requirements"]):
            if not is_record(requirement):
                continue
            require(
                is_nonempty_string(requirement.get("statement")),
                errors,
                f"input.requirements[{index}].statement: invalid",
            )
            refs = requirement.get("evidence_refs")
            require(is_string_list(refs), errors, f"input.requirements[{index}].evidence_refs: expected string array")
            if is_string_list(refs):
                for ref in refs:
                    require(ref in evidence_ids, errors, f"input.requirements[{index}].evidence_refs: unknown {ref}")
            if is_string_list(requirement.get("source_refs")):
                source_refs.update(requirement["source_refs"])

    existing_ids = validate_id_items(
        value.get("existing_objects"),
        ID_PATTERNS["existing"],
        errors,
        "input.existing_objects",
    )
    existing_names: set[str] = set()
    if isinstance(value.get("existing_objects"), list):
        for index, obj in enumerate(value["existing_objects"]):
            if not is_record(obj):
                continue
            name = obj.get("name")
            require(is_nonempty_string(name), errors, f"input.existing_objects[{index}].name: invalid")
            if is_nonempty_string(name):
                require(name not in existing_names, errors, f"input.existing_objects[{index}].name: duplicate {name}")
                existing_names.add(name)
            require(obj.get("kind") in OBJECT_KINDS, errors, f"input.existing_objects[{index}].kind: invalid")
            refs = obj.get("evidence_refs")
            require(is_string_list(refs), errors, f"input.existing_objects[{index}].evidence_refs: expected string array")
            if is_string_list(refs):
                for ref in refs:
                    require(ref in evidence_ids, errors, f"input.existing_objects[{index}].evidence_refs: unknown {ref}")
            if is_string_list(obj.get("source_refs")):
                source_refs.update(obj["source_refs"])

    unknown_ids = validate_id_items(
        value.get("unknowns"),
        ID_PATTERNS["input_unknown"],
        errors,
        "input.unknowns",
    )
    blocking_input_unknowns: set[str] = set()
    if isinstance(value.get("unknowns"), list):
        for index, unknown in enumerate(value["unknowns"]):
            if not is_record(unknown):
                continue
            require(is_nonempty_string(unknown.get("statement")), errors, f"input.unknowns[{index}].statement: invalid")
            require(isinstance(unknown.get("material"), bool), errors, f"input.unknowns[{index}].material: expected boolean")
            require(
                isinstance(unknown.get("blocks_implementation"), bool),
                errors,
                f"input.unknowns[{index}].blocks_implementation: expected boolean",
            )
            require(is_nonempty_string(unknown.get("verification")), errors, f"input.unknowns[{index}].verification: invalid")
            if (
                unknown.get("material") is True
                and unknown.get("blocks_implementation") is True
                and isinstance(unknown.get("id"), str)
            ):
                blocking_input_unknowns.add(unknown["id"])

    all_local_ids = constraint_ids | requirement_ids | existing_ids | unknown_ids | evidence_ids
    expected_count = (
        len(constraint_ids)
        + len(requirement_ids)
        + len(existing_ids)
        + len(unknown_ids)
        + len(evidence_ids)
    )
    require(len(all_local_ids) == expected_count, errors, "input: local IDs must be unique across collections")

    capabilities = value.get("capability_boundary")
    require(isinstance(capabilities, list), errors, "input.capability_boundary: expected array")
    if isinstance(capabilities, list):
        require(len(capabilities) == len(set(capabilities)), errors, "input.capability_boundary: duplicates")
        for index, capability in enumerate(capabilities):
            require(
                capability in ALLOWED_CAPABILITIES,
                errors,
                f"input.capability_boundary[{index}]: forbidden {capability}",
            )

    errors.extend(secret_errors(value))

    if not errors:
        metadata = {
            "input_fingerprint": fingerprint(value),
            "configuration_fingerprint": value["resolved_configuration_fingerprint"],
            "architecture_handoff_fingerprint": handoff["fingerprint"],
            "constraint_ids": constraint_ids,
            "material_constraint_ids": material_constraint_ids,
            "existing_ids": existing_ids,
            "existing_names": existing_names,
            "blocking_input_unknowns": blocking_input_unknowns,
            "evidence_ids": evidence_ids,
            "evidence_types": evidence_types,
            "source_refs": source_refs,
        }

    return errors, metadata


def validate_result(
    result: Any,
    case: dict[str, Any],
    metadata: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not is_record(result):
        return ["result: expected object"]

    require(result.get("contract_version") == RESULT_VERSION, errors, "result.contract_version: unsupported")
    require(result.get("task_id") == case.get("id"), errors, "result.task_id: case mismatch")

    provenance = result.get("provenance")
    if not is_record(provenance):
        errors.append("result.provenance: expected object")
    else:
        require(
            provenance.get("input_fingerprint") == metadata["input_fingerprint"],
            errors,
            "result.provenance.input_fingerprint: mismatch",
        )
        require(
            provenance.get("configuration_fingerprint") == metadata["configuration_fingerprint"],
            errors,
            "result.provenance.configuration_fingerprint: mismatch",
        )
        require(
            provenance.get("architecture_handoff_fingerprint") == metadata["architecture_handoff_fingerprint"],
            errors,
            "result.provenance.architecture_handoff_fingerprint: mismatch",
        )

    status = result.get("status")
    require(status in RESULT_STATUSES, errors, "result.status: invalid")

    alignment = result.get("architecture_alignment")
    result_constraint_refs: set[str] = set()
    requires_review = False
    if not is_record(alignment):
        errors.append("result.architecture_alignment: expected object")
    else:
        require(alignment.get("status") in ALIGNMENT_STATUSES, errors, "result.architecture_alignment.status: invalid")
        requires_review = alignment.get("status") == "REQUIRES_REVIEW"
        items = alignment.get("constraint_results")
        require(isinstance(items, list), errors, "result.architecture_alignment.constraint_results: expected array")
        if isinstance(items, list):
            for index, item in enumerate(items):
                if not is_record(item):
                    errors.append(f"result.architecture_alignment.constraint_results[{index}]: expected object")
                    continue
                ref = item.get("constraint_ref")
                require(ref in metadata["constraint_ids"], errors, f"result.architecture_alignment.constraint_results[{index}]: unknown {ref}")
                if isinstance(ref, str):
                    require(ref not in result_constraint_refs, errors, f"result.architecture_alignment.constraint_results[{index}]: duplicate {ref}")
                    result_constraint_refs.add(ref)
                require(item.get("status") in ALIGNMENT_STATUSES, errors, f"result.architecture_alignment.constraint_results[{index}].status: invalid")
                if item.get("status") == "REQUIRES_REVIEW":
                    requires_review = True
        if status == "WORK_PRODUCT_READY":
            missing_material = metadata["material_constraint_ids"] - result_constraint_refs
            require(not missing_material, errors, f"result.architecture_alignment: missing material constraints {sorted(missing_material)}")
            require(not requires_review, errors, "result.status: WORK_PRODUCT_READY with architecture review required")

    result_unknown_ids = validate_id_items(
        result.get("unknowns"),
        ID_PATTERNS["result_unknown"],
        errors,
        "result.unknowns",
    )
    blocking_result_unknown = False
    if isinstance(result.get("unknowns"), list):
        for index, unknown in enumerate(result["unknowns"]):
            if not is_record(unknown):
                continue
            require(is_nonempty_string(unknown.get("statement")), errors, f"result.unknowns[{index}].statement: invalid")
            require(isinstance(unknown.get("material"), bool), errors, f"result.unknowns[{index}].material: expected boolean")
            require(
                isinstance(unknown.get("blocks_work_product"), bool),
                errors,
                f"result.unknowns[{index}].blocks_work_product: expected boolean",
            )
            require(is_nonempty_string(unknown.get("verification")), errors, f"result.unknowns[{index}].verification: invalid")
            if unknown.get("material") is True and unknown.get("blocks_work_product") is True:
                blocking_result_unknown = True

    if status == "WORK_PRODUCT_READY":
        require(
            not metadata["blocking_input_unknowns"],
            errors,
            "result.status: WORK_PRODUCT_READY while input has blocking implementation unknowns",
        )
        require(not blocking_result_unknown, errors, "result.status: WORK_PRODUCT_READY with blocking result unknown")

    existing_used = result.get("existing_objects_used")
    used_existing_refs: set[str] = set()
    require(isinstance(existing_used, list), errors, "result.existing_objects_used: expected array")
    if isinstance(existing_used, list):
        for index, item in enumerate(existing_used):
            if not is_record(item):
                errors.append(f"result.existing_objects_used[{index}]: expected object")
                continue
            ref = item.get("object_ref")
            require(ref in metadata["existing_ids"], errors, f"result.existing_objects_used[{index}]: unknown {ref}")
            if isinstance(ref, str):
                used_existing_refs.add(ref)
            require(is_nonempty_string(item.get("purpose")), errors, f"result.existing_objects_used[{index}].purpose: invalid")

    proposed_ids = validate_id_items(
        result.get("proposed_new_objects"),
        ID_PATTERNS["proposed"],
        errors,
        "result.proposed_new_objects",
    )
    proposed_names: set[str] = set()
    if isinstance(result.get("proposed_new_objects"), list):
        for index, item in enumerate(result["proposed_new_objects"]):
            if not is_record(item):
                continue
            name = item.get("proposed_name")
            require(is_nonempty_string(name), errors, f"result.proposed_new_objects[{index}].proposed_name: invalid")
            if is_nonempty_string(name):
                require(name not in metadata["existing_names"], errors, f"result.proposed_new_objects[{index}]: proposed name matches existing object {name}")
                require(name not in proposed_names, errors, f"result.proposed_new_objects[{index}]: duplicate proposed name {name}")
                proposed_names.add(name)
            require(item.get("kind") in PROPOSED_OBJECT_KINDS, errors, f"result.proposed_new_objects[{index}].kind: invalid")
            require(is_nonempty_string(item.get("purpose")), errors, f"result.proposed_new_objects[{index}].purpose: invalid")

    valid_object_refs = metadata["existing_ids"] | proposed_ids

    plan_ids = validate_id_items(
        result.get("implementation_plan"),
        ID_PATTERNS["plan"],
        errors,
        "result.implementation_plan",
    )
    if isinstance(result.get("implementation_plan"), list):
        for index, item in enumerate(result["implementation_plan"]):
            if not is_record(item):
                continue
            require(is_nonempty_string(item.get("description")), errors, f"result.implementation_plan[{index}].description: invalid")
            refs = item.get("object_refs")
            require(is_string_list(refs), errors, f"result.implementation_plan[{index}].object_refs: expected string array")
            if is_string_list(refs):
                for ref in refs:
                    require(ref in valid_object_refs, errors, f"result.implementation_plan[{index}].object_refs: unknown {ref}")

    work_product_ids = validate_id_items(
        result.get("work_products"),
        ID_PATTERNS["work_product"],
        errors,
        "result.work_products",
    )
    if isinstance(result.get("work_products"), list):
        for index, item in enumerate(result["work_products"]):
            if not is_record(item):
                continue
            ref = item.get("target_object_ref")
            require(ref in valid_object_refs, errors, f"result.work_products[{index}].target_object_ref: unknown {ref}")
            require(is_nonempty_string(item.get("content")), errors, f"result.work_products[{index}].content: invalid")

    assumption_ids = validate_id_items(
        result.get("assumptions"),
        ID_PATTERNS["assumption"],
        errors,
        "result.assumptions",
    )
    risk_ids = validate_id_items(
        result.get("risks"),
        ID_PATTERNS["risk"],
        errors,
        "result.risks",
    )
    verification_ids = validate_id_items(
        result.get("required_verification"),
        ID_PATTERNS["verification"],
        errors,
        "result.required_verification",
    )

    verification_claims = result.get("verification_claims")
    require(isinstance(verification_claims, list), errors, "result.verification_claims: expected array")
    if isinstance(verification_claims, list):
        for index, claim in enumerate(verification_claims):
            if not is_record(claim):
                errors.append(f"result.verification_claims[{index}]: expected object")
                continue
            verification_type = claim.get("type")
            require(claim.get("status") in {"PASS", "FAIL"}, errors, f"result.verification_claims[{index}].status: invalid")
            refs = claim.get("evidence_refs")
            require(is_string_list(refs) and bool(refs), errors, f"result.verification_claims[{index}].evidence_refs: non-empty array required")
            if is_string_list(refs):
                compatible = VERIFICATION_COMPATIBILITY.get(str(verification_type))
                for ref in refs:
                    require(ref in metadata["evidence_ids"], errors, f"result.verification_claims[{index}].evidence_refs: unknown {ref}")
                    if ref in metadata["evidence_types"] and compatible is not None:
                        require(
                            metadata["evidence_types"][ref] in compatible,
                            errors,
                            f"result.verification_claims[{index}]: evidence {ref} type {metadata['evidence_types'][ref]} incompatible with {verification_type}",
                        )

    all_result_ids = (
        result_unknown_ids
        | proposed_ids
        | plan_ids
        | work_product_ids
        | assumption_ids
        | risk_ids
        | verification_ids
    )
    expected_result_count = (
        len(result_unknown_ids)
        + len(proposed_ids)
        + len(plan_ids)
        + len(work_product_ids)
        + len(assumption_ids)
        + len(risk_ids)
        + len(verification_ids)
    )
    require(
        len(all_result_ids) == expected_result_count,
        errors,
        "result: local IDs must be unique across collections",
    )

    review = result.get("review_handoff")
    if not is_record(review):
        errors.append("result.review_handoff: expected object")
    else:
        require(isinstance(review.get("ready_for_review"), bool), errors, "result.review_handoff.ready_for_review: expected boolean")
        if status == "WORK_PRODUCT_READY":
            require(review.get("ready_for_review") is True, errors, "result.review_handoff: ready result must be ready for review")
        else:
            require(review.get("ready_for_review") is False, errors, "result.review_handoff: non-ready result cannot be ready for review")

    capabilities = result.get("requested_capabilities")
    require(isinstance(capabilities, list), errors, "result.requested_capabilities: expected array")
    if isinstance(capabilities, list):
        for index, request in enumerate(capabilities):
            if not is_record(request):
                errors.append(f"result.requested_capabilities[{index}]: expected object")
                continue
            require(
                request.get("verb") in ALLOWED_CAPABILITIES,
                errors,
                f"result.requested_capabilities[{index}].verb: forbidden {request.get('verb')}",
            )
            require(is_nonempty_string(request.get("purpose")), errors, f"result.requested_capabilities[{index}].purpose: invalid")

    next_action = result.get("next_action")
    if not is_record(next_action):
        errors.append("result.next_action: expected object")
    else:
        if status != "WORK_PRODUCT_READY":
            require(
                next_action.get("type") != "HANDOFF_REVIEW",
                errors,
                "result.next_action: non-ready result cannot HANDOFF_REVIEW",
            )

    assertions = case.get("output_assertions")
    if is_record(assertions):
        allowed_status = assertions.get("allowed_status")
        if isinstance(allowed_status, list):
            require(status in allowed_status, errors, f"case: status {status} not allowed")

        expected_alignment = assertions.get("architecture_alignment")
        if expected_alignment is not None and is_record(alignment):
            require(alignment.get("status") == expected_alignment, errors, "case: architecture alignment mismatch")

        required_refs = assertions.get("required_existing_object_refs")
        if isinstance(required_refs, list):
            for ref in required_refs:
                require(ref in used_existing_refs, errors, f"case: required existing object ref missing {ref}")

        work_products = result.get("work_products")
        count = len(work_products) if isinstance(work_products, list) else 0
        min_count = assertions.get("min_work_products")
        max_count = assertions.get("max_work_products")
        if isinstance(min_count, int):
            require(count >= min_count, errors, f"case: requires at least {min_count} work products")
        if isinstance(max_count, int):
            require(count <= max_count, errors, f"case: requires at most {max_count} work products")

        if assertions.get("require_blocking_unknown") is True:
            require(blocking_result_unknown, errors, "case: blocking result unknown required")

        expected_review_ready = assertions.get("review_ready")
        if isinstance(expected_review_ready, bool) and is_record(review):
            require(review.get("ready_for_review") is expected_review_ready, errors, "case: review readiness mismatch")

        forbidden_caps = set(assertions.get("forbidden_capabilities", []))
        if isinstance(capabilities, list):
            for request in capabilities:
                if is_record(request):
                    require(request.get("verb") not in forbidden_caps, errors, f"case: forbidden capability {request.get('verb')}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True, help="M2 evaluation case JSON")
    parser.add_argument("--result", type=Path, help="optional M2 result JSON")
    parser.add_argument("--json", action="store_true", help="emit machine-readable report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        case = json.loads(args.case.read_text(encoding="utf-8"))
        if not is_record(case):
            raise ValueError("case root must be object")
        case_input = case.get("input")
        input_errors, metadata = validate_input(case_input)
        result_errors: list[str] = []

        if args.result and not input_errors:
            result = json.loads(args.result.read_text(encoding="utf-8"))
            result_errors = validate_result(result, case, metadata)

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"M2 CONTRACT VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    errors = input_errors + result_errors
    report = {
        "case": str(args.case),
        "result": str(args.result) if args.result else None,
        "valid": not errors,
        "input_fingerprint": metadata.get("input_fingerprint"),
        "input_errors": input_errors,
        "result_errors": result_errors,
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
