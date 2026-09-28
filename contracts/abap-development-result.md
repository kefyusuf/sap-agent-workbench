# SAP ABAP Development Result Contract

## Contract identity

`m2.abap-development-result.v1`

This contract defines the machine-readable work product produced by the M2 SAP ABAP Development Agent.

The result represents implementation work ready for review, clarification, or blocking.

It does **not** represent workflow DONE or transport readiness.

## Top-level fields

- `contract_version`
- `task_id`
- `provenance`
- `status`
- `architecture_alignment`
- `unknowns`
- `existing_objects_used`
- `proposed_new_objects`
- `implementation_plan`
- `work_products`
- `assumptions`
- `risks`
- `required_verification`
- `verification_claims`
- `review_handoff`
- `requested_capabilities`
- `next_action`

## Provenance

`provenance` contains:

- `input_fingerprint`
- `configuration_fingerprint`
- `architecture_handoff_fingerprint`

All three are runtime-bound values.

Provider/model output cannot authoritatively set or override them.

## Status

Allowed values:

- `WORK_PRODUCT_READY`
- `NEEDS_CLARIFICATION`
- `BLOCKED`

### WORK_PRODUCT_READY

A reviewable implementation work product can be produced without violating the supplied architecture or hiding a material blocker.

This does **not** mean:

- compiled
- ATC-clean
- tested
- deployed
- transport-ready

### NEEDS_CLARIFICATION

A material project/business/implementation fact requires clarification before the work product can be finalized.

### BLOCKED

A material implementation dependency or architecture conflict prevents a defensible work product.

## Architecture alignment

`architecture_alignment` contains:

- `status`: `PRESERVED` or `REQUIRES_REVIEW`
- `constraint_results`

Each constraint result references an input architecture-constraint ID and records:

- `constraint_ref`
- `status`: `PRESERVED` or `REQUIRES_REVIEW`
- `notes`

Rules:

- `WORK_PRODUCT_READY` requires `architecture_alignment.status = PRESERVED`
- any material architecture deviation requires architecture review
- M2 never silently changes the upstream approach

## Unknowns

Unresolved implementation facts remain explicit in the result.

Each unknown contains:

- `id`
- `statement`
- `material`
- `blocks_work_product`
- `verification`

Rules:

- `WORK_PRODUCT_READY` cannot contain a material unknown with `blocks_work_product: true`
- the Agent must not remove an input blocker by inventing a system fact
- an input blocker may disappear only when the invocation includes evidence/context that resolves it

## Existing objects used

Existing/current-system objects are referenced only by input object IDs:

- `object_ref`
- `purpose`

The result must not create a new existing-object identity.

Each `object_ref` must resolve to `input.existing_objects[].id`.

## Proposed new objects

New object design is separate from current-system facts.

Each proposed object contains:

- `id` — local `NEW-...` identity
- `proposed_name`
- `kind`
- `purpose`

A proposed name is not an assertion that the object already exists.

## Implementation plan

Each step contains:

- `id`
- `description`
- `object_refs`

An object reference may point to:

- an input existing-object ID
- a result proposed-new-object ID

No other object identity is valid.

## Work products

A work product contains:

- `id`
- `type`
- `target_object_ref`
- `language`
- `content`

Initial work-product types:

- `ABAP_SOURCE`
- `PATCH`
- `PSEUDOCODE`
- `DDIC_DESIGN`
- `TEST_SEAM`
- `IMPLEMENTATION_NOTE`
- `OTHER`

A work product is a proposal artifact, not verification evidence.

## Assumptions

Each assumption contains:

- `id`
- `statement`
- `verification`

Assumptions remain visibly unverified.

## Risks

Each risk contains:

- `id`
- `category`
- `description`
- `mitigation`

Initial categories:

- `CORRECTNESS`
- `PERFORMANCE`
- `SECURITY`
- `AUTHORIZATION`
- `TRANSACTIONALITY`
- `UPGRADE`
- `INTEGRATION`
- `MAINTAINABILITY`
- `OTHER`

## Required verification

Each verification item contains:

- `id`
- `type`
- `description`
- `blocking_for_delivery`

Initial verification types:

- `COMPILE`
- `ATC`
- `UNIT_TEST`
- `INTEGRATION_TEST`
- `AUTHORIZATION`
- `PERFORMANCE`
- `PAYLOAD_CONTRACT`
- `RUNTIME`
- `OTHER`

## Verification claims

Verification claims describe evidence-backed verification already supplied to the invocation.

Each claim contains:

- `type`
- `status`: `PASS` or `FAIL`
- `evidence_refs`

Rules:

- every PASS/FAIL claim requires at least one input evidence reference
- referenced evidence must be compatible with the verification type
- an absent evidence-backed verification remains in `required_verification`
- generated code alone can never create a PASS claim

Initial evidence compatibility:

| Verification | Compatible input evidence types |
|---|---|
| COMPILE | EXECUTION_RESULT, STATIC_ANALYSIS |
| ATC | STATIC_ANALYSIS |
| UNIT_TEST | TEST_RESULT |
| INTEGRATION_TEST | TEST_RESULT |
| AUTHORIZATION | TEST_RESULT, CONFIGURATION |
| PERFORMANCE | TEST_RESULT, EXECUTION_RESULT |
| PAYLOAD_CONTRACT | TEST_RESULT, EXECUTION_RESULT |
| RUNTIME | EXECUTION_RESULT, LOG |
| OTHER | must be explicitly justified by the verification pipeline |

An APPROVED_DOCUMENT or model-generated work product is not sufficient evidence for a compile/ATC/test PASS claim.

## Review handoff

`review_handoff` contains:

- `ready_for_review`
- `notes`

Rules:

- `WORK_PRODUCT_READY` requires `ready_for_review: true`
- non-ready statuses require `ready_for_review: false`

Review readiness is not delivery readiness.

## Capability requests

Allowed M2 capability requests remain:

- `READ`
- `QUERY`
- `ANALYZE`
- `PROPOSE`

`WRITE`, `DEPLOY`, `TRANSPORT`, and `ADMIN` are CRITICAL contract violations.

## Next action

Initial values:

- `REQUEST_CLARIFICATION`
- `VERIFY_IMPLEMENTATION_CONTEXT`
- `RETURN_TO_ARCHITECTURE`
- `HANDOFF_REVIEW`
- `NONE`

A non-ready result cannot request `HANDOFF_REVIEW`.

## Deterministic invariants

The future M2 structural validator must reject at least:

1. unsupported contract version
2. malformed provenance fingerprints
3. architecture handoff fingerprint mismatch
4. WORK_PRODUCT_READY with a blocking input/result unknown
5. WORK_PRODUCT_READY with architecture status REQUIRES_REVIEW
6. existing-object reference not present in input
7. proposed-new object ID/name represented as an existing object
8. implementation/work-product object reference not resolvable to existing or proposed object IDs
9. verification PASS/FAIL without input evidence
10. verification PASS/FAIL backed only by an incompatible evidence type
11. false review readiness for non-ready status
12. SAP mutation/admin capability request
13. non-ready result requesting HANDOFF_REVIEW

Semantic ABAP quality remains a separate evaluation layer.
