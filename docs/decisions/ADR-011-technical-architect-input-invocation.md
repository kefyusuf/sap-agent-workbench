# ADR-011 — Technical Architect Input & Invocation Contract

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D111 through SAP-AW-D119
- **Scope:** M1 Technical Architect

## Context

The M1 result contract is stable, but provider-specific runtime work must not begin until the semantic input to the Agent
is equally explicit.

Without an input contract, provider adapters could silently widen context, lose provenance, invent missing system state,
or alter capability boundaries.

## Decision

### SAP-AW-D111

The Technical Architect receives a first-class provider-independent input envelope.

Initial contract identity:

`m1.technical-architect-input.v1`

### SAP-AW-D112

The Agent receives a resolved context/evidence snapshot, not unrestricted access to the global Knowledge registry.

Unknown and conflicting state remains explicit in the input.

### SAP-AW-D113

Each invocation receives an exact resolved configuration fingerprint and requests an explicit result-contract version.

### SAP-AW-D114

The orchestration layer computes a deterministic SHA-256 input fingerprint over canonical JSON of the complete validated
input envelope.

Array order is preserved; object keys are sorted.

### SAP-AW-D115

Input VERIFIED claims must reference evidence IDs present in the input evidence catalog.

KNOWN claims require evidence or source provenance.

### SAP-AW-D116

The input capability boundary is explicit and limited to READ, QUERY, ANALYZE, and PROPOSE for M1.

Mutation/admin capabilities are invalid input.

### SAP-AW-D117

Raw secrets and credentials are forbidden in the Agent input envelope.

### SAP-AW-D118

Provider adapters may serialize the input but may not alter its semantic content, widen capabilities,
drop material unknown/conflict state, or change the requested result contract.

### SAP-AW-D119

The produced result must bind to both:

- the computed input fingerprint
- the input resolved configuration fingerprint

This preserves revision/configuration provenance across provider execution.

## Consequences

- providers receive the same semantic task/context contract
- M1 can compare providers without changing the Agent boundary
- exact input snapshots become replayable/auditable
- result provenance can be mechanically checked
- live SAP retrieval remains a later Context Builder/Tool concern rather than hidden provider behavior

## Verification / fitness implications

Input validation must reject:

- unsupported contract versions
- malformed task/scope
- unsupported or unresolved evidence references
- VERIFIED claims without catalogued evidence
- mutation/admin capabilities
- malformed resolved configuration fingerprints
- raw secret material
- unsupported requested result contract

Case-aware result validation should verify that result provenance matches the case input fingerprint and configuration fingerprint.

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
