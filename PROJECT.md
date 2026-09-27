# SAP Agent Workbench — Project Charter

## Status

M0 — Foundation / Pre-Implementation

## Purpose

Build a provider-independent SAP engineering agent workbench that helps technical consultants
turn business requirements into safe, traceable, evidence-aware technical outcomes.

The system is not a generic coding assistant and is not an autonomous SAP administrator.

Primary lifecycle:

Business Requirement
→ Context Discovery
→ Technical Analysis
→ Architecture Decision
→ Implementation Proposal
→ Verification
→ Human Approval where required
→ Delivery

## Primary users

- SAP Technical Consultant
- SAP ABAP Developer
- SAP BTP Consultant
- SAP Integration Consultant
- SAP Technical Architect

Future users may include functional consultants, QA/test engineers, Basis/operations, and support teams.

## Core outcomes

The system should support:

1. Business requirement analysis
2. Functional-to-technical translation
3. SAP solution option analysis
4. Existing-solution discovery and reuse
5. ABAP development assistance
6. S/4HANA modernization analysis
7. BTP and integration design
8. Fiori/OData technical analysis
9. Incident and root-cause analysis
10. Code and solution review
11. Test scenario generation
12. Technical documentation
13. Decision provenance
14. Evidence-based verification

## Product principle

AI recommendation != verified SAP system fact.

The system provides decision support and engineering assistance.
Material system changes remain governed by explicit capability, policy, approval, and verification boundaries.

## Initial SAP scope

### Development

- ABAP
- ABAP OO
- DDIC
- BAPI
- BAdI
- User/Customer Exits
- Enhancement Points
- Adobe Forms
- SmartForms

### Modern SAP

- S/4HANA
- RISE with SAP
- Clean Core
- Custom-code modernization
- CDS
- RAP
- ABAP Cloud

### SAP BTP

- SAP BTP
- CAP
- Node.js
- Business Application Studio
- Build Process Automation
- Cloud Connector

### Integration

- REST
- SOAP
- OData
- RFC
- IDoc
- Integration Suite
- API Management
- Kafka
- Event-driven integration

### UI

- Fiori
- UI5
- Fiori extensions
- OData-backed applications

### Functional context

Initial context packs may include SD, MM, PP, FI, CO, HR, QM, EWM, IS-U, and CRM.
These begin as technical-context support, not autonomous functional consulting.

## Non-goals

The initial system will not:

- autonomously modify production SAP systems
- import transports autonomously
- perform unrestricted database writes
- modify users or authorizations autonomously
- replace SAP functional or technical consultants
- treat model-generated information as system truth
- invent SAP object names as verified facts
- bind architecture to one LLM provider
- inject all SAP knowledge into every task

## Architecture principles

1. **Provider independent** — SAP responsibilities define agents; providers are adapters.
2. **Domain first** — component boundaries follow engineering responsibilities, not model brands.
3. **Reuse before create** — inspect standard SAP, configuration, existing customizations, released APIs,
   reusable internal components, and only then propose new custom development.
4. **Evidence before authority** — distinguish VERIFIED, KNOWN, INFERRED, ASSUMED, UNKNOWN, and CONFLICTING.
5. **Human-controlled material changes** — analysis may automate; side effects remain governed.
6. **Least context** — provide only task-relevant context.
7. **Customization outside core** — company, landscape, project, team, and user knowledge remain overlays.
8. **Workflow over agent proliferation** — prefer Skill, Workflow, Policy, Tool, or Knowledge before adding a new Agent.
9. **Completion is evidence-bound** — output generation alone is not DONE.

## Component model

The platform distinguishes:

- Agent — bounded reasoning owner
- Skill — reusable expertise
- Workflow — ordered coordination and gates
- Policy — enforceable permission/safety rule
- Tool — external capability
- Knowledge Pack — facts and references

## Customization hierarchy

Core
→ SAP Domain Pack
→ Organization
→ Landscape
→ Project
→ Team
→ User
→ Task

Context may become more specific down the hierarchy.
Policies may only become more restrictive.

## Initial capability boundary

Initial runtime capability classes:

READ
QUERY
ANALYZE
PROPOSE

The MVP does not register SAP-system capabilities for:

WRITE
DEPLOY
TRANSPORT
ADMIN

## Decision boundary

Material actions resolve to one of:

- AUTO_EXECUTE
- EXECUTE_AND_RECORD
- REQUEST_APPROVAL
- MUST_NOT_PROCEED

The most restrictive applicable policy wins.

## Verification principle

A task is not complete merely because an LLM produced output.
Verification must be appropriate to the task and may include source inspection, static analysis,
tests, API responses, logs, human review, or verified system evidence.

## Initial agents

Primary:

- SAP Technical Architect
- SAP Developer
- SAP Troubleshooter

Verification:

- SAP Reviewer
- SAP Test Engineer

Specialist capabilities should be introduced progressively and only when they own a bounded reasoning responsibility.

## First workflow

Requirement
→ Context Discovery
→ Architecture Proposal
→ Human Approval where required
→ Implementation Proposal
→ Review
→ Test Plan / Verification

## M0 success

M0 is complete only when the architecture is:

- defined
- internally consistent
- testable
- reproducible
- safe to implement

No unresolved foundation blocker may remain before M1.
