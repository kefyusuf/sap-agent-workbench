# M3 Reviewer & Test Engineer Evaluation Fixtures

These fixtures exercise ADR-020 through ADR-022.

They are synthetic/anonymized and require no provider, SAP system, compiler, ATC service, or test runner.

## Initial cases

### Reviewer

- REVIEW-001 — architecture-preserving work product with outstanding verification debt
- REVIEW-002 — implementation violates a material no-direct-table-update constraint

### Test Engineer

- TEST-001 — order-validation work product requires traceable positive/negative/static verification
- TEST-002 — PI/PO payload change requires regression and payload-contract coverage without invented PASS results

## Contracts

Reviewer input/result:

```text
m3.sap-review-input.v1
m3.sap-review-result.v1

evals/m3/sap-review-input.schema.json
evals/m3/sap-review-result.schema.json
```

Test Engineer input/result:

```text
m3.sap-test-plan-input.v1
m3.sap-test-plan-result.v1

evals/m3/sap-test-plan-input.schema.json
evals/m3/sap-test-plan-result.schema.json
```

## Normalized fixtures

All four initial cases contain provider-independent `input` envelopes plus machine-readable `output_assertions`.

Reviewer assertions cover:

- outcome
- architecture alignment
- blocking findings
- required constraint/work-product references
- verification-debt preservation
- proceed-to-verification semantics
- forbidden mutation capabilities

Test Engineer assertions cover:

- plan status
- critical requirement coverage
- material constraint coverage
- minimum planned checks
- zero invented execution claims
- execution-handoff readiness
- forbidden mutation capabilities

## Core distinctions

```text
REVIEW_ACCEPTABLE
!=
delivery / transport ready

TEST_PLAN_READY
!=
tests executed
!=
tests passed
```

No runtime or verification executor is introduced by these fixtures.
