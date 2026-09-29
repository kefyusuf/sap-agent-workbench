# ADR-002 — Component Responsibility Model

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D010 through SAP-AW-D020
- **Scope:** M0 Foundation

## Context

SAP domains contain many narrow topics such as BAdI, SmartForms, OData, CDS, RAP, ATC, transports, and integration.
Representing each topic as an autonomous Agent would produce agent proliferation, unclear ownership, and accidental
privilege paths.

The foundation therefore needs a stable rule for deciding what is an Agent, Skill, Workflow, Policy, Tool, or Knowledge Pack.

## Decision

### SAP-AW-D010

An Agent is a bounded reasoning owner, not a generic capability container.

### SAP-AW-D011

Repeatable domain expertise is represented as a Skill.

Examples include BAdI analysis, ABAP OO review, RAP design, or OData troubleshooting.

### SAP-AW-D012

Multi-step process coordination belongs to Workflows.

Workflows own sequence, gates, handoffs, and completion conditions.

### SAP-AW-D013

Authorization and safety constraints belong to enforceable Policies.

Policy is not advisory prompt text.

### SAP-AW-D014

External-system capabilities are exposed through Tools.

Tool identity does not itself grant authorization.

### SAP-AW-D015

Knowledge is a first-class component separate from Skills.

Facts/reference material and reusable expertise must not be conflated.

### SAP-AW-D016

Agents do not directly create arbitrary Workflows or invoke unrestricted Tools.

Delegation and external-action requests pass through controlled runtime boundaries.

### SAP-AW-D017

Tool execution passes through capability resolution and policy evaluation.

Canonical external-action path:

Agent
→ Action Intent
→ Orchestrator
→ Capability Resolver
→ Policy Engine
→ Tool Runtime

### SAP-AW-D018

Customization may extend behavior but may not weaken inherited safety boundaries.

### SAP-AW-D019

Component lifecycle and work-item lifecycle are separate concepts.

Component lifecycle may include DRAFT, REVIEWED, ACTIVE, DEPRECATED, and RETIRED.
Work-item lifecycle begins with PROPOSED, READY, IN_PROGRESS, VERIFYING, and DONE.

### SAP-AW-D020

Creating a new Agent requires justification that the capability owns a distinct bounded reasoning responsibility.

A new SAP topic alone is insufficient justification.

## Consequences

- BAdI, SmartForms, CDS, RAP, and similar narrow expertise default to Skills rather than Agents.
- Workflows remain inspectable and deterministic around stage ordering.
- Policy and tool enforcement stay outside model discretion.
- Agent count can remain small while expertise grows through Skills and Knowledge Packs.
- Future custom Agents remain possible where there is a genuine reasoning boundary.

## Verification / fitness implications

Foundation fitness must prove that:

- Skills cannot grant authorization
- Agents cannot bypass the orchestrator/policy path for unrestricted tools
- Knowledge content cannot become executable policy merely by containing imperative text
- mandatory Workflow gates remain controlled by Workflow/Policy contracts

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
