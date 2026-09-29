# ADR-001 — Product & Safety Boundary

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D001 through SAP-AW-D009
- **Scope:** M0 Foundation

## Context

The project began from a SAP/ABAP consulting use case, but the intended system spans requirement analysis,
S/4HANA modernization, BTP, integration, Fiori/OData, implementation guidance, review, testing, and incident analysis.

A narrow "ABAP code generator" framing would make later architecture, safety, customization, and verification concerns
secondary. The foundation therefore needs an explicit product boundary before any agent implementation starts.

## Decision

### SAP-AW-D001

The product is a SAP engineering workbench, not an ABAP coding assistant.

Its primary lifecycle is:

Business Requirement
→ Context Discovery
→ Technical Analysis
→ Architecture Decision
→ Implementation Proposal
→ Verification
→ Human Approval where required
→ Delivery

### SAP-AW-D002

The architecture is LLM-provider independent.

Agents are defined by SAP engineering responsibilities, not provider or model names.
Providers are adapters behind stable domain contracts.

### SAP-AW-D003

Agent, Skill, Workflow, Policy, Tool, and Knowledge are distinct concepts with distinct responsibilities.

They must not be collapsed into one generic "agent" abstraction.

### SAP-AW-D004

Organization-, landscape-, project-, team-, and user-specific information lives outside the reusable core
through explicit customization layers.

### SAP-AW-D005

The initial product does not autonomously mutate production SAP systems.

The MVP does not register SAP-system WRITE, DEPLOY, TRANSPORT, or ADMIN capabilities.

### SAP-AW-D006

Model output is not treated as verified SAP system fact.

Material factual claims require appropriate source/evidence classification.

### SAP-AW-D007

The system follows **reuse before create**.

Before proposing new custom development, it should consider relevant SAP standard capability, configuration,
existing internal implementation, released extension/API options, and reusable company components.

### SAP-AW-D008

The system follows **least context**.

Available knowledge is not automatically injected into every task.

### SAP-AW-D009

Task completion is verification-based rather than output-based.

Generating an answer, patch, or code artifact is not sufficient to make a workflow DONE.

## Consequences

- M0 concentrates on contracts, safety boundaries, provenance, and deterministic fitness before SAP agent prompts.
- Provider-specific behavior must remain behind adapters.
- Company-specific SAP intelligence can evolve independently from the core.
- Mutation support, if introduced later, requires an explicit design gate.
- Verification becomes part of workflow semantics rather than an optional review step.

## Verification / fitness implications

At minimum, foundation fitness must prove that:

- mutation capabilities are unavailable in the MVP
- model output cannot become verified system evidence by assertion
- mandatory verification cannot be bypassed by task/user customization
- provider changes cannot alter deterministic safety invariants

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
