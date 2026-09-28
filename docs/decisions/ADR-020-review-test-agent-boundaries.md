# ADR-020 — Reviewer & Test Engineer Agent Boundaries

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D192 through SAP-AW-D204
- **Scope:** M3 Review & Verification

## Context

M2 produces reviewable implementation work products but explicitly does not own review acceptance or test planning.

The verification layer contains two different bounded reasoning responsibilities:

1. evaluate the implementation against architecture/quality/evidence constraints
2. design traceable verification coverage

Collapsing them into one generic verification Agent would blur review findings, test planning, and executed evidence.

## Decision

### SAP-AW-D192

The SAP Reviewer Agent is a distinct bounded reasoning owner for implementation review.

### SAP-AW-D193

The SAP Test Engineer Agent is a distinct bounded reasoning owner for test/verification-plan design.

### SAP-AW-D194

Reviewer and Test Engineer remain separate Agents rather than one generic verification Agent because their decision responsibilities and outputs differ.

### SAP-AW-D195

The Reviewer consumes a revision-bound architecture/implementation/evidence snapshot and does not silently retrieve or invent missing system facts.

### SAP-AW-D196

Reviewer outcomes are:

- REVIEW_ACCEPTABLE
- CHANGES_REQUIRED
- BLOCKED

REVIEW_ACCEPTABLE means ready to proceed to verification, not delivery-ready.

### SAP-AW-D197

A material architecture violation or unresolved review-blocking finding prevents REVIEW_ACCEPTABLE.

### SAP-AW-D198

The Reviewer cannot waive architecture constraints, fabricate verification evidence, or silently modify the reviewed work product.

### SAP-AW-D199

The Test Engineer produces a traceable verification plan mapped to requirements, constraints, risks, work products, and Reviewer findings where applicable.

### SAP-AW-D200

Test Engineer outcomes are:

- TEST_PLAN_READY
- NEEDS_CLARIFICATION
- BLOCKED

TEST_PLAN_READY means the plan is ready, not executed or passing.

### SAP-AW-D201

Planned verification, executed verification, and passing verification are distinct states.

M3 planning cannot create PASS/FAIL evidence.

### SAP-AW-D202

Material environment/system unknowns remain explicit and may block complete verification planning.

### SAP-AW-D203

Initial M3 introduces no test execution, SAP WRITE, DEPLOY, TRANSPORT, or ADMIN capability.

### SAP-AW-D204

Reviewer/Test artifacts remain workflow-stage outputs; neither Agent self-declares overall workflow DONE or production readiness.

## Consequences

- implementation review and test design stay independently inspectable
- false review acceptance and false test-pass claims become separate failure classes
- review findings can feed test planning without the Test Engineer waiving them
- later test execution tools can add evidence without changing planning semantics
- M3 can be designed without live SAP or provider integration

## Verification / fitness implications

Initial M3 cases must cover:

- architecture-preserving review outcome
- architecture-violating implementation review
- traceable verification plan for a scoped ABAP change
- no-evidence case where test PASS must not be invented

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
