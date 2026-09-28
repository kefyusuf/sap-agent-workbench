# ADR-021 — Reviewer & Test Engineer Evaluation Model

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D205 through SAP-AW-D213
- **Scope:** M3 Review & Verification

## Context

Review and test-plan quality allow multiple valid formulations, so exact prose matching is unsuitable.

Hard boundaries such as architecture fidelity, verification honesty, requirement coverage, and no-mutation behavior still need explicit evaluation rules.

## Decision

### SAP-AW-D205

M3 evaluation is property-based rather than exact-prose or exact-test-name matching.

### SAP-AW-D206

Reviewer and Test Engineer fixtures are evaluated independently even when a later workflow composes them.

### SAP-AW-D207

Reviewer evaluation explicitly checks architecture fidelity, finding traceability, outcome consistency, and verification honesty.

### SAP-AW-D208

REVIEW_ACCEPTABLE with a case-defined material architecture violation or unresolved blocking finding is a CRITICAL failure.

### SAP-AW-D209

Test Engineer evaluation explicitly checks requirement/risk/finding coverage and traceable planned evidence.

### SAP-AW-D210

A case-defined critical requirement must have verification coverage or an explicit justified exclusion.

### SAP-AW-D211

False compile/ATC/test/runtime PASS/FAIL without evidence is a CRITICAL failure for both review and test contexts.

### SAP-AW-D212

Initial M3 fixtures are synthetic/anonymized and require no provider, SAP connection, compiler, ATC, or test execution.

### SAP-AW-D213

Model-assisted grading may later supplement semantic quality review but cannot be the sole oracle for CRITICAL M3 boundaries.

## Consequences

- review and verification planning remain provider-independent
- multiple useful review/test-plan styles are acceptable
- hard safety/evidence boundaries stay deterministic where possible
- M3 design can progress while parent runtime verification remains pending

## Verification / fitness implications

The initial fixture set must include positive and negative review cases and at least one test-plan case that demonstrates
requirement traceability without falsely claiming execution.

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
