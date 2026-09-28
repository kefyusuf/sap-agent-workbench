# ADR-022 — M3 Reviewer & Test Engineer Contracts

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D214 through SAP-AW-D226
- **Scope:** M3 Review & Verification

## Context

M3 Agent/evaluation boundaries are defined, but the initial cases cannot become deterministic until review findings,
review outcomes, coverage mapping, planned checks, and provenance have machine-readable contracts.

## Decision

### SAP-AW-D214

Reviewer input uses provider-independent contract `m3.sap-review-input.v1`.

### SAP-AW-D215

Reviewer result uses provider-independent contract `m3.sap-review-result.v1`.

### SAP-AW-D216

Reviewer input/result bind to exact architecture-handoff, implementation-snapshot, configuration, and canonical input fingerprints.

### SAP-AW-D217

Reviewer findings are traceable structured records with severity, category, affected references, supporting references,
required action, and blocking semantics.

### SAP-AW-D218

REVIEW_ACCEPTABLE requires preserved architecture alignment and no unresolved review-blocking finding/unknown.

Outstanding verification debt may remain and is preserved explicitly.

### SAP-AW-D219

Reviewer review acceptance means proceed to verification only; delivery/transport readiness is outside the Reviewer contract.

### SAP-AW-D220

Test Engineer input uses provider-independent contract `m3.sap-test-plan-input.v1`.

### SAP-AW-D221

Test Engineer result uses provider-independent contract `m3.sap-test-plan-result.v1`.

### SAP-AW-D222

Test-plan coverage explicitly maps requirements, constraints, Reviewer findings, and risks to planned checks or justified exclusions.

### SAP-AW-D223

Critical requirements require coverage unless an explicit non-empty exclusion justification is recorded.

### SAP-AW-D224

Planned checks include traceability, preconditions, expected result, expected evidence type, and delivery-blocking semantics.

Planning does not imply execution.

### SAP-AW-D225

Reviewer/Test Engineer result verification claims require evidence from the exact invocation evidence catalog;
planning or review text cannot create PASS/FAIL evidence.

### SAP-AW-D226

Both M3 contracts preserve the READ/QUERY/ANALYZE/PROPOSE boundary and may be designed/evaluated while runtime remains blocked.

## Consequences

- REVIEW_ACCEPTABLE and TEST_PLAN_READY become mechanically distinct from delivery readiness
- review findings can feed test planning through stable references
- critical requirement coverage becomes machine-checkable
- planned-vs-executed verification remains explicit
- M3 can progress through deterministic contract tooling without runtime/provider work

## Verification / fitness implications

Normalized M3 cases must demonstrate:

- acceptable review with preserved verification debt
- changes-required review for architecture violation
- critical requirement coverage
- planned checks without fabricated execution claims
- no mutation/admin capability

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
