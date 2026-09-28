# ADR-015 — ABAP Development Agent Boundary

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D146 through SAP-AW-D156
- **Scope:** M2 ABAP Development Agent

## Context

M1 owns requirement-to-architecture reasoning.

The next Agent must implement a scoped solution without becoming a second architecture owner, inventing system-specific SAP objects,
or turning generated code into unearned verification evidence.

## Decision

### SAP-AW-D146

The SAP ABAP Development Agent is the bounded owner of implementation reasoning and implementation work products for an already-scoped technical solution.

### SAP-AW-D147

M2 requires an approved architecture handoff or an explicitly scoped implementation task with architectural constraints.

Materially missing architecture input prevents autonomous implementation selection.

### SAP-AW-D148

M2 preserves upstream architecture constraints.

A materially different implementation approach requires architecture re-review rather than silent deviation.

### SAP-AW-D149

System-specific existing SAP object identifiers require evidence or an approved handoff.

New object names may be proposed, but must remain explicitly classified as proposed new objects.

### SAP-AW-D150

Generated ABAP/source artifacts are work products, not verification evidence.

### SAP-AW-D151

Compile, ATC, test, runtime, authorization, and transport-readiness claims require corresponding verification evidence.

### SAP-AW-D152

M2 follows reuse-before-create within the approved architecture and must account for existing implementation/object context when supplied.

### SAP-AW-D153

Material implementation unknowns or conflicts produce `NEEDS_CLARIFICATION` or `BLOCKED` behavior rather than invented system facts.

### SAP-AW-D154

Initial M2 introduces no SAP-system WRITE, DEPLOY, TRANSPORT, or ADMIN capability.

### SAP-AW-D155

M2 work products are revision/provenance-bound and are not considered DONE until downstream review/verification requirements are satisfied.

### SAP-AW-D156

The initial M2 slice is evaluated with synthetic/anonymized implementation cases and requires no live SAP connection.

## Consequences

- Technical architecture and implementation ownership remain separate
- generated code can be useful without being mistaken for verified code
- false compile/ATC/test claims become explicit acceptance failures
- system-object hallucination remains a first-class safety concern
- M2 can be designed and evaluated while live SAP connectivity remains deferred
- later SAP source-write/transport support requires a separate capability design gate

## Verification / fitness implications

M2 evaluation must demonstrate that the Agent:

- preserves the supplied architectural approach
- does not invent existing system objects
- distinguishes proposed-new from existing object identity
- refuses to claim compile/ATC/test PASS without evidence
- does not request mutation/admin capabilities
- exposes material missing implementation facts
- produces a reviewable handoff rather than self-declaring DONE

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
