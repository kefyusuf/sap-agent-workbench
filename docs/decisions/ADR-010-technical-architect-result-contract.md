# ADR-010 — Technical Architect Structured Result Contract

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D102 through SAP-AW-D110
- **Scope:** M1 Technical Architect

## Context

M1 has an Agent responsibility boundary and property-based evaluation cases, but a provider-independent runtime cannot
be implemented safely until the Agent result has a stable machine-readable contract.

The result contract must preserve M0 evidence semantics and make critical M1 boundary failures deterministically detectable.

## Decision

### SAP-AW-D102

The Technical Architect result is a first-class machine-readable contract independent from provider prompt wording.

Initial contract identity:

`m1.technical-architect-result.v1`

### SAP-AW-D103

Result status is one of:

- `COMPLETED`
- `NEEDS_CLARIFICATION`
- `BLOCKED`

Status reflects evidence/context sufficiency rather than whether the model produced text.

### SAP-AW-D104

Claims remain explicitly classified and traceable.

VERIFIED requires evidence.
KNOWN requires evidence or source provenance.
INFERRED and ASSUMED remain visibly non-verified.

### SAP-AW-D105

Material decision-blocking unknowns, unresolved conflicts, or blocking verification items prohibit `COMPLETED`.

### SAP-AW-D106

A selected proposal is nullable and exists only for `COMPLETED`.

Non-completed results may still contain candidate solution options but cannot select a final proposal.

### SAP-AW-D107

Existing-solution discovery is represented explicitly in the result.

A final proposal requires discovery to have been performed.

### SAP-AW-D108

A deterministic provider-independent validator enforces structural and safety invariants.

It does not judge semantic SAP architecture quality.

### SAP-AW-D109

M1 result capability requests are limited to READ, QUERY, ANALYZE, and PROPOSE.

Any WRITE, DEPLOY, TRANSPORT, or ADMIN request is a CRITICAL contract violation.

### SAP-AW-D110

Every Technical Architect result is bound to the deterministic semantic fingerprint of the exact input/context snapshot
and the resolved runtime configuration that produced it.

The result must not be reused as if it were produced from a different input or configuration.

## Consequences

- provider adapters have a stable target result shape
- critical status/evidence/capability errors can be detected without an LLM judge
- blocked/clarification states are representable without forcing a fake recommendation
- semantic architecture quality remains a separate evaluation concern
- result-contract evolution can be versioned explicitly
- work products can be tied to the exact input/configuration state that produced them

## Verification / fitness implications

The validator must cover at least:

- claim support requirements
- duplicate IDs
- blocker/status consistency
- proposal/status consistency
- proposal option reference validity
- discovery-before-final-proposal
- handoff/status consistency
- capability boundary
- next-action/status consistency
- input/configuration provenance fingerprint validity

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
