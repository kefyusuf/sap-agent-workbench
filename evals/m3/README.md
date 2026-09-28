# M3 Reviewer & Test Engineer Evaluation Fixtures

These fixtures exercise the design boundaries from ADR-020 and ADR-021.

They are synthetic/anonymized and require no provider, SAP system, compiler, ATC service, or test runner.

## Initial cases

### Reviewer

- REVIEW-001 — architecture-preserving work product with verification debt
- REVIEW-002 — implementation violates a material no-direct-table-update constraint

### Test Engineer

- TEST-001 — order-validation work product requires traceable positive/negative/static verification
- TEST-002 — PI/PO payload change requires regression and payload-contract coverage without inventing PASS results

## Fixture purpose

The initial set checks:

- Reviewer architecture fidelity
- review-outcome consistency
- verification honesty
- distinction between review acceptance and delivery readiness
- requirement-to-test coverage
- planned-vs-executed verification discipline
- no mutation/execution capability

These fixtures do not yet define final M3 input/result contracts.
