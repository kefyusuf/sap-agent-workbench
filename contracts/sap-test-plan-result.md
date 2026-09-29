# SAP Test Engineer Result Contract

## Contract identity

`m3.sap-test-plan-result.v1`

## Top-level fields

- `contract_version`
- `task_id`
- `provenance`
- `status`
- `coverage`
- `planned_checks`
- `unknowns`
- `verification_claims`
- `execution_handoff`
- `requested_capabilities`
- `next_action`

## Provenance

Runtime-owned:

- `input_fingerprint`
- `configuration_fingerprint`
- `implementation_fingerprint`

## Status

Allowed:

- `TEST_PLAN_READY`
- `NEEDS_CLARIFICATION`
- `BLOCKED`

TEST_PLAN_READY means a defensible plan exists; no check is implied executed.

## Coverage

Coverage entries map a source reference to one or more planned checks.

Each entry contains:

- `source_type`: REQUIREMENT | CONSTRAINT | REVIEW_FINDING | RISK
- `source_ref`
- `check_refs`
- `excluded`
- `exclusion_justification`

Rules:

- critical requirements must have check_refs unless excluded with non-empty justification
- case-defined material constraints/findings/risks may require coverage
- check refs must resolve to planned_checks

## Planned checks

Each check contains:

- `id`
- `type`
- `description`
- `trace_refs`
- `preconditions`
- `expected_result`
- `expected_evidence_type`
- `blocking_for_delivery`

Initial types:

- COMPILE
- ATC
- UNIT_TEST
- INTEGRATION_TEST
- AUTHORIZATION
- PERFORMANCE
- PAYLOAD_CONTRACT
- NEGATIVE_CASE
- BOUNDARY_CASE
- TRANSACTIONAL
- RUNTIME
- REGRESSION
- OTHER

A planned check is not an executed check.

## Unknowns

Each unknown:

- `id`
- `statement`
- `material`
- `blocks_plan`
- `verification`

A blocking unknown prevents TEST_PLAN_READY.

## Verification claims

Existing evidence-backed claims may be represented:

- `type`
- `status`: PASS | FAIL
- `evidence_refs`

No evidence → no PASS/FAIL claim.

Evidence must also be compatible with the claimed verification type under ADR-024:

- COMPILE → EXECUTION_RESULT or STATIC_ANALYSIS
- ATC → STATIC_ANALYSIS
- UNIT_TEST → TEST_RESULT
- INTEGRATION_TEST → TEST_RESULT
- AUTHORIZATION → TEST_RESULT or CONFIGURATION
- PERFORMANCE → TEST_RESULT or EXECUTION_RESULT
- PAYLOAD_CONTRACT → TEST_RESULT or EXECUTION_RESULT
- RUNTIME → EXECUTION_RESULT or LOG
- REGRESSION → TEST_RESULT

`OTHER` PASS/FAIL is not accepted in M3 v1 without a later explicit compatibility decision.

Planning itself never creates evidence.

## Execution handoff

Contains:

- `ready_for_execution`
- `notes`

TEST_PLAN_READY requires ready_for_execution = true.

This does not grant execution permission.

## Capabilities

Only READ / QUERY / ANALYZE / PROPOSE.

## Next action

Initial values:

- `HANDOFF_VERIFICATION_EXECUTION`
- `REQUEST_CLARIFICATION`
- `VERIFY_CONTEXT`
- `RETURN_TO_IMPLEMENTATION`
- `NONE`

Non-ready results cannot request HANDOFF_VERIFICATION_EXECUTION.
