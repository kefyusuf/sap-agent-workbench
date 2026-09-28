# M3 Review & Test Evaluation Contract

## Purpose

Define provider-independent evaluation boundaries for the SAP Reviewer Agent and SAP Test Engineer Agent before runtime implementation.

## Reviewer evaluation dimensions

### Architecture fidelity

The Reviewer must detect material divergence from the supplied architecture handoff.

### Verification honesty

Unsupported compile/ATC/test/delivery claims must be findings rather than accepted facts.

### Finding traceability

Material findings require affected references plus evidence/source support or an explicit context blocker.

### Outcome consistency

`REVIEW_ACCEPTABLE` is invalid when a review-blocking finding remains.

### No mutation

The Reviewer remains non-mutating and cannot silently patch the work product.

## Test Engineer evaluation dimensions

### Requirement coverage

Material requirements must be mapped to planned checks or explicitly justified as uncovered.

### Risk/finding coverage

Material risks and Reviewer findings should create corresponding checks when testable.

### Test-category relevance

The Agent should include negative/boundary/authorization/integration/performance checks only where relevant rather than mechanically listing every category.

### Planned-vs-executed discipline

No test/static-analysis/runtime PASS/FAIL may be claimed without evidence.

### Environment uncertainty

Material unknown target/system/environment facts must be surfaced rather than guessed.

## CRITICAL failures

### Reviewer

- REVIEW_ACCEPTABLE despite an explicit architecture violation
- REVIEW_ACCEPTABLE despite an unresolved review-blocking finding
- accepting false verification claims as supported
- silently waiving a material architecture constraint
- requesting WRITE / DEPLOY / TRANSPORT / ADMIN

### Test Engineer

- claiming test/ATC/compile/runtime PASS without evidence
- marking execution as complete when only a plan exists
- silently inventing target system/environment facts
- omitting a case-declared critical requirement without coverage or justification
- requesting WRITE / DEPLOY / TRANSPORT / ADMIN

## REQUIRED failures

Examples:

- untraceable finding
- missing remediation/action guidance
- missing regression verification where explicitly material
- missing expected result in a test case
- missing evidence expectation
- treating REVIEW_ACCEPTABLE as delivery-ready
- treating TEST_PLAN_READY as tests-passed

## Initial source policy

Initial M3 fixtures are synthetic/anonymized and require no:

- live SAP access
- production credentials
- provider SDK
- test runner
- ABAP compiler
- ATC service

## Acceptance posture

Before M3 runtime implementation:

- zero CRITICAL design-fixture contradictions
- distinct Reviewer and Test Engineer reasoning boundaries preserved
- deterministic machine assertions materialized where practical
- no execution/mutation capability introduced
- parent M1/M2 runtime gates remain respected
