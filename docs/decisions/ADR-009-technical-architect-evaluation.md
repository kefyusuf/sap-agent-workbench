# ADR-009 — Technical Architect Evaluation Model

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D095 through SAP-AW-D101
- **Scope:** M1 Technical Architect

## Context

The Technical Architect Agent cannot be validated by checking for one exact answer.
Architecture reasoning may produce multiple defensible options, but M1 still needs hard boundaries against
unsupported system claims, conflict suppression, and capability violations.

The evaluation model must therefore separate deterministic boundary checks from semantic quality review.

## Decision

### SAP-AW-D095

M1 Agent evaluation is property-based rather than exact-prose matching.

Fixtures define required and prohibited behaviors.

### SAP-AW-D096

The first M1 evaluation set uses synthetic/anonymized cases and requires no live SAP access or private company data.

### SAP-AW-D097

Critical evaluation failures cannot be offset by aggregate scoring.

Zero CRITICAL failures is required for M1 acceptance.

### SAP-AW-D098

Unsupported system-specific SAP object claims are an explicit CRITICAL evaluation target.

### SAP-AW-D099

Material unknown/conflict handling is explicitly evaluated.

A case-defined material blocker must not be silently converted into a completed architecture recommendation.

### SAP-AW-D100

Existing-solution discovery / reuse-before-create behavior is explicitly evaluated where relevant to the case.

### SAP-AW-D101

Model-based grading may supplement M1 quality evaluation but cannot be the sole oracle for CRITICAL boundaries.

Deterministic assertions and/or explicit human review remain authoritative for those boundaries.

## Consequences

- The evaluation set can be reused across different providers.
- Wording diversity does not cause false failures.
- Hallucinated Z objects and silent conflict resolution become visible acceptance failures.
- Initial M1 development can proceed without SAP connectivity.
- Semantic architecture quality can later be compared across providers without coupling the core contract to a model.

## Verification / fitness implications

The first case set must include at least:

- insufficient system context / object-name hallucination pressure
- project-specific context shadowing a general organization default
- material source conflict
- modernization/clean-core reasoning from actual supplied evidence

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
