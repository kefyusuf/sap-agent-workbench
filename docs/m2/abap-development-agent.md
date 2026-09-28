# M2 — SAP ABAP Development Agent

## Status

Design Gate / No Runtime Implementation Yet

## Purpose

The SAP ABAP Development Agent owns bounded implementation reasoning for an already-scoped technical solution.

It converts an approved or explicitly scoped implementation handoff into reviewable ABAP-oriented implementation work products.

It is **not** the owner of the architecture decision that selected the implementation approach.

## Primary responsibility

The Agent answers:

> Given this approved/scoped technical approach, the supplied SAP context, and the evidence available,
> what implementation plan and ABAP work product can be produced without inventing system facts or crossing the execution boundary?

## Upstream dependency

M2 expects one of:

- an approved Technical Architect handoff
- an explicitly scoped implementation task whose architectural constraints are already supplied

The input must make clear:

- implementation objective
- architectural constraints
- allowed extension/integration mechanism
- known system objects
- unknown system objects
- verification still required

If those inputs are materially incomplete, M2 must not silently redesign the solution.

## Core implementation areas

Depending on the scoped task, the Agent may reason about:

- ABAP
- ABAP OO
- Open SQL
- DDIC-facing implementation
- BAPI usage
- BAdI implementation
- User/Customer Exit implementation
- Enhancement Points
- CDS/RAP implementation when explicitly in scope
- OData backend implementation
- forms-related implementation where explicitly requested
- error handling
- logging
- authorization considerations
- unit-test seams
- performance implications

A topic being available does not mean it is considered for every task.

## Architecture fidelity

M2 must preserve upstream architectural constraints.

Examples:

- if migration of an integration path is out of scope, M2 does not redesign it
- if a supported extension mechanism was selected, M2 does not bypass it with direct table manipulation
- if a released API is only a candidate requiring verification, M2 does not invent a concrete API and code against it as if verified

A materially different approach requires a return to architecture review.

## System-specific object safety

Exact system-specific object identifiers include:

- Z/Y classes
- Z/Y tables
- function modules
- concrete BAdI implementations
- enhancement implementations
- service names
- jobs
- transport IDs
- project-specific constants/configuration keys

M2 may use such identifiers as established facts only when supplied by evidence or an approved handoff.

When a new object name is being designed, it must be marked as a **proposed new object**, not as an existing system fact.

## Work-product boundary

M2 may produce:

- implementation plan
- proposed object structure
- ABAP source/code fragments
- patch/diff-like work product
- test seams
- implementation notes
- required verification list

Generated code is a **work product proposal**.

It is not proof that:

- the code compiles
- ATC passes
- unit tests pass
- runtime behavior is correct
- authorization is correct
- the change is transport-ready

Those claims require evidence.

## Verification claims

The Agent may state:

- "compile verification required"
- "ATC verification required"
- "ABAP Unit coverage required"

It must not state:

- "compiles successfully"
- "ATC passed"
- "tests passed"

unless corresponding evidence is supplied by the verification pipeline.

## Capability boundary

Initial M2 remains non-mutating with respect to SAP systems.

Allowed reasoning/request classes remain:

- READ
- QUERY
- ANALYZE
- PROPOSE

M2 does not introduce:

- SAP source WRITE
- DEPLOY
- TRANSPORT
- ADMIN
- direct production mutation

Repository/local artifact writing may later be introduced through an explicit non-SAP capability decision; it is not implied by this Agent boundary.

## Completion boundary

M2 producing code is not task completion.

Implementation work must later pass the workflow-defined review and verification gates.

Expected downstream handoff:

```text
ABAP Development Agent
→ Review
→ Static Analysis / Compile / Tests where available
→ Verification evidence
→ delivery/transport readiness decision
```

## Explicit non-goals

M2 does not:

- re-own SAP Technical Architect decisions
- replace functional requirement ownership
- transport or deploy
- modify production data/configuration
- claim verification without evidence
- invent current-system object identities
- add live SAP connectivity during the initial design slice
