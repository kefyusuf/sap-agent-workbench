# ADR-019 — M2 Deterministic Contract Validation

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D183 through SAP-AW-D191
- **Scope:** M2 ABAP Development Agent

## Context

M2 input/result contracts and normalized cases are now materialized.

Because the parent M1 runtime verification gate remains open, M2 must not implement an Agent runtime.
However, deterministic evaluation tooling can validate the M2 contracts without invoking a provider, SAP, or an ABAP runtime.

## Decision

### SAP-AW-D183

M2 may implement deterministic contract/evaluation tooling while the M2 product runtime remains blocked.

The tooling is not an Agent runtime.

### SAP-AW-D184

The deterministic M2 validator uses Python standard library only and requires no network, provider SDK, SAP connection, or credential.

### SAP-AW-D185

M2 input validation computes the canonical SHA-256 input fingerprint using the same semantic algorithm established by M1.

### SAP-AW-D186

Result validation is invocation-aware and checks input/configuration/architecture-handoff provenance binding.

### SAP-AW-D187

Existing-object, proposed-object, implementation-plan, and work-product references are validated as closed local references.

Unknown object references are contract violations.

### SAP-AW-D188

WORK_PRODUCT_READY is rejected when the invocation input still contains a material implementation blocker,
when result unknowns block the work product, or when architecture alignment requires review.

### SAP-AW-D189

Verification PASS/FAIL claims are checked against the invocation evidence catalog and the evidence compatibility rules from ADR-018.

### SAP-AW-D190

Case-specific machine assertions are evaluation-only and do not redefine the product result contract.

### SAP-AW-D191

The initial self-test suite includes positive ready, positive blocked, and negative false-verification examples.

A passing deterministic self-test is required before any M2 runtime implementation can later be considered.

## Consequences

- M2 contracts can be exercised while product runtime work remains correctly blocked
- object/reference integrity and verification honesty become executable design constraints
- M2 runtime implementation can later reuse the proven semantics without requiring a model judge
- parent M1 runtime verification remains an independent prerequisite for M2 runtime work

## Verification / fitness implications

The deterministic self-test must cover:

- all four normalized case inputs
- a valid WORK_PRODUCT_READY result
- a valid BLOCKED result
- rejection of ATC PASS backed only by APPROVED_DOCUMENT evidence

Future cases may extend coverage without weakening these CRITICAL rules.

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
