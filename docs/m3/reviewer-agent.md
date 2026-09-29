# M3 — SAP Reviewer Agent

## Status

Design Gate / No Runtime Implementation Yet

## Purpose

The SAP Reviewer Agent owns bounded reasoning for reviewing an implementation work product against:

- the approved architecture handoff
- scoped implementation requirements
- supplied object/context facts
- organization/project engineering constraints
- available verification evidence

It does not own implementation, deployment, transport, or final delivery approval.

## Primary responsibility

The Agent answers:

> Given this architecture handoff, implementation work product, and evidence snapshot, what review findings are supported,
> what must change, and what may proceed to verification?

## Inputs

The reviewer expects a revision-bound review snapshot containing:

- architecture handoff
- implementation result/work products
- requirement references
- existing/proposed object references
- assumptions and risks
- required verification
- evidence catalog
- applicable review standards/constraints

The reviewer must not silently retrieve or invent system facts that are absent from the supplied review context.

## Review dimensions

Depending on the task, review reasoning may cover:

- architecture fidelity
- requirement coverage
- existing-vs-proposed object identity
- ABAP correctness concerns
- error handling
- exception handling
- transactionality
- Open SQL / performance
- authorization/security considerations
- maintainability
- logging/observability
- test seams
- verification honesty
- upgrade / clean-core constraints where relevant

A dimension is applied only when material to the supplied task/context.

## Finding model

A review finding must identify:

- finding ID
- severity
- category
- statement
- affected work-product/object references
- supporting evidence/source references
- required action
- whether it blocks review acceptance

Initial severity values:

- `CRITICAL`
- `MAJOR`
- `MINOR`
- `INFO`

Severity is local to technical review and is not a substitute for Policy decisions.

## Review outcome

Initial outcomes:

- `REVIEW_ACCEPTABLE`
- `CHANGES_REQUIRED`
- `BLOCKED`

### REVIEW_ACCEPTABLE

No unresolved review-blocking finding remains.

This means only:

> the work product may proceed to the next verification stage.

It does **not** mean:

- compiled
- ATC-clean
- tests passed
- delivery-ready
- transport-ready
- approved for production

### CHANGES_REQUIRED

One or more supported review findings require implementation changes before verification can proceed.

### BLOCKED

The reviewer lacks material context/evidence required to produce a defensible review result.

## Architecture fidelity

A material architecture constraint cannot be waived by the Reviewer.

If the implementation violates an approved architecture constraint, the result cannot be `REVIEW_ACCEPTABLE`.

If the implementation requires a legitimate architecture change, the Reviewer returns it to architecture review.

## Verification honesty

The Reviewer evaluates verification claims against supplied evidence.

It must flag:

- compile PASS without compile/static-analysis evidence
- ATC PASS without ATC/static-analysis evidence
- test PASS without test evidence
- delivery/transport readiness without the required verification chain

Generated code or documentation is not verification evidence.

## Review vs implementation

The Reviewer may:

- identify defects
- explain remediation
- suggest a correction strategy

The Reviewer does not silently rewrite the implementation or mutate SAP/repository state.

A later workflow may hand findings back to the Development Agent.

## Capability boundary

Initial M3 Reviewer remains within:

- READ
- QUERY
- ANALYZE
- PROPOSE

It introduces no:

- SAP WRITE
- DEPLOY
- TRANSPORT
- ADMIN
- production mutation

## Completion boundary

A review result is evidence for the review stage only.

Workflow completion still requires downstream verification as defined by the workflow.
