# SAP Technical Architect Result Contract

## Contract identity

`m1.technical-architect-result.v1`

This contract defines the machine-readable result produced by the M1 SAP Technical Architect Agent.

It is provider-independent and does not define prompt wording.

## Top-level fields

A result contains:

- `contract_version`
- `task_id`
- `status`
- `requirement_summary`
- `scope`
- `claims`
- `unknowns`
- `conflicts`
- `existing_solution_discovery`
- `solution_options`
- `proposal`
- `required_verification`
- `implementation_handoff`
- `requested_capabilities`
- `next_action`

## Status

Allowed values:

- `COMPLETED`
- `NEEDS_CLARIFICATION`
- `BLOCKED`

### COMPLETED

A defensible architecture proposal exists with no unresolved material blocker.

### NEEDS_CLARIFICATION

User/business/project clarification or verification is required before a final proposal can be selected.

### BLOCKED

A material conflict or missing system fact prevents a defensible proposal.

## Claims

Claims use the M0 classifications:

- `VERIFIED`
- `KNOWN`
- `INFERRED`
- `ASSUMED`

`UNKNOWN` and `CONFLICTING` are represented in their dedicated collections because they require blocker/verification metadata.

Each claim has:

- stable result-local `id`
- `classification`
- `statement`
- `system_specific`
- `evidence_refs`
- `source_refs`

### Supporting-reference rules

- `VERIFIED` requires at least one `evidence_ref`.
- `KNOWN` requires at least one `evidence_ref` or `source_ref`.
- a system-specific claim marked `VERIFIED` or `KNOWN` follows the same rule and must not be supported only by model background
- `INFERRED` and `ASSUMED` must remain visibly non-verified classifications

## Unknowns

Each unknown records:

- `id`
- `statement`
- `material`
- `blocks_decision`
- `verification`

A material unknown that blocks the architecture decision prevents `COMPLETED`.

## Conflicts

Each conflict records:

- `id`
- `statement`
- `material`
- `blocks_decision`
- `status`: `UNRESOLVED` or `RESOLVED`
- `source_refs`
- `verification`

An unresolved material conflict that blocks the decision prevents `COMPLETED`.

## Existing-solution discovery

The result explicitly records whether reuse-before-create discovery was performed.

Discovery checks may use:

- `SAP_STANDARD`
- `CONFIGURATION`
- `EXISTING_IMPLEMENTATION`
- `SUPPORTED_EXTENSION`
- `RELEASED_API_EVENT`
- `SIDE_BY_SIDE_EXTENSION`
- `CUSTOM_IMPLEMENTATION`

Each check records:

- category
- status: `APPLICABLE`, `NOT_APPLICABLE`, or `UNKNOWN`
- notes
- evidence references

A final proposal requires `performed: true`.

## Solution options

Candidate solution options are not facts.

Each option records:

- `id`
- `title`
- `family`
- `description`
- trade-offs
- risks
- evidence references
- assumption references
- required verification

Initial option families:

- `STANDARD_CONFIGURATION`
- `SUPPORTED_EXTENSION`
- `RELEASED_API_EVENT`
- `INTEGRATION`
- `SIDE_BY_SIDE_BTP`
- `CUSTOM_IMPLEMENTATION`
- `OTHER`

## Proposal

`proposal` is either an object or `null`.

A proposal contains:

- `selected_option_id`
- `summary`
- `rationale`
- `confidence`: `LOW`, `MEDIUM`, or `HIGH`
- evidence references
- assumption references

Rules:

- `COMPLETED` requires a non-null proposal.
- `NEEDS_CLARIFICATION` and `BLOCKED` require `proposal: null`.
- `selected_option_id` must reference an existing `solution_options[].id`.

The result may still contain candidate options while clarification is pending or the task is blocked.

## Required verification

Verification entries record:

- `id`
- `description`
- `why`
- `blocking`

A blocking verification item prevents `COMPLETED`.

## Implementation handoff

The architecture Agent does not implement the solution.

The handoff contains:

- `ready`
- `notes`

Rules:

- `ready: true` is allowed only when status is `COMPLETED`.
- non-completed results must keep `ready: false`.

## Requested capabilities

The result may declare follow-up capability requests, but M1 permits only:

- `READ`
- `QUERY`
- `ANALYZE`
- `PROPOSE`

Any request for `WRITE`, `DEPLOY`, `TRANSPORT`, or `ADMIN` is a CRITICAL contract violation.

## Next action

Initial next-action types:

- `REQUEST_CLARIFICATION`
- `VERIFY_CONTEXT`
- `REVIEW_ARCHITECTURE`
- `HANDOFF_IMPLEMENTATION`
- `NONE`

A non-completed result must not request `HANDOFF_IMPLEMENTATION`.

## Deterministic invariants

The M1 structural validator must reject:

1. unsupported contract version
2. malformed or duplicate result-local IDs
3. unsupported claim classification
4. VERIFIED claim without evidence
5. KNOWN claim without evidence/source reference
6. COMPLETED with a blocking unknown
7. COMPLETED with an unresolved blocking conflict
8. COMPLETED with blocking verification
9. COMPLETED without proposal
10. non-COMPLETED with proposal
11. proposal referencing an unknown option
12. proposal when existing-solution discovery was not performed
13. non-COMPLETED handoff marked ready
14. mutating/admin requested capability
15. non-COMPLETED next action requesting implementation handoff

These checks validate contract safety, not semantic architecture quality.
