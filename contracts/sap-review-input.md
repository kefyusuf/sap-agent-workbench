# SAP Reviewer Input Contract

## Contract identity

`m3.sap-review-input.v1`

This contract defines the provider-independent review snapshot consumed by the M3 SAP Reviewer Agent.

## Top-level fields

- `contract_version`
- `task`
- `scope`
- `architecture_handoff`
- `requirements`
- `implementation_snapshot`
- `evidence_catalog`
- `review_rules`
- `capability_boundary`
- `resolved_configuration_fingerprint`
- `requested_result_contract`

## Task

`task` contains:

- `id`
- `review_objective`
- `requested_outcome`

Initial requested outcome:

`IMPLEMENTATION_REVIEW`

## Architecture handoff

The Reviewer receives the upstream architecture contract as immutable review context.

Fields:

- `id`
- `fingerprint`
- `approach`
- `constraints`

Each constraint contains:

- `id`
- `statement`
- `material`

A material constraint cannot be waived by the Reviewer.

## Requirements

Each requirement contains:

- `id`
- `statement`
- `material`
- `source_refs`

Requirements allow findings to trace back to the scoped behavior.

## Implementation snapshot

The implementation snapshot is revision-bound input.

It contains:

- `id`
- `fingerprint`
- `status`
- `existing_object_refs`
- `proposed_object_refs`
- `work_products`
- `required_verification`
- `verification_claims`

Each work product contains:

- `id`
- `type`
- `summary`
- `content`

The snapshot is review input, not mutable state.

## Evidence catalog

Evidence entries reuse the M0 evidence vocabulary.

Any result evidence reference must resolve to this catalog.

The Reviewer cannot create evidence IDs.

Verification claims already present in the implementation snapshot must also use evidence compatible with the claimed verification type.
An unrelated approved document does not establish compile, ATC, test, runtime, or performance PASS/FAIL.

Initial compatibility follows ADR-024:

- COMPILE → EXECUTION_RESULT or STATIC_ANALYSIS
- ATC → STATIC_ANALYSIS
- UNIT_TEST → TEST_RESULT
- INTEGRATION_TEST → TEST_RESULT
- AUTHORIZATION → TEST_RESULT or CONFIGURATION
- PERFORMANCE → TEST_RESULT or EXECUTION_RESULT
- PAYLOAD_CONTRACT → TEST_RESULT or EXECUTION_RESULT
- RUNTIME → EXECUTION_RESULT or LOG
- REGRESSION → TEST_RESULT

`OTHER` remains a required/planned verification category only in M3 v1 unless a later compatibility decision defines acceptable executed evidence.

## Review rules

Organization/project review constraints may be supplied as explicit rules:

- `id`
- `category`
- `statement`
- `material`
- `source_refs`

Initial categories:

- `ARCHITECTURE`
- `CORRECTNESS`
- `PERFORMANCE`
- `SECURITY`
- `AUTHORIZATION`
- `TRANSACTIONALITY`
- `MAINTAINABILITY`
- `OBSERVABILITY`
- `VERIFICATION`
- `UPGRADE`
- `OTHER`

## Capability boundary

Initial Reviewer capabilities remain:

- READ
- QUERY
- ANALYZE
- PROPOSE

No WRITE / DEPLOY / TRANSPORT / ADMIN.

## Fingerprinting

The orchestration layer computes the input fingerprint from canonical UTF-8 JSON of the entire validated input envelope.

The result also binds to:

- architecture handoff fingerprint
- implementation snapshot fingerprint
- resolved configuration fingerprint

## Result contract

M3 Reviewer v1 requests:

`m3.sap-review-result.v1`

## Secret boundary

Raw credentials/secrets are forbidden.
