# ADR-023 — M3 Deterministic Contract Validation

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D227 through SAP-AW-D236
- **Scope:** M3 Review & Verification

## Context

M3 Reviewer/Test Engineer boundaries, normalized cases, and provider-independent contracts are materialized.

Product runtime and live verification remain blocked by parent gates, but deterministic evaluation tooling can validate
review/test-plan contracts without invoking a model, SAP system, compiler, ATC service, or test runner.

## Decision

### SAP-AW-D227

M3 may implement deterministic contract/evaluation tooling while Reviewer/Test Engineer product runtimes remain blocked.

### SAP-AW-D228

The M3 deterministic validator uses Python standard library only.

It performs no network, provider, SAP, compiler, ATC, test execution, deployment, or transport action.

### SAP-AW-D229

Reviewer input/result validation binds review outputs to exact input, configuration, architecture-handoff, and implementation fingerprints.

### SAP-AW-D230

REVIEW_ACCEPTABLE is deterministically rejected when architecture alignment is not preserved,
a material architecture constraint is not represented, a blocking finding remains, or a blocking review unknown remains.

### SAP-AW-D231

Reviewer finding references are closed over the invocation snapshot.

Affected work-product/object references, architecture-constraint references, requirement references,
evidence references, and source references must resolve to supplied input context.

### SAP-AW-D232

Outstanding implementation verification debt must remain represented through review.

Review acceptance cannot silently convert pending compile/ATC/test work into verified state.

### SAP-AW-D233

Test-plan validation requires critical requirements to have planned-check coverage or an explicit justified exclusion.

Case-specific material constraint coverage may add stricter requirements.

### SAP-AW-D234

Planned-check trace references and coverage check references must resolve to the exact test-plan input/result snapshot.

### SAP-AW-D235

Test Engineer PASS/FAIL claims require evidence IDs from the invocation input evidence catalog.

A plan with no evidence cannot create executed verification claims.

### SAP-AW-D236

Initial M3 self-tests include positive Reviewer/Test Engineer results and negative architecture-acceptance,
critical-coverage, and false-verification cases.

Passing deterministic self-tests is required before any later M3 runtime implementation can be considered.

## Consequences

- review acceptance and test-plan readiness become executable design invariants
- architecture drift cannot be hidden behind prose
- critical requirement coverage is mechanically checkable
- false PASS/FAIL claims are structurally rejectable
- parent runtime gates remain intact

## Verification / fitness implications

The self-test suite must validate all four normalized inputs plus:

- valid REVIEW_ACCEPTABLE
- valid CHANGES_REQUIRED
- invalid REVIEW_ACCEPTABLE with architecture violation
- valid TEST_PLAN_READY for TEST-001
- valid TEST_PLAN_READY for TEST-002
- invalid critical-requirement coverage
- invalid PASS claim without invocation evidence

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
