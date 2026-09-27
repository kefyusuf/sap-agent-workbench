# Evaluation & Foundation Fitness Model

## Two evaluation layers

Foundation fitness and agent-quality evaluation are separate.

### Foundation fitness

Validates architecture invariants:

- component boundaries
- context/evidence semantics
- policy enforcement
- approval binding
- capability isolation
- customization boundaries
- provenance
- completion semantics

### Agent quality

Later evaluates domain behavior such as requirement understanding, SAP solution quality,
hallucination, architecture reasoning, ABAP quality, test coverage, and incident diagnosis.

M0 focuses on foundation fitness.

## Fitness scenario

A scenario has:

- id
- title
- preconditions/given
- action/when
- expected result/then
- criticality
- revision

The serialization format is not yet a product contract.

## Result states

Use:

- PASS
- FAIL
- BLOCKED
- NOT_APPLICABLE

Do not use an aggregate numeric score to mask a critical failure.

## Criticality

- CRITICAL — failure blocks the milestone
- REQUIRED — expected for milestone completion
- ADVISORY — informative quality/optimization signal

## Deterministic first

M0 foundation correctness should be primarily deterministic.

Safety-critical enforcement must not depend on an LLM judge.

## Safety Kernel Suite

The initial critical suite must cover at least:

1. Agent cannot bypass policy
2. More restrictive policy wins
3. Project cannot weaken organization safety
4. Unknown target blocks side effects
5. Model output is not system evidence
6. VERIFIED claim requires supporting evidence
7. Stale evidence cannot verify a new revision
8. Approval is bound to exact action fingerprint
9. Approval cannot override MUST_NOT_PROCEED
10. Mandatory verification cannot be customized away
11. Protected fields cannot be overridden
12. MVP exposes no SAP mutation capabilities

## Negative-path requirement

Every critical invariant should include positive, negative, and relevant boundary cases.

## Property-style invariants

Examples:

- adding a more restrictive policy can never produce a less restrictive result
- changing a fingerprint-significant action field invalidates approval
- every VERIFIED claim has valid supporting evidence
- a newer work-product revision cannot reuse stale revision-bound verification

## Reproducibility

Fitness runs record:

- core version
- SAP domain pack versions
- customization pack versions
- resolved configuration fingerprint
- scenario revision
- runtime version
- result

## Public vs private evals

The core repository contains synthetic or anonymized evaluation fixtures.

Organization/project-specific evaluation cases belong in private customization packs.

Lower-level packs may add stricter tests but may not disable inherited critical invariants.

## M0 exit criteria

M0 closes only when:

1. canonical contracts are documented
2. architecture decisions are recorded
3. component responsibilities are unambiguous
4. context/evidence semantics are documented
5. policy/approval semantics are documented
6. customization semantics are documented
7. foundation fitness scenarios are materialized
8. all CRITICAL scenarios pass
9. all REQUIRED scenarios pass or have an explicit non-safety blocker
10. no architecture blocker remains for M1

Safety-critical failures cannot be accepted blockers.

M0 DONE means the architecture is:

DEFINED
CONSISTENT
TESTABLE
REPRODUCIBLE
SAFE TO IMPLEMENT
