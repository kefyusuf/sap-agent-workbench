#!/usr/bin/env python3
"""Validate M3 Reviewer/Test Engineer design fixtures and results.

Python standard library only.
This is deterministic evaluation tooling, not an M3 Agent runtime or test executor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REVIEW_INPUT_VERSION = "m3.sap-review-input.v1"
REVIEW_RESULT_VERSION = "m3.sap-review-result.v1"
TEST_INPUT_VERSION = "m3.sap-test-plan-input.v1"
TEST_RESULT_VERSION = "m3.sap-test-plan-result.v1"

ALLOWED_CAPABILITIES = {"READ", "QUERY", "ANALYZE", "PROPOSE"}
REVIEW_OUTCOMES = {"REVIEW_ACCEPTABLE", "CHANGES_REQUIRED", "BLOCKED"}
TEST_STATUSES = {"TEST_PLAN_READY", "NEEDS_CLARIFICATION", "BLOCKED"}
ALIGNMENT_STATUSES = {"PRESERVED", "VIOLATED", "UNKNOWN"}
FINGERPRINT = re.compile(r"^sha256:[a-f0-9]{64}$")

ID_PATTERNS = {
    "constraint": re.compile(r"^AC-[0-9]{3,}$"),
    "requirement": re.compile(r"^REQ-[0-9]{3,}$"),
    "work_product": re.compile(r"^WP-[0-9]{3,}$"),
    "evidence": re.compile(r"^E-[0-9]{3,}$"),
    "review_rule": re.compile(r"^RR-[0-9]{3,}$"),
    "finding": re.compile(r"^F-[0-9]{3,}$"),
    "unknown": re.compile(r"^U-[0-9]{3,}$"),
    "input_unknown": re.compile(r"^IU-[0-9]{3,}$"),
    "risk": re.compile(r"^R-[0-9]{3,}$"),
    "check": re.compile(r"^CHK-[0-9]{3,}$"),
}

FORBIDDEN_SECRET_KEYS = {
    "password",
    "client_secret",
    "api_key",
    "private_key",
    "access_token",
    "refresh_token",
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


def validate_ids(
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
        for index, item in enumerate(value):
            errors.extend(secret_errors(item, f"{path}[{index}]"))
    elif isinstance(value, dict):
        for key, nested in value.items():
            child = f"{path}.{key}"
            if key.lower() in FORBIDDEN_SECRET_KEYS and nested not in (None, ""):
                errors.append(f"{child}: raw secret material forbidden")
            errors.extend(secret_errors(nested, child))

    return errors


def validate_capabilities(value: Any, errors: list[str], path: str) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return

    require(len(value) == len(set(value)), errors, f"{path}: duplicate capability")

    for index, capability in enumerate(value):
        require(
            capability in ALLOWED_CAPABILITIES,
            errors,
            f"{path}[{index}]: forbidden capability {capability}",
        )


def validate_evidence_catalog(
    value: Any,
    errors: list[str],
    path: str,
) -> tuple[set[str], set[str]]:
    evidence_ids = validate_ids(value, ID_PATTERNS["evidence"], errors, path)
    source_refs: set[str] = set()

    if isinstance(value, list):
        for index, evidence in enumerate(value):
            if not is_record(evidence):
                continue
            require(
                is_nonempty_string(evidence.get("source_ref")),
                errors,
                f"{path}[{index}].source_ref: invalid",
            )
            require(
                is_nonempty_string(evidence.get("summary")),
                errors,
                f"{path}[{index}].summary: invalid",
            )
            if is_nonempty_string(evidence.get("source_ref")):
                source_refs.add(evidence["source_ref"])

    return evidence_ids, source_refs


def validate_review_input(value: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    metadata: dict[str, Any] = {}

    if not is_record(value):
        return ["review input: expected object"], metadata

    require(
        value.get("contract_version") == REVIEW_INPUT_VERSION,
        errors,
        "review input.contract_version: unsupported",
    )
    require(
        value.get("requested_result_contract") == REVIEW_RESULT_VERSION,
        errors,
        "review input.requested_result_contract: unsupported",
    )
    require(
        isinstance(value.get("resolved_configuration_fingerprint"), str)
        and FINGERPRINT.fullmatch(value["resolved_configuration_fingerprint"]) is not None,
        errors,
        "review input.resolved_configuration_fingerprint: invalid",
    )

    task = value.get("task")
    if not is_record(task):
        errors.append("review input.task: expected object")
    else:
        require(is_nonempty_string(task.get("id")), errors, "review input.task.id: invalid")
        require(
            task.get("requested_outcome") == "IMPLEMENTATION_REVIEW",
            errors,
            "review input.task.requested_outcome: unsupported",
        )

    architecture = value.get("architecture_handoff")
    constraint_ids: set[str] = set()
    material_constraint_ids: set[str] = set()
    architecture_fingerprint: str | None = None

    if not is_record(architecture):
        errors.append("review input.architecture_handoff: expected object")
    else:
        architecture_fingerprint = architecture.get("fingerprint")
        require(
            isinstance(architecture_fingerprint, str)
            and FINGERPRINT.fullmatch(architecture_fingerprint) is not None,
            errors,
            "review input.architecture_handoff.fingerprint: invalid",
        )
        constraint_ids = validate_ids(
            architecture.get("constraints"),
            ID_PATTERNS["constraint"],
            errors,
            "review input.architecture_handoff.constraints",
        )
        if isinstance(architecture.get("constraints"), list):
            for index, constraint in enumerate(architecture["constraints"]):
                if not is_record(constraint):
                    continue
                require(
                    is_nonempty_string(constraint.get("statement")),
                    errors,
                    f"review input.architecture_handoff.constraints[{index}].statement: invalid",
                )
                require(
                    isinstance(constraint.get("material"), bool),
                    errors,
                    f"review input.architecture_handoff.constraints[{index}].material: expected boolean",
                )
                if constraint.get("material") is True and isinstance(constraint.get("id"), str):
                    material_constraint_ids.add(constraint["id"])

    requirement_ids = validate_ids(
        value.get("requirements"),
        ID_PATTERNS["requirement"],
        errors,
        "review input.requirements",
    )
    requirement_source_refs: set[str] = set()

    if isinstance(value.get("requirements"), list):
        for index, requirement in enumerate(value["requirements"]):
            if not is_record(requirement):
                continue
            require(
                is_nonempty_string(requirement.get("statement")),
                errors,
                f"review input.requirements[{index}].statement: invalid",
            )
            refs = requirement.get("source_refs")
            require(
                is_string_list(refs),
                errors,
                f"review input.requirements[{index}].source_refs: expected string array",
            )
            if is_string_list(refs):
                requirement_source_refs.update(refs)

    implementation = value.get("implementation_snapshot")
    implementation_fingerprint: str | None = None
    work_product_ids: set[str] = set()
    affected_refs: set[str] = set()
    required_verification: set[str] = set()
    verified_verification: set[str] = set()

    evidence_ids, evidence_source_refs = validate_evidence_catalog(
        value.get("evidence_catalog"),
        errors,
        "review input.evidence_catalog",
    )

    if not is_record(implementation):
        errors.append("review input.implementation_snapshot: expected object")
    else:
        implementation_fingerprint = implementation.get("fingerprint")
        require(
            isinstance(implementation_fingerprint, str)
            and FINGERPRINT.fullmatch(implementation_fingerprint) is not None,
            errors,
            "review input.implementation_snapshot.fingerprint: invalid",
        )
        require(
            implementation.get("status") in {
                "WORK_PRODUCT_READY",
                "NEEDS_CLARIFICATION",
                "BLOCKED",
            },
            errors,
            "review input.implementation_snapshot.status: invalid",
        )

        existing_refs = implementation.get("existing_object_refs")
        proposed_refs = implementation.get("proposed_object_refs")
        require(
            is_string_list(existing_refs),
            errors,
            "review input.implementation_snapshot.existing_object_refs: expected string array",
        )
        require(
            is_string_list(proposed_refs),
            errors,
            "review input.implementation_snapshot.proposed_object_refs: expected string array",
        )
        if is_string_list(existing_refs):
            affected_refs.update(existing_refs)
        if is_string_list(proposed_refs):
            affected_refs.update(proposed_refs)

        work_product_ids = validate_ids(
            implementation.get("work_products"),
            ID_PATTERNS["work_product"],
            errors,
            "review input.implementation_snapshot.work_products",
        )
        affected_refs.update(work_product_ids)

        verification_items = implementation.get("required_verification")
        require(
            is_string_list(verification_items),
            errors,
            "review input.implementation_snapshot.required_verification: expected string array",
        )
        if is_string_list(verification_items):
            required_verification.update(verification_items)

        verification_claims = implementation.get("verification_claims")
        require(
            isinstance(verification_claims, list),
            errors,
            "review input.implementation_snapshot.verification_claims: expected array",
        )
        if isinstance(verification_claims, list):
            for index, claim in enumerate(verification_claims):
                if not is_record(claim):
                    errors.append(
                        f"review input.implementation_snapshot.verification_claims[{index}]: expected object"
                    )
                    continue
                claim_type = claim.get("type")
                require(
                    claim.get("status") in {"PASS", "FAIL"},
                    errors,
                    f"review input.implementation_snapshot.verification_claims[{index}].status: invalid",
                )
                refs = claim.get("evidence_refs")
                require(
                    is_string_list(refs) and bool(refs),
                    errors,
                    f"review input.implementation_snapshot.verification_claims[{index}].evidence_refs: required",
                )
                if is_string_list(refs):
                    for ref in refs:
                        require(
                            ref in evidence_ids,
                            errors,
                            f"review input.implementation_snapshot.verification_claims[{index}]: unknown evidence {ref}",
                        )
                if (
                    isinstance(claim_type, str)
                    and claim.get("status") == "PASS"
                    and is_string_list(refs)
                    and bool(refs)
                ):
                    verified_verification.add(claim_type)

    review_rule_ids = validate_ids(
        value.get("review_rules"),
        ID_PATTERNS["review_rule"],
        errors,
        "review input.review_rules",
    )
    review_rule_source_refs: set[str] = set()

    if isinstance(value.get("review_rules"), list):
        for index, rule in enumerate(value["review_rules"]):
            if not is_record(rule):
                continue
            require(
                is_nonempty_string(rule.get("statement")),
                errors,
                f"review input.review_rules[{index}].statement: invalid",
            )
            refs = rule.get("source_refs")
            require(
                is_string_list(refs),
                errors,
                f"review input.review_rules[{index}].source_refs: expected string array",
            )
            if is_string_list(refs):
                review_rule_source_refs.update(refs)

    validate_capabilities(
        value.get("capability_boundary"),
        errors,
        "review input.capability_boundary",
    )
    errors.extend(secret_errors(value))

    if not errors:
        metadata = {
            "input_fingerprint": fingerprint(value),
            "configuration_fingerprint": value["resolved_configuration_fingerprint"],
            "architecture_fingerprint": architecture_fingerprint,
            "implementation_fingerprint": implementation_fingerprint,
            "constraint_ids": constraint_ids,
            "material_constraint_ids": material_constraint_ids,
            "requirement_ids": requirement_ids,
            "work_product_ids": work_product_ids,
            "affected_refs": affected_refs,
            "evidence_ids": evidence_ids,
            "source_refs": (
                requirement_source_refs
                | evidence_source_refs
                | review_rule_source_refs
            ),
            "required_verification": required_verification,
            "verified_verification": verified_verification,
            "review_rule_ids": review_rule_ids,
        }

    return errors, metadata


def validate_review_result(
    result: Any,
    case: dict[str, Any],
    metadata: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not is_record(result):
        return ["review result: expected object"]

    require(
        result.get("contract_version") == REVIEW_RESULT_VERSION,
        errors,
        "review result.contract_version: unsupported",
    )
    require(
        result.get("task_id") == case.get("id"),
        errors,
        "review result.task_id: case mismatch",
    )

    provenance = result.get("provenance")
    if not is_record(provenance):
        errors.append("review result.provenance: expected object")
    else:
        require(
            provenance.get("input_fingerprint") == metadata["input_fingerprint"],
            errors,
            "review result.provenance.input_fingerprint: mismatch",
        )
        require(
            provenance.get("configuration_fingerprint") == metadata["configuration_fingerprint"],
            errors,
            "review result.provenance.configuration_fingerprint: mismatch",
        )
        require(
            provenance.get("architecture_handoff_fingerprint") == metadata["architecture_fingerprint"],
            errors,
            "review result.provenance.architecture_handoff_fingerprint: mismatch",
        )
        require(
            provenance.get("implementation_fingerprint") == metadata["implementation_fingerprint"],
            errors,
            "review result.provenance.implementation_fingerprint: mismatch",
        )

    outcome = result.get("outcome")
    require(outcome in REVIEW_OUTCOMES, errors, "review result.outcome: invalid")

    alignment = result.get("architecture_alignment")
    represented_constraints: set[str] = set()
    architecture_violated = False

    if not is_record(alignment):
        errors.append("review result.architecture_alignment: expected object")
    else:
        alignment_status = alignment.get("status")
        require(
            alignment_status in ALIGNMENT_STATUSES,
            errors,
            "review result.architecture_alignment.status: invalid",
        )
        architecture_violated = alignment_status != "PRESERVED"

        items = alignment.get("constraint_results")
        require(
            isinstance(items, list),
            errors,
            "review result.architecture_alignment.constraint_results: expected array",
        )
        if isinstance(items, list):
            for index, item in enumerate(items):
                if not is_record(item):
                    errors.append(
                        f"review result.architecture_alignment.constraint_results[{index}]: expected object"
                    )
                    continue
                ref = item.get("constraint_ref")
                require(
                    ref in metadata["constraint_ids"],
                    errors,
                    f"review result.architecture_alignment.constraint_results[{index}]: unknown {ref}",
                )
                if isinstance(ref, str):
                    require(
                        ref not in represented_constraints,
                        errors,
                        f"review result.architecture_alignment.constraint_results[{index}]: duplicate {ref}",
                    )
                    represented_constraints.add(ref)

                status = item.get("status")
                require(
                    status in ALIGNMENT_STATUSES,
                    errors,
                    f"review result.architecture_alignment.constraint_results[{index}].status: invalid",
                )
                if status != "PRESERVED":
                    architecture_violated = True

    finding_ids = validate_ids(
        result.get("findings"),
        ID_PATTERNS["finding"],
        errors,
        "review result.findings",
    )
    blocking_findings = 0
    finding_constraint_refs: set[str] = set()
    finding_affected_refs: set[str] = set()

    if isinstance(result.get("findings"), list):
        for index, finding in enumerate(result["findings"]):
            if not is_record(finding):
                continue

            require(
                finding.get("severity") in {"CRITICAL", "MAJOR", "MINOR", "INFO"},
                errors,
                f"review result.findings[{index}].severity: invalid",
            )
            require(
                is_nonempty_string(finding.get("statement")),
                errors,
                f"review result.findings[{index}].statement: invalid",
            )
            require(
                is_nonempty_string(finding.get("required_action")),
                errors,
                f"review result.findings[{index}].required_action: invalid",
            )

            affected = finding.get("affected_refs")
            require(
                is_string_list(affected),
                errors,
                f"review result.findings[{index}].affected_refs: expected string array",
            )
            if is_string_list(affected):
                for ref in affected:
                    require(
                        ref in metadata["affected_refs"],
                        errors,
                        f"review result.findings[{index}].affected_refs: unknown {ref}",
                    )
                    finding_affected_refs.add(ref)

            constraint_refs = finding.get("constraint_refs")
            require(
                is_string_list(constraint_refs),
                errors,
                f"review result.findings[{index}].constraint_refs: expected string array",
            )
            if is_string_list(constraint_refs):
                for ref in constraint_refs:
                    require(
                        ref in metadata["constraint_ids"],
                        errors,
                        f"review result.findings[{index}].constraint_refs: unknown {ref}",
                    )
                    finding_constraint_refs.add(ref)

            requirement_refs = finding.get("requirement_refs")
            require(
                is_string_list(requirement_refs),
                errors,
                f"review result.findings[{index}].requirement_refs: expected string array",
            )
            if is_string_list(requirement_refs):
                for ref in requirement_refs:
                    require(
                        ref in metadata["requirement_ids"],
                        errors,
                        f"review result.findings[{index}].requirement_refs: unknown {ref}",
                    )

            evidence_refs = finding.get("evidence_refs")
            require(
                is_string_list(evidence_refs),
                errors,
                f"review result.findings[{index}].evidence_refs: expected string array",
            )
            if is_string_list(evidence_refs):
                for ref in evidence_refs:
                    require(
                        ref in metadata["evidence_ids"],
                        errors,
                        f"review result.findings[{index}].evidence_refs: unknown {ref}",
                    )

            source_refs = finding.get("source_refs")
            require(
                is_string_list(source_refs),
                errors,
                f"review result.findings[{index}].source_refs: expected string array",
            )
            if is_string_list(source_refs):
                for ref in source_refs:
                    require(
                        ref in metadata["source_refs"],
                        errors,
                        f"review result.findings[{index}].source_refs: unknown {ref}",
                    )

            require(
                isinstance(finding.get("blocks_acceptance"), bool),
                errors,
                f"review result.findings[{index}].blocks_acceptance: expected boolean",
            )
            if finding.get("blocks_acceptance") is True:
                blocking_findings += 1

    unknown_ids = validate_ids(
        result.get("unknowns"),
        ID_PATTERNS["unknown"],
        errors,
        "review result.unknowns",
    )
    blocking_unknown = False

    if isinstance(result.get("unknowns"), list):
        for index, unknown in enumerate(result["unknowns"]):
            if not is_record(unknown):
                continue
            require(
                is_nonempty_string(unknown.get("statement")),
                errors,
                f"review result.unknowns[{index}].statement: invalid",
            )
            if unknown.get("material") is True and unknown.get("blocks_review") is True:
                blocking_unknown = True

    debt_types: set[str] = set()
    debt = result.get("verification_debt")
    require(
        isinstance(debt, list),
        errors,
        "review result.verification_debt: expected array",
    )
    if isinstance(debt, list):
        for index, item in enumerate(debt):
            if not is_record(item):
                errors.append(f"review result.verification_debt[{index}]: expected object")
                continue
            verification_type = item.get("type")
            if isinstance(verification_type, str):
                debt_types.add(verification_type)

            status = item.get("status")
            require(
                status in {"PENDING", "EVIDENCE_PRESENT"},
                errors,
                f"review result.verification_debt[{index}].status: invalid",
            )
            refs = item.get("evidence_refs")
            require(
                is_string_list(refs),
                errors,
                f"review result.verification_debt[{index}].evidence_refs: expected string array",
            )
            if is_string_list(refs):
                for ref in refs:
                    require(
                        ref in metadata["evidence_ids"],
                        errors,
                        f"review result.verification_debt[{index}].evidence_refs: unknown {ref}",
                    )
                if status == "EVIDENCE_PRESENT":
                    require(
                        bool(refs),
                        errors,
                        f"review result.verification_debt[{index}]: EVIDENCE_PRESENT requires evidence",
                    )

    unresolved_debt = metadata["required_verification"] - metadata["verified_verification"]
    require(
        unresolved_debt <= debt_types,
        errors,
        f"review result.verification_debt: missing outstanding items {sorted(unresolved_debt - debt_types)}",
    )

    if outcome == "REVIEW_ACCEPTABLE":
        require(
            not architecture_violated,
            errors,
            "review result.outcome: REVIEW_ACCEPTABLE with architecture violation/unknown",
        )
        require(
            metadata["material_constraint_ids"] <= represented_constraints,
            errors,
            "review result.architecture_alignment: missing material constraints",
        )
        require(
            blocking_findings == 0,
            errors,
            "review result.outcome: REVIEW_ACCEPTABLE with blocking finding",
        )
        require(
            not blocking_unknown,
            errors,
            "review result.outcome: REVIEW_ACCEPTABLE with blocking unknown",
        )

    handoff = result.get("review_handoff")
    if not is_record(handoff):
        errors.append("review result.review_handoff: expected object")
    else:
        proceed = handoff.get("proceed_to_verification")
        require(
            isinstance(proceed, bool),
            errors,
            "review result.review_handoff.proceed_to_verification: expected boolean",
        )
        if outcome == "REVIEW_ACCEPTABLE":
            require(
                proceed is True,
                errors,
                "review result.review_handoff: acceptable review must proceed to verification",
            )
        else:
            require(
                proceed is False,
                errors,
                "review result.review_handoff: non-acceptable review cannot proceed to verification",
            )

    validate_capabilities(
        [item.get("verb") for item in result.get("requested_capabilities", []) if is_record(item)]
        if isinstance(result.get("requested_capabilities"), list)
        else result.get("requested_capabilities"),
        errors,
        "review result.requested_capabilities",
    )

    next_action = result.get("next_action")
    if is_record(next_action) and outcome != "REVIEW_ACCEPTABLE":
        require(
            next_action.get("type") != "HANDOFF_VERIFICATION",
            errors,
            "review result.next_action: non-acceptable review cannot HANDOFF_VERIFICATION",
        )

    assertions = case.get("output_assertions")
    if is_record(assertions):
        allowed = assertions.get("allowed_outcome")
        if isinstance(allowed, list):
            require(outcome in allowed, errors, f"case: review outcome {outcome} not allowed")

        expected_alignment = assertions.get("architecture_alignment")
        if expected_alignment is not None and is_record(alignment):
            require(
                alignment.get("status") == expected_alignment,
                errors,
                "case: review architecture alignment mismatch",
            )

        max_blocking = assertions.get("max_blocking_findings")
        min_blocking = assertions.get("min_blocking_findings")
        if isinstance(max_blocking, int):
            require(
                blocking_findings <= max_blocking,
                errors,
                f"case: maximum blocking findings is {max_blocking}",
            )
        if isinstance(min_blocking, int):
            require(
                blocking_findings >= min_blocking,
                errors,
                f"case: minimum blocking findings is {min_blocking}",
            )

        for ref in assertions.get("required_constraint_refs", []):
            require(ref in finding_constraint_refs, errors, f"case: required finding constraint ref missing {ref}")
        for ref in assertions.get("required_work_product_refs", []):
            require(ref in finding_affected_refs, errors, f"case: required affected work-product ref missing {ref}")

        if assertions.get("must_preserve_verification_debt") is True:
            require(
                unresolved_debt <= debt_types,
                errors,
                "case: verification debt was not preserved",
            )

        expected_proceed = assertions.get("proceed_to_verification")
        if isinstance(expected_proceed, bool) and is_record(handoff):
            require(
                handoff.get("proceed_to_verification") is expected_proceed,
                errors,
                "case: proceed_to_verification mismatch",
            )

    _ = finding_ids, unknown_ids
    return errors


def validate_test_input(value: Any) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    metadata: dict[str, Any] = {}

    if not is_record(value):
        return ["test input: expected object"], metadata

    require(
        value.get("contract_version") == TEST_INPUT_VERSION,
        errors,
        "test input.contract_version: unsupported",
    )
    require(
        value.get("requested_result_contract") == TEST_RESULT_VERSION,
        errors,
        "test input.requested_result_contract: unsupported",
    )
    require(
        isinstance(value.get("resolved_configuration_fingerprint"), str)
        and FINGERPRINT.fullmatch(value["resolved_configuration_fingerprint"]) is not None,
        errors,
        "test input.resolved_configuration_fingerprint: invalid",
    )

    task = value.get("task")
    if not is_record(task):
        errors.append("test input.task: expected object")
    else:
        require(is_nonempty_string(task.get("id")), errors, "test input.task.id: invalid")
        require(
            task.get("requested_outcome") == "VERIFICATION_PLAN",
            errors,
            "test input.task.requested_outcome: unsupported",
        )

    requirement_ids = validate_ids(
        value.get("requirements"),
        ID_PATTERNS["requirement"],
        errors,
        "test input.requirements",
    )
    critical_requirements: set[str] = set()
    if isinstance(value.get("requirements"), list):
        for requirement in value["requirements"]:
            if is_record(requirement) and requirement.get("critical") is True and isinstance(requirement.get("id"), str):
                critical_requirements.add(requirement["id"])

    constraint_ids = validate_ids(
        value.get("architecture_constraints"),
        ID_PATTERNS["constraint"],
        errors,
        "test input.architecture_constraints",
    )
    material_constraints: set[str] = set()
    if isinstance(value.get("architecture_constraints"), list):
        for constraint in value["architecture_constraints"]:
            if is_record(constraint) and constraint.get("material") is True and isinstance(constraint.get("id"), str):
                material_constraints.add(constraint["id"])

    implementation = value.get("implementation_snapshot")
    implementation_fingerprint: str | None = None
    work_product_ids: set[str] = set()
    object_refs: set[str] = set()

    if not is_record(implementation):
        errors.append("test input.implementation_snapshot: expected object")
    else:
        implementation_fingerprint = implementation.get("fingerprint")
        require(
            isinstance(implementation_fingerprint, str)
            and FINGERPRINT.fullmatch(implementation_fingerprint) is not None,
            errors,
            "test input.implementation_snapshot.fingerprint: invalid",
        )
        refs = implementation.get("object_refs")
        require(
            is_string_list(refs),
            errors,
            "test input.implementation_snapshot.object_refs: expected string array",
        )
        if is_string_list(refs):
            object_refs.update(refs)

        work_product_ids = validate_ids(
            implementation.get("work_products"),
            ID_PATTERNS["work_product"],
            errors,
            "test input.implementation_snapshot.work_products",
        )

    finding_ids = validate_ids(
        value.get("review_findings"),
        ID_PATTERNS["finding"],
        errors,
        "test input.review_findings",
    )
    blocking_findings: set[str] = set()
    if isinstance(value.get("review_findings"), list):
        for finding in value["review_findings"]:
            if is_record(finding) and finding.get("blocks_verification") is True and isinstance(finding.get("id"), str):
                blocking_findings.add(finding["id"])

    risk_ids = validate_ids(
        value.get("risks"),
        ID_PATTERNS["risk"],
        errors,
        "test input.risks",
    )
    material_risks: set[str] = set()
    if isinstance(value.get("risks"), list):
        for risk in value["risks"]:
            if is_record(risk) and risk.get("material") is True and isinstance(risk.get("id"), str):
                material_risks.add(risk["id"])

    evidence_ids, _ = validate_evidence_catalog(
        value.get("evidence_catalog"),
        errors,
        "test input.evidence_catalog",
    )

    input_unknown_ids = validate_ids(
        value.get("unknowns"),
        ID_PATTERNS["input_unknown"],
        errors,
        "test input.unknowns",
    )
    blocking_unknowns: set[str] = set()
    if isinstance(value.get("unknowns"), list):
        for unknown in value["unknowns"]:
            if (
                is_record(unknown)
                and unknown.get("material") is True
                and unknown.get("blocks_plan") is True
                and isinstance(unknown.get("id"), str)
            ):
                blocking_unknowns.add(unknown["id"])

    validate_capabilities(
        value.get("capability_boundary"),
        errors,
        "test input.capability_boundary",
    )
    errors.extend(secret_errors(value))

    if not errors:
        metadata = {
            "input_fingerprint": fingerprint(value),
            "configuration_fingerprint": value["resolved_configuration_fingerprint"],
            "implementation_fingerprint": implementation_fingerprint,
            "requirement_ids": requirement_ids,
            "critical_requirements": critical_requirements,
            "constraint_ids": constraint_ids,
            "material_constraints": material_constraints,
            "work_product_ids": work_product_ids,
            "object_refs": object_refs,
            "finding_ids": finding_ids,
            "blocking_findings": blocking_findings,
            "risk_ids": risk_ids,
            "material_risks": material_risks,
            "evidence_ids": evidence_ids,
            "blocking_unknowns": blocking_unknowns,
        }

    _ = input_unknown_ids
    return errors, metadata


def validate_test_result(
    result: Any,
    case: dict[str, Any],
    metadata: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not is_record(result):
        return ["test result: expected object"]

    require(
        result.get("contract_version") == TEST_RESULT_VERSION,
        errors,
        "test result.contract_version: unsupported",
    )
    require(
        result.get("task_id") == case.get("id"),
        errors,
        "test result.task_id: case mismatch",
    )

    provenance = result.get("provenance")
    if not is_record(provenance):
        errors.append("test result.provenance: expected object")
    else:
        require(
            provenance.get("input_fingerprint") == metadata["input_fingerprint"],
            errors,
            "test result.provenance.input_fingerprint: mismatch",
        )
        require(
            provenance.get("configuration_fingerprint") == metadata["configuration_fingerprint"],
            errors,
            "test result.provenance.configuration_fingerprint: mismatch",
        )
        require(
            provenance.get("implementation_fingerprint") == metadata["implementation_fingerprint"],
            errors,
            "test result.provenance.implementation_fingerprint: mismatch",
        )

    status = result.get("status")
    require(status in TEST_STATUSES, errors, "test result.status: invalid")

    check_ids = validate_ids(
        result.get("planned_checks"),
        ID_PATTERNS["check"],
        errors,
        "test result.planned_checks",
    )
    known_trace_refs = (
        metadata["requirement_ids"]
        | metadata["constraint_ids"]
        | metadata["work_product_ids"]
        | metadata["object_refs"]
        | metadata["finding_ids"]
        | metadata["risk_ids"]
    )

    if isinstance(result.get("planned_checks"), list):
        for index, check in enumerate(result["planned_checks"]):
            if not is_record(check):
                continue
            require(
                is_nonempty_string(check.get("description")),
                errors,
                f"test result.planned_checks[{index}].description: invalid",
            )
            trace_refs = check.get("trace_refs")
            require(
                is_string_list(trace_refs) and bool(trace_refs),
                errors,
                f"test result.planned_checks[{index}].trace_refs: non-empty array required",
            )
            if is_string_list(trace_refs):
                for ref in trace_refs:
                    require(
                        ref in known_trace_refs,
                        errors,
                        f"test result.planned_checks[{index}].trace_refs: unknown {ref}",
                    )
            require(
                is_nonempty_string(check.get("expected_result")),
                errors,
                f"test result.planned_checks[{index}].expected_result: invalid",
            )
            require(
                is_nonempty_string(check.get("expected_evidence_type")),
                errors,
                f"test result.planned_checks[{index}].expected_evidence_type: invalid",
            )

    covered_requirements: set[str] = set()
    covered_constraints: set[str] = set()
    coverage = result.get("coverage")
    require(isinstance(coverage, list), errors, "test result.coverage: expected array")

    if isinstance(coverage, list):
        for index, item in enumerate(coverage):
            if not is_record(item):
                errors.append(f"test result.coverage[{index}]: expected object")
                continue

            source_type = item.get("source_type")
            source_ref = item.get("source_ref")
            valid_source = False

            if source_type == "REQUIREMENT":
                valid_source = source_ref in metadata["requirement_ids"]
                if valid_source and isinstance(source_ref, str):
                    covered_requirements.add(source_ref)
            elif source_type == "CONSTRAINT":
                valid_source = source_ref in metadata["constraint_ids"]
                if valid_source and isinstance(source_ref, str):
                    covered_constraints.add(source_ref)
            elif source_type == "REVIEW_FINDING":
                valid_source = source_ref in metadata["finding_ids"]
            elif source_type == "RISK":
                valid_source = source_ref in metadata["risk_ids"]

            require(
                valid_source,
                errors,
                f"test result.coverage[{index}]: invalid source reference {source_ref}",
            )

            excluded = item.get("excluded")
            require(
                isinstance(excluded, bool),
                errors,
                f"test result.coverage[{index}].excluded: expected boolean",
            )

            check_refs = item.get("check_refs")
            require(
                is_string_list(check_refs),
                errors,
                f"test result.coverage[{index}].check_refs: expected string array",
            )

            if is_string_list(check_refs):
                for ref in check_refs:
                    require(
                        ref in check_ids,
                        errors,
                        f"test result.coverage[{index}].check_refs: unknown {ref}",
                    )

            if excluded is True:
                require(
                    is_nonempty_string(item.get("exclusion_justification")),
                    errors,
                    f"test result.coverage[{index}]: excluded item requires justification",
                )
            else:
                require(
                    is_string_list(check_refs) and bool(check_refs),
                    errors,
                    f"test result.coverage[{index}]: non-excluded coverage requires checks",
                )

    for requirement in metadata["critical_requirements"]:
        entries = [
            item
            for item in coverage
            if is_record(item)
            and item.get("source_type") == "REQUIREMENT"
            and item.get("source_ref") == requirement
        ] if isinstance(coverage, list) else []

        require(
            bool(entries),
            errors,
            f"test result.coverage: critical requirement {requirement} missing",
        )
        if entries:
            valid_entry = any(
                (
                    item.get("excluded") is False
                    and is_string_list(item.get("check_refs"))
                    and bool(item["check_refs"])
                )
                or (
                    item.get("excluded") is True
                    and is_nonempty_string(item.get("exclusion_justification"))
                )
                for item in entries
            )
            require(
                valid_entry,
                errors,
                f"test result.coverage: critical requirement {requirement} lacks checks/justification",
            )

    result_unknown_ids = validate_ids(
        result.get("unknowns"),
        ID_PATTERNS["unknown"],
        errors,
        "test result.unknowns",
    )
    blocking_result_unknown = False

    if isinstance(result.get("unknowns"), list):
        for unknown in result["unknowns"]:
            if (
                is_record(unknown)
                and unknown.get("material") is True
                and unknown.get("blocks_plan") is True
            ):
                blocking_result_unknown = True

    if status == "TEST_PLAN_READY":
        require(
            not metadata["blocking_unknowns"],
            errors,
            "test result.status: TEST_PLAN_READY while input has blocking unknowns",
        )
        require(
            not blocking_result_unknown,
            errors,
            "test result.status: TEST_PLAN_READY with blocking result unknown",
        )

    claims = result.get("verification_claims")
    require(
        isinstance(claims, list),
        errors,
        "test result.verification_claims: expected array",
    )
    claim_count = 0
    if isinstance(claims, list):
        claim_count = len(claims)
        for index, claim in enumerate(claims):
            if not is_record(claim):
                errors.append(f"test result.verification_claims[{index}]: expected object")
                continue
            require(
                claim.get("status") in {"PASS", "FAIL"},
                errors,
                f"test result.verification_claims[{index}].status: invalid",
            )
            refs = claim.get("evidence_refs")
            require(
                is_string_list(refs) and bool(refs),
                errors,
                f"test result.verification_claims[{index}].evidence_refs: evidence required",
            )
            if is_string_list(refs):
                for ref in refs:
                    require(
                        ref in metadata["evidence_ids"],
                        errors,
                        f"test result.verification_claims[{index}].evidence_refs: unknown {ref}",
                    )

    handoff = result.get("execution_handoff")
    if not is_record(handoff):
        errors.append("test result.execution_handoff: expected object")
    else:
        ready = handoff.get("ready_for_execution")
        require(
            isinstance(ready, bool),
            errors,
            "test result.execution_handoff.ready_for_execution: expected boolean",
        )
        if status == "TEST_PLAN_READY":
            require(
                ready is True,
                errors,
                "test result.execution_handoff: ready plan must be ready for execution",
            )
        else:
            require(
                ready is False,
                errors,
                "test result.execution_handoff: non-ready plan cannot be ready for execution",
            )

    validate_capabilities(
        [item.get("verb") for item in result.get("requested_capabilities", []) if is_record(item)]
        if isinstance(result.get("requested_capabilities"), list)
        else result.get("requested_capabilities"),
        errors,
        "test result.requested_capabilities",
    )

    next_action = result.get("next_action")
    if is_record(next_action) and status != "TEST_PLAN_READY":
        require(
            next_action.get("type") != "HANDOFF_VERIFICATION_EXECUTION",
            errors,
            "test result.next_action: non-ready result cannot HANDOFF_VERIFICATION_EXECUTION",
        )

    assertions = case.get("output_assertions")
    if is_record(assertions):
        allowed = assertions.get("allowed_status")
        if isinstance(allowed, list):
            require(status in allowed, errors, f"case: test status {status} not allowed")

        for ref in assertions.get("required_requirement_refs", []):
            require(
                ref in covered_requirements,
                errors,
                f"case: required requirement coverage missing {ref}",
            )
        for ref in assertions.get("required_constraint_refs", []):
            require(
                ref in covered_constraints,
                errors,
                f"case: required constraint coverage missing {ref}",
            )

        min_checks = assertions.get("min_planned_checks")
        if isinstance(min_checks, int):
            require(
                len(check_ids) >= min_checks,
                errors,
                f"case: requires at least {min_checks} planned checks",
            )

        expected_claims = assertions.get("executed_verification_claims")
        if isinstance(expected_claims, int):
            require(
                claim_count == expected_claims,
                errors,
                f"case: expected {expected_claims} verification claims, got {claim_count}",
            )

        expected_ready = assertions.get("ready_for_execution")
        if isinstance(expected_ready, bool) and is_record(handoff):
            require(
                handoff.get("ready_for_execution") is expected_ready,
                errors,
                "case: ready_for_execution mismatch",
            )

    _ = result_unknown_ids
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True, help="M3 case JSON")
    parser.add_argument("--result", type=Path, help="optional result JSON")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        case = json.loads(args.case.read_text(encoding="utf-8"))
        if not is_record(case):
            raise ValueError("case root must be object")

        agent = case.get("agent")
        case_input = case.get("input")
        result_errors: list[str] = []

        if agent == "SAP_REVIEWER":
            input_errors, metadata = validate_review_input(case_input)
            if args.result and not input_errors:
                result = json.loads(args.result.read_text(encoding="utf-8"))
                result_errors = validate_review_result(result, case, metadata)
        elif agent == "SAP_TEST_ENGINEER":
            input_errors, metadata = validate_test_input(case_input)
            if args.result and not input_errors:
                result = json.loads(args.result.read_text(encoding="utf-8"))
                result_errors = validate_test_result(result, case, metadata)
        else:
            raise ValueError(f"unsupported agent: {agent}")

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"M3 CONTRACT VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2

    errors = input_errors + result_errors
    report = {
        "case": str(args.case),
        "result": str(args.result) if args.result else None,
        "agent": case.get("agent"),
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
