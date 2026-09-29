# ADR-003 — Context, Evidence & Provenance

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D021 through SAP-AW-D034
- **Scope:** M0 Foundation

## Context

SAP technical decisions frequently depend on a mixture of current source code, live system state, project documentation,
organization standards, official SAP documentation, user intent, historical incidents, and model background knowledge.

These sources differ in authority, freshness, scope, and revision. Without explicit semantics, an agent could silently
treat a stale document or a plausible model inference as current SAP system truth.

## Decision

### SAP-AW-D021

Knowledge and runtime Context are separate concepts.

Knowledge is available information; Context is the task-scoped subset supplied to reasoning.

### SAP-AW-D022

Agents receive task-scoped Context rather than all available Knowledge.

### SAP-AW-D023

Every material Context item preserves source, scope, freshness, revision, and provenance metadata where applicable.

### SAP-AW-D024

Authority is claim-dependent and is not equivalent to reasoning confidence.

There is no single universal source ranking for every type of claim.

### SAP-AW-D025

Material claims are classified as:

- VERIFIED
- KNOWN
- INFERRED
- ASSUMED
- UNKNOWN
- CONFLICTING

### SAP-AW-D026

Material source conflicts must be surfaced and must not be silently reconciled by an Agent.

### SAP-AW-D027

Evidence is append-oriented/immutable and revision-bound whenever the verified subject is revision-sensitive.

### SAP-AW-D028

Material recommendations must be traceable to claims, and claims to supporting evidence where evidence exists.

### SAP-AW-D029

Model-generated content is not evidence of SAP system state.

### SAP-AW-D030

Workflow completion requirements determine sufficient evidence.

Agents do not independently declare evidence sufficiency.

### SAP-AW-D031

Context specificity may refine or shadow facts but cannot weaken Policy.

### SAP-AW-D032

Secrets and credentials do not enter general Agent Context.

Runtime tools may reference secret-management facilities without exposing raw secret material.

### SAP-AW-D033

Provenance must survive retrieval, transformation, and reasoning handoffs.

### SAP-AW-D034

Task completion is evidence-bound, not output-bound.

## Consequences

- Context Builder becomes a first-class runtime concern.
- Context resolution must preserve both the effective fact and shadowed/conflicting provenance.
- Evidence and work products need revision identities where correctness depends on revision.
- "Unknown" is a valid state and must not be filled by unsupported model background.
- Later retrieval implementations must return source metadata, not anonymous text fragments.

## Verification / fitness implications

Foundation fitness must prove that:

- UNKNOWN does not silently become KNOWN
- CONFLICTING material context remains visible
- VERIFIED claims require valid supporting evidence
- evidence for revision A cannot verify revision B
- retrieval preserves source/provenance metadata
- model output alone cannot create live-system evidence

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
