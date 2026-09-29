# Component Model

## Core distinction

| Component | Question it answers |
|---|---|
| Agent | Who owns the bounded reasoning responsibility? |
| Skill | What reusable expertise is applied? |
| Workflow | In what sequence is work performed? |
| Policy | What is allowed, restricted, or denied? |
| Tool | What can interact with the outside world? |
| Knowledge Pack | What facts or references are available? |

## Agent

An Agent owns bounded reasoning responsibility.

An Agent may interpret a task, identify missing information, evaluate alternatives, select relevant skills,
assess evidence, and produce recommendations.

An Agent must not:

- change policy
- bypass policy
- grant itself tool privileges
- silently promote model output to verified system fact
- directly create arbitrary workflows
- directly invoke unrestricted tools

Cross-agent delegation is requested through the orchestrator.

## Skill

A Skill is reusable domain expertise. It should be as stateless as practical.

Examples:

- BAdI analysis
- ABAP OO review
- RAP design
- OData troubleshooting
- Kafka integration
- SmartForms guidance

A Skill is not an authorization boundary, workflow engine, or long-lived autonomous actor.

## Workflow

A Workflow coordinates stages, dependencies, checkpoints, approvals, handoffs, and completion conditions.

A Workflow does not own SAP domain reasoning.
It delegates bounded reasoning to Agents and reusable expertise to Skills.

Base work-item lifecycle:

PROPOSED
→ READY
→ IN_PROGRESS
→ VERIFYING
→ DONE

Additional terminal or blocking states may include BLOCKED, FAILED, and CANCELLED.

## Policy

A Policy is an enforceable rule.
It is not advisory prompt text.

Canonical decisions:

AUTO_EXECUTE
< EXECUTE_AND_RECORD
< REQUEST_APPROVAL
< MUST_NOT_PROCEED

When multiple applicable policies exist, the most restrictive decision wins.

## Tool

A Tool exposes external capabilities.

Agents request capabilities; they do not receive unrestricted tool authority.
Tool execution is mediated by capability resolution and policy evaluation.

## Knowledge Pack

A Knowledge Pack contains facts or references.
It is distinct from a Skill.

Example:

- SAP Clean Core documentation = knowledge
- evaluating a design against Clean Core = skill

## Dependency rules

Preferred direction:

Workflow
→ Agent
→ Skill
→ Knowledge

External action path:

Agent
→ Action Intent
→ Orchestrator
→ Capability Resolver
→ Policy Engine
→ Tool Runtime

An Agent may request delegation to another Agent, but direct uncontrolled Agent-to-Agent invocation is not a privilege path.

## New-component selection rule

Create an:

- Agent when a capability owns bounded reasoning responsibility
- Skill when it is repeatable expertise
- Workflow when it coordinates multiple stages
- Policy when it governs allow/restrict/deny behavior
- Tool when it interacts with an external system
- Knowledge Pack when it provides facts/reference material

A new SAP topic does not automatically justify a new Agent.
