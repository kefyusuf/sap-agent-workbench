# ADR-008 — SAP Technical Architect Agent Boundary

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D087 through SAP-AW-D094
- **Scope:** M1 Technical Architect

## Context

M0 established the generic Agent/Skill/Workflow/Policy/Tool/Knowledge boundaries but did not define any concrete SAP Agent.

M1 introduces the first product Agent. Its boundary must remain small enough to avoid becoming a generic SAP super-agent
while still covering requirement-to-architecture reasoning.

## Decision

### SAP-AW-D087

The SAP Technical Architect Agent is a bounded architecture-reasoning owner.

It converts requirements plus resolved context/evidence into technical architecture assessments and proposals.

### SAP-AW-D088

The Agent receives task-scoped resolved context rather than unrestricted access to all available Knowledge.

The M0 least-context and provenance rules remain unchanged.

### SAP-AW-D089

The Agent follows existing-solution discovery before proposing new custom development.

It explicitly considers relevant standard/configuration/existing implementation/extension/API options before new custom code.

### SAP-AW-D090

The Agent output separates verified/known facts, inferences, assumptions, unknowns, conflicts, alternatives, rationale,
risks, and required verification.

An architecture proposal is not itself a verified system fact.

### SAP-AW-D091

System-specific SAP object identifiers cannot be asserted as verified without supporting project/system evidence.

Plausible generic mechanisms may be proposed only with the appropriate non-verified classification.

### SAP-AW-D092

The Agent does not own implementation, final architecture approval, deployment, transport, administration,
or production mutation.

### SAP-AW-D093

A material unknown or conflict that changes the architecture decision must surface as `NEEDS_CLARIFICATION` or `BLOCKED`
rather than being silently filled by model background knowledge.

### SAP-AW-D094

M1 introduces no SAP-system WRITE, DEPLOY, TRANSPORT, or ADMIN capability.

The first M1 slice may be evaluated entirely with synthetic/anonymized context before any live SAP adapter is introduced.

## Consequences

- The first concrete Agent remains compatible with the M0 safety kernel.
- Architecture reasoning can be tested before SAP connectivity exists.
- Hallucinated Z-object/system-state claims become an explicit evaluation target.
- Coding/implementation remains a separate later responsibility.
- M1 can progress on a stacked child branch while M0 merge waits for remote CI capacity.

## Verification / fitness implications

M1 evaluation must eventually demonstrate that the Agent:

- exposes material unknowns/conflicts
- does not invent verified system-specific objects
- considers reuse/existing-solution paths before custom development
- separates proposal from evidence
- stays within the READ/QUERY/ANALYZE/PROPOSE boundary
- produces a handoff suitable for later implementation/review workflows

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
