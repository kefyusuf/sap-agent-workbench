# ADR-006 — Foundation Evaluation & M0 Gate

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D071 through SAP-AW-D083
- **Scope:** M0 Foundation

## Context

A documented architecture is insufficient if its safety and resolution rules cannot be tested.

The first implementation milestone should validate deterministic foundation invariants before evaluating SAP domain reasoning.
A single aggregate score must not allow a critical safety failure to be masked by many passing tests.

## Decision

### SAP-AW-D071

Foundation fitness and Agent-quality evaluation are separate evaluation layers.

### SAP-AW-D072

Foundation fitness is scenario-based and primarily deterministic.

### SAP-AW-D073

Safety-critical foundation correctness must not depend on an LLM judge.

### SAP-AW-D074

Foundation scenario results are:

- PASS
- FAIL
- BLOCKED
- NOT_APPLICABLE

No aggregate numeric score can override a CRITICAL failure.

### SAP-AW-D075

Fitness scenarios are classified:

- CRITICAL
- REQUIRED
- ADVISORY

### SAP-AW-D076

Every critical architecture invariant requires negative-path testing and relevant boundary coverage.

### SAP-AW-D077

Policy monotonicity, approval binding, evidence revision binding, and protected customization boundaries
are executable fitness invariants.

### SAP-AW-D078

M0 provides a minimal Safety Kernel Suite that must pass before M1.

### SAP-AW-D079

Foundation fitness runs are revision- and resolved-configuration-fingerprint-bound.

### SAP-AW-D080

The generic repository contains synthetic or anonymized evaluation fixtures.

Organization/project-specific cases remain in private Customization Packs.

### SAP-AW-D081

Lower-level customization may add stricter fitness requirements but cannot disable inherited critical fitness invariants.

### SAP-AW-D082

Workflow DONE eligibility is itself subject to foundation fitness testing.

### SAP-AW-D083

M0 closes only when no unresolved architecture blocker remains for M1.

## Safety Kernel baseline

The initial critical suite covers at least:

1. Agent cannot bypass Policy
2. More restrictive Policy wins
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

## Consequences

- M0 can fail even when most tests pass if one CRITICAL invariant fails.
- Safety Kernel tests must remain provider-independent.
- SAP reasoning quality evaluation starts later, after foundation execution semantics exist.
- M0 closure becomes an evidence-based gate rather than a documentation milestone.

## Verification / fitness implications

M0 is exit-eligible only when:

- canonical contracts and decisions are materialized
- the Safety Kernel is executable
- all CRITICAL scenarios pass
- required scenarios pass or have an explicitly accepted non-safety blocker
- the run records revision/configuration identity
- no architecture blocker remains for M1

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
