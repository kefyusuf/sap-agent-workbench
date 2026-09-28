# SAP Reviewer Result Contract

## Contract identity

`m3.sap-review-result.v1`

## Top-level fields

- `contract_version`
- `task_id`
- `provenance`
- `outcome`
- `architecture_alignment`
- `findings`
- `unknowns`
- `verification_debt`
- `review_handoff`
- `requested_capabilities`
- `next_action`

## Provenance

Runtime-owned:

- `input_fingerprint`
- `configuration_fingerprint`
- `architecture_handoff_fingerprint`
- `implementation_fingerprint`

## Outcome

Allowed:

- `REVIEW_ACCEPTABLE`
- `CHANGES_REQUIRED`
- `BLOCKED`

Rules:

- REVIEW_ACCEPTABLE requires architecture alignment PRESERVED
- REVIEW_ACCEPTABLE allows verification debt to remain outstanding
- REVIEW_ACCEPTABLE forbids unresolved review-blocking findings
- BLOCKED represents insufficient review context, not implementation rejection

## Architecture alignment

Contains:

- `status`: PRESERVED | VIOLATED | UNKNOWN
- `constraint_results`

Each constraint result:

- `constraint_ref`
- `status`: PRESERVED | VIOLATED | UNKNOWN
- `notes`

Every material input architecture constraint must be represented before REVIEW_ACCEPTABLE.

## Findings

Each finding contains:

- `id`
- `severity`: CRITICAL | MAJOR | MINOR | INFO
- `category`
- `statement`
- `affected_refs`
- `constraint_refs`
- `requirement_refs`
- `evidence_refs`
- `source_refs`
- `required_action`
- `blocks_acceptance`

All references must resolve to the review input snapshot.

A blocking finding prevents REVIEW_ACCEPTABLE.

## Unknowns

Each unknown contains:

- `id`
- `statement`
- `material`
- `blocks_review`
- `verification`

A material blocking unknown prevents REVIEW_ACCEPTABLE.

## Verification debt

The Reviewer preserves outstanding verification items rather than pretending they passed.

Each item contains:

- `type`
- `status`: PENDING | EVIDENCE_PRESENT
- `evidence_refs`

EVIDENCE_PRESENT requires evidence from the review input catalog **and** that evidence must be compatible with the verification type under ADR-024.

For M3 v1:

- COMPILE → EXECUTION_RESULT or STATIC_ANALYSIS
- ATC → STATIC_ANALYSIS
- UNIT_TEST → TEST_RESULT
- INTEGRATION_TEST → TEST_RESULT
- AUTHORIZATION → TEST_RESULT or CONFIGURATION
- PERFORMANCE → TEST_RESULT or EXECUTION_RESULT
- PAYLOAD_CONTRACT → TEST_RESULT or EXECUTION_RESULT
- RUNTIME → EXECUTION_RESULT or LOG
- REGRESSION → TEST_RESULT

`PENDING` debt carries no evidence-backed success/failure state.
`OTHER` cannot be marked EVIDENCE_PRESENT until a later compatibility decision defines acceptable evidence.

## Review handoff

Contains:

- `proceed_to_verification`
- `notes`

Rules:

- REVIEW_ACCEPTABLE → proceed_to_verification = true
- CHANGES_REQUIRED / BLOCKED → false

Proceeding to verification is not delivery readiness.

## Capabilities

Only READ / QUERY / ANALYZE / PROPOSE.

## Next action

Initial values:

- `HANDOFF_VERIFICATION`
- `RETURN_TO_IMPLEMENTATION`
- `RETURN_TO_ARCHITECTURE`
- `REQUEST_REVIEW_CONTEXT`
- `NONE`

Non-acceptable outcomes cannot request HANDOFF_VERIFICATION.
