# SAP ABAP Development Input Contract

## Contract identity

`m2.abap-development-input.v1`

This contract defines the provider-independent input envelope for the M2 SAP ABAP Development Agent.

M2 consumes an already-scoped implementation handoff. It does not rediscover or silently replace the architecture decision.

## Top-level fields

- `contract_version`
- `task`
- `scope`
- `architecture_handoff`
- `requirements`
- `existing_objects`
- `unknowns`
- `evidence_catalog`
- `capability_boundary`
- `resolved_configuration_fingerprint`
- `requested_result_contract`

## Task

`task` contains:

- `id`
- `implementation_objective`
- `requested_outcome`

Initial requested outcome:

`IMPLEMENTATION_WORK_PRODUCT`

The implementation objective must remain within the supplied architecture handoff.

## Scope

`scope` contains:

- `modules`
- `systems`
- `environments`
- `project`

Unknown scope values remain empty/null rather than being guessed.

## Architecture handoff

The handoff is first-class input.

It contains:

- `id`
- `fingerprint`
- `status`
- `approach`
- `constraints`
- `source_refs`

Allowed status values:

- `APPROVED`
- `APPROVED_WITH_VERIFICATION`

Each architecture constraint has:

- `id`
- `statement`
- `material`

A material constraint cannot be silently overridden by M2.

If the implementation requires violating a material constraint, the result must return to architecture review rather than produce a ready work product.

## Requirements

Each implementation requirement contains:

- `id`
- `statement`
- `evidence_refs`
- `source_refs`

Requirements preserve traceability to approved/project/user sources.

## Existing objects

Current-system object identities are supplied explicitly.

Each entry contains:

- `id`
- `name`
- `kind`
- `evidence_refs`
- `source_refs`

The `id` is a result-safe local reference such as `OBJ-001`.

The Agent should reference existing objects through these IDs rather than inventing new current-system identities.

Initial object kinds:

- `CLASS`
- `INTERFACE`
- `TABLE`
- `STRUCTURE`
- `FUNCTION_MODULE`
- `BADI_DEFINITION`
- `BADI_IMPLEMENTATION`
- `ENHANCEMENT`
- `CDS`
- `RAP_OBJECT`
- `ODATA_SERVICE`
- `FORM`
- `JOB`
- `OTHER`

## Unknowns

Each unknown contains:

- `id`
- `statement`
- `material`
- `blocks_implementation`
- `verification`

A material unknown with `blocks_implementation: true` prevents `WORK_PRODUCT_READY`.

## Evidence catalog

Evidence records reuse the M0 evidence vocabulary.

Every evidence reference in requirements/existing objects must resolve inside the input evidence catalog.

M2 cannot create new system evidence.

## Capability boundary

Initial M2 SAP-system capabilities remain:

- `READ`
- `QUERY`
- `ANALYZE`
- `PROPOSE`

The input contract rejects:

- `WRITE`
- `DEPLOY`
- `TRANSPORT`
- `ADMIN`

## Resolved configuration fingerprint

The input carries the exact resolved runtime/customization configuration fingerprint:

`sha256:<64 lowercase hex characters>`

## Result contract

M2 v1 requests:

`m2.abap-development-result.v1`

## Input fingerprint

The orchestration layer computes the invocation input fingerprint from canonical UTF-8 JSON:

1. sort object keys lexicographically
2. preserve array order
3. use compact separators
4. SHA-256
5. lowercase hex with `sha256:` prefix

The result binds to:

- this input fingerprint
- the resolved configuration fingerprint
- the architecture handoff fingerprint

## Secret boundary

Raw credentials, tokens, passwords, private keys, and other secret material are forbidden in the M2 input envelope.
