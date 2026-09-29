# ADR-014 — M1 Result Provenance Integrity

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D141 through SAP-AW-D145
- **Scope:** M1 Technical Architect

## Context

The M1 reference runtime binds the final result to the exact input/configuration fingerprints, but provider semantic output
still contains evidence and source references.

Without an invocation-aware integrity check, a provider could fabricate an evidence identifier or source reference while
still satisfying the standalone result shape.

M1 performs no live tool execution, so accepted result provenance must be derived from the validated invocation input.

## Decision

### SAP-AW-D141

Every result `evidence_ref` accepted by the M1 runtime must resolve to an evidence ID present in the invocation input's
`evidence_catalog`.

### SAP-AW-D142

The M1 provider/model cannot create new system evidence.

New evidence may enter a later invocation only through the Context/Evidence/Tool pipeline defined by M0.

### SAP-AW-D143

Result source references used for factual/conflict provenance must resolve to source references already present in the
validated input snapshot.

### SAP-AW-D144

Result `assumption_refs` must reference result claims classified `ASSUMED`; they may not point to VERIFIED, KNOWN,
or INFERRED claims.

### SAP-AW-D145

The TypeScript reference validator must enforce the same contract-critical structural invariants as the canonical
M1 input/result contracts before a real provider adapter may be introduced.

Differences between Python evaluation utilities and the product/runtime validator must not weaken CRITICAL boundaries.

## Consequences

- a model cannot manufacture evidence IDs to make an unsupported architecture statement appear verified
- result provenance remains closed over the exact invocation snapshot
- future live evidence acquisition remains a Tool/Context Builder concern
- assumption traceability becomes mechanically meaningful
- the reference harness requires invocation-aware result validation rather than shape validation alone

## Verification / fitness implications

Reference-harness tests must include:

- fabricated result evidence reference → rejected
- fabricated result source reference → rejected
- assumption reference to non-ASSUMED claim → rejected
- valid input evidence/source references → accepted
- no provider attempt creates an accepted evidence record

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
