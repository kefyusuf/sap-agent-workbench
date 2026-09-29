# ADR-017 — ABAP Development Input & Result Contracts

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D165 through SAP-AW-D176
- **Scope:** M2 ABAP Development Agent

## Context

The M2 Agent boundary and evaluation cases are defined, but implementation cases cannot become machine-checkable until
the architecture handoff, existing-object context, implementation work product, and verification honesty rules have stable contracts.

M2 must preserve the separation between current-system facts and proposed-new objects, and between generated code and verification evidence.

## Decision

### SAP-AW-D165

M2 uses a provider-independent input contract:

`m2.abap-development-input.v1`

### SAP-AW-D166

The architecture handoff is first-class input and carries an immutable semantic fingerprint, status, approach, constraints,
and source provenance.

### SAP-AW-D167

Existing/current-system SAP objects are supplied through explicit local object IDs.

M2 may reference those IDs but cannot invent additional existing-object identities.

### SAP-AW-D168

New object design is represented separately as `proposed_new_objects`.

A proposed name is never interpreted as evidence that the object already exists.

### SAP-AW-D169

M2 uses a provider-independent result contract:

`m2.abap-development-result.v1`

### SAP-AW-D170

M2 result status is one of:

- WORK_PRODUCT_READY
- NEEDS_CLARIFICATION
- BLOCKED

WORK_PRODUCT_READY means ready for review only, not verified/deliverable/DONE.

### SAP-AW-D171

A WORK_PRODUCT_READY result requires preserved architecture alignment and no material input unknown blocking implementation.

### SAP-AW-D172

Implementation plan/work-product object references must resolve only to supplied existing-object IDs or explicitly proposed-new-object IDs.

### SAP-AW-D173

Generated source/code artifacts are never verification evidence.

Verification PASS/FAIL claims require explicit input evidence references.

### SAP-AW-D174

M2 result provenance binds to:

- exact input fingerprint
- resolved configuration fingerprint
- architecture handoff fingerprint

### SAP-AW-D175

M2 capability requests remain limited to READ, QUERY, ANALYZE, and PROPOSE.

SAP-system WRITE, DEPLOY, TRANSPORT, and ADMIN remain invalid.

### SAP-AW-D176

M2 input/result contracts may be materialized and evaluated while the M2 runtime remains blocked on parent M1 verification.

Contract design does not authorize M2 runtime implementation.

## Consequences

- the four initial M2 cases can be normalized into machine-checkable inputs
- existing vs proposed object identity is mechanically representable
- architecture drift can be surfaced explicitly
- code-generation output cannot be mistaken for compile/ATC/test evidence
- review readiness becomes distinct from delivery readiness
- M2 remains design-only until the parent gate clears

## Verification / fitness implications

The initial normalized cases must demonstrate:

- supplied existing-object references resolve
- missing exact object context can block work-product readiness
- modernization constraints remain explicit
- integration-path constraints remain explicit
- no mutation capability is present
- no verification PASS is present without evidence

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
