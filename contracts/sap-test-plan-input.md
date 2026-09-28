# SAP Test Engineer Input Contract

## Contract identity

`m3.sap-test-plan-input.v1`

This contract defines the provider-independent snapshot used to design verification coverage.

## Top-level fields

- `contract_version`
- `task`
- `scope`
- `requirements`
- `architecture_constraints`
- `implementation_snapshot`
- `review_findings`
- `risks`
- `evidence_catalog`
- `unknowns`
- `capability_boundary`
- `resolved_configuration_fingerprint`
- `requested_result_contract`

## Task

Initial requested outcome:

`VERIFICATION_PLAN`

## Requirements

Each requirement:

- `id`
- `statement`
- `critical`

Critical requirements require coverage or an explicit justified exclusion.

## Architecture constraints

Each constraint:

- `id`
- `statement`
- `material`

Material constraints may require verification coverage.

## Implementation snapshot

Contains:

- `id`
- `fingerprint`
- object/work-product references
- outstanding verification debt

This allows test planning to stay revision-bound.

## Reviewer findings

Each finding supplied to test planning contains:

- `id`
- `severity`
- `statement`
- `testable`
- `blocks_verification`

A review-blocking finding may prevent TEST_PLAN_READY when implementation is not yet testable.

## Risks

Each risk:

- `id`
- `category`
- `description`
- `material`

Material risks should map to checks where testable.

## Unknowns

Each unknown:

- `id`
- `statement`
- `material`
- `blocks_plan`
- `verification`

Material blocking unknowns prevent TEST_PLAN_READY.

## Evidence catalog

Existing evidence may be consumed, but M3 planning cannot create executed evidence.

## Capability boundary

Initial Test Engineer capabilities:

- READ
- QUERY
- ANALYZE
- PROPOSE

No test execution or SAP mutation capability is introduced.

## Fingerprinting

The result binds to:

- canonical input fingerprint
- configuration fingerprint
- implementation snapshot fingerprint

## Result contract

`m3.sap-test-plan-result.v1`
