# Foundation Fitness Fixtures

This directory materializes deterministic M0 architecture fitness scenarios.

## Scope

These fixtures validate foundation semantics, not SAP domain reasoning quality.

The fixture serialization is an **internal M0 test format**, not a public product manifest contract.
It may evolve with the runner as long as scenario meaning and stable scenario IDs remain traceable.

## Result model

Each scenario expects one of:

- PASS
- FAIL
- BLOCKED
- NOT_APPLICABLE

Critical scenarios must PASS before M0 can close.

## Fixture structure

Each JSON fixture contains:

- `id` — stable scenario identity
- `revision` — fixture revision
- `criticality` — CRITICAL / REQUIRED / ADVISORY
- `category` — foundation area
- `kind` — deterministic runner handler
- `title` — human-readable invariant
- `given` — input state
- `when` — deterministic operation under test
- `then` — expected result
- `invariant` — canonical rule being protected
- `decision_refs` — architecture decisions supporting the scenario

## Safety Kernel

The initial Safety Kernel contains 12 CRITICAL scenarios:

- FIT-001 Agent cannot bypass policy
- FIT-002 More restrictive policy wins
- FIT-003 Project cannot weaken organization safety
- FIT-004 Unknown target blocks side effects
- FIT-005 Model output is not system evidence
- FIT-006 VERIFIED claim requires supporting evidence
- FIT-007 Stale evidence cannot verify a new revision
- FIT-008 Approval is bound to exact action fingerprint
- FIT-009 Approval cannot override MUST_NOT_PROCEED
- FIT-010 Mandatory verification cannot be customized away
- FIT-011 Protected fields cannot be overridden
- FIT-012 MVP exposes no SAP mutation capabilities

The runner must treat scenario IDs and expected semantics as authoritative test inputs.
