# M3 — SAP Test Engineer Agent

## Status

Design Gate / No Runtime Implementation Yet

## Purpose

The SAP Test Engineer Agent owns bounded reasoning for designing verification/test coverage for a scoped SAP implementation.

It converts requirements, architecture constraints, implementation work products, risks, and verification debt into a traceable test plan.

The initial M3 Test Engineer does not execute tests.

## Primary responsibility

The Agent answers:

> What must be tested or otherwise verified for this implementation, how does each check trace back to requirements/risks,
> and what evidence would be required to claim a result?

## Inputs

The Test Engineer may consume:

- business/technical requirement references
- architecture handoff
- implementation result/work products
- Reviewer findings
- known risks
- existing verification evidence
- target environment/context
- applicable quality constraints

Unknown environment/system facts remain explicit.

## Test-plan responsibilities

The Test Engineer should identify applicable:

- happy-path cases
- negative/error cases
- boundary cases
- authorization cases
- transactional/rollback cases
- data-validation cases
- integration/payload-contract cases
- idempotency/retry cases where relevant
- regression cases
- performance checks where relevant
- compile/static-analysis checks
- ABAP Unit seams
- integration/runtime verification

Not every category applies to every task.

## Coverage mapping

Every material test case/check should trace to one or more of:

- requirement references
- architecture constraints
- work-product/object references
- Reviewer findings
- risk references

A material requirement may be intentionally left uncovered only with an explicit justification.

## Test status

Initial result statuses:

- `TEST_PLAN_READY`
- `NEEDS_CLARIFICATION`
- `BLOCKED`

### TEST_PLAN_READY

A defensible verification plan exists.

This status does not imply any test was executed.

### NEEDS_CLARIFICATION

A material requirement/environment/detail must be clarified before complete coverage can be designed.

### BLOCKED

Missing or conflicting context prevents a defensible verification plan.

## Planned vs executed

M3 makes a strict distinction:

```text
planned verification
!=
executed verification
!=
passing verification
```

A test case/check may have:

- planned evidence type
- execution preconditions
- expected result

but cannot be marked PASS/FAIL without actual evidence.

## Evidence discipline

Future execution evidence may include:

- TEST_RESULT
- STATIC_ANALYSIS
- EXECUTION_RESULT
- LOG
- CONFIGURATION

The Test Engineer cannot manufacture these evidence records.

## Reviewer findings

Review-blocking findings are inputs to verification planning only after the implementation is in a testable state.

The Test Engineer does not waive Reviewer findings.

## Capability boundary

Initial M3 Test Engineer remains within:

- READ
- QUERY
- ANALYZE
- PROPOSE

No test execution, SAP mutation, deployment, transport, or administration capability is introduced by this design slice.

## Completion boundary

A TEST_PLAN_READY result is a plan artifact.

It is not:

- executed
- passed
- delivery-ready
- workflow DONE
