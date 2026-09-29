# ADR-004 — Capability, Policy & Approval

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D035 through SAP-AW-D050
- **Scope:** M0 Foundation

## Context

A simple READ/WRITE permission model is insufficient for SAP automation.

Writing a local artifact and changing production business data are not equivalent. Authorization must account for
the requested action, resource, target environment, relevant parameters, risk characteristics, and the exact action
that a human approved.

## Decision

### SAP-AW-D035

Capabilities are evaluated as **action + resource + target**, not as standalone verbs.

### SAP-AW-D036

Capabilities do not implicitly inherit other capabilities.

WRITE does not imply READ; ADMIN does not imply unrestricted access; TRANSPORT does not imply arbitrary WRITE.

### SAP-AW-D037

Tool identity does not determine authorization.

Individual Tool operations expose explicit capability descriptors.

### SAP-AW-D038

Agents request material external actions through Action Intents.

### SAP-AW-D039

Material Action Intents receive deterministic semantic fingerprints used for approval and execution validation.

Fingerprint-significant changes produce a different action.

### SAP-AW-D040

Risk is represented through explicit dimensions rather than a synthetic numeric score.

Initial dimensions include mutation, environment, blast radius, reversibility, privilege, data sensitivity,
external effect, and automation scope.

### SAP-AW-D041

Policy decisions are ordered:

AUTO_EXECUTE
< EXECUTE_AND_RECORD
< REQUEST_APPROVAL
< MUST_NOT_PROCEED

### SAP-AW-D042

When multiple Policies apply, the most restrictive decision wins.

### SAP-AW-D043

Capability availability and Policy authorization are separate.

An unavailable capability is not represented as a Policy denial.

### SAP-AW-D044

Insufficient or conflicting material Policy context prevents side-effecting execution.

### SAP-AW-D045

Approvals are action-, target-, scope-, parameter-, and revision/precondition-bound.

### SAP-AW-D046

Approval cannot override MUST_NOT_PROCEED.

### SAP-AW-D047

Material changes to an approved action invalidate the approval.

### SAP-AW-D048

Policy and Action fingerprint validity are re-evaluated immediately before side-effecting execution.

### SAP-AW-D049

Tool execution success is not equivalent to Workflow completion.

### SAP-AW-D050

The initial MVP registers no SAP-system WRITE, DEPLOY, TRANSPORT, or ADMIN capabilities.

## Consequences

- Authorization is evaluated per operation instead of per adapter/tool name.
- Approval becomes an auditable record rather than a conversational yes/no.
- Future mutation support requires preflight and revalidation to reduce time-of-check/time-of-use drift.
- The MVP has a hard capability boundary in addition to Policy enforcement.
- Side-effecting capability implementation is intentionally deferred beyond M0.

## Verification / fitness implications

Foundation fitness must prove that:

- the most restrictive applicable Policy wins
- project customization cannot weaken organization safety
- unknown/conflicting targets block side effects
- approval for one fingerprint cannot be replayed for a different material action
- human approval cannot defeat MUST_NOT_PROCEED
- no SAP mutation capability is exposed by the MVP

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
