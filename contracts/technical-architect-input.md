# SAP Technical Architect Input Contract

## Contract identity

`m1.technical-architect-input.v1`

This contract defines the provider-independent input envelope for the M1 SAP Technical Architect Agent.

The Agent receives a resolved task/context snapshot. It does not discover arbitrary global knowledge on its own.

## Top-level fields

- `contract_version`
- `task`
- `scope`
- `constraints`
- `context`
- `evidence_catalog`
- `capability_boundary`
- `resolved_configuration_fingerprint`
- `requested_result_contract`

## Task

`task` contains:

- `id`
- `requirement`
- `requested_outcome`

Initial `requested_outcome`:

- `ARCHITECTURE_ASSESSMENT`

The requirement is the user/business intent to preserve, not an instruction to invent missing system facts.

## Scope

`scope` contains:

- `modules`
- `systems`
- `environments`
- `project`
- `landscape`

Unknown scope values are represented by empty arrays or nulls rather than guessed values.

## Constraints

Each constraint contains:

- `id`
- `statement`
- `authority`
- `source_refs`

Initial authority labels reuse M0 terminology:

- `SYSTEM_VERIFIED`
- `PROJECT_APPROVED`
- `ORGANIZATION_APPROVED`
- `OFFICIAL_VENDOR`
- `INTERNAL_REFERENCE`
- `USER_PROVIDED`

Constraints inform reasoning but do not replace enforceable Policy.

## Resolved context

`context` contains:

- `claims`
- `unknowns`
- `conflicts`

Claims preserve:

- classification
- statement
- system-specific marker
- evidence references
- source references

Input claim classifications:

- `VERIFIED`
- `KNOWN`
- `INFERRED`
- `ASSUMED`

Unknown and conflicting state remains explicit rather than being filled by the Agent.

## Evidence catalog

`evidence_catalog` describes evidence IDs referenced by input claims.

Each entry contains:

- `id`
- `type`
- `source_ref`
- `revision`
- `summary`

Initial evidence types reuse the M0 evidence vocabulary.

A VERIFIED input claim must reference catalogued evidence.

## Capability boundary

The invocation explicitly supplies the capabilities available to M1.

Allowed values:

- `READ`
- `QUERY`
- `ANALYZE`
- `PROPOSE`

The input contract rejects:

- `WRITE`
- `DEPLOY`
- `TRANSPORT`
- `ADMIN`

This is descriptive input to the Agent; real authorization remains enforced by the M0 runtime boundary.

## Resolved configuration fingerprint

`resolved_configuration_fingerprint` binds the invocation to the resolved Agent/Skill/Policy/Customization configuration.

It uses the M0 semantic fingerprint form:

`sha256:<64 lowercase hex characters>`

## Requested result contract

M1 v1 requires:

`m1.technical-architect-result.v1`

A provider adapter may serialize the input differently for a model API, but it may not change the semantic input contract.

## Input fingerprint

The orchestration layer computes an input fingerprint over the complete validated input envelope.

Algorithm:

1. serialize the entire input envelope as canonical UTF-8 JSON
2. sort object keys lexicographically
3. use compact separators
4. preserve array order
5. compute SHA-256
6. encode as lowercase hex with `sha256:` prefix

The input envelope does not contain its own fingerprint.

The produced Technical Architect result records this fingerprint under:

`provenance.input_fingerprint`

The result also copies the input's:

`resolved_configuration_fingerprint`

to:

`provenance.configuration_fingerprint`

## Secret boundary

Raw credentials and secret material are forbidden in the input envelope.

The input may contain opaque credential/capability references only when required by future read-only tooling.

## Provider boundary

Provider adapters may:

- serialize this envelope
- translate it into provider message/tool structures
- request a result conforming to the selected result contract

Provider adapters may not:

- add unverified SAP system facts
- silently drop material conflicts/unknowns
- widen the capability boundary
- change the requested result contract
- mutate the resolved configuration fingerprint

## Initial M1 boundary

The v1 input contract supports synthetic/anonymized evaluation without:

- live SAP access
- private company data
- production credentials
- provider-specific runtime behavior
