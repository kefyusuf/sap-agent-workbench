# Agent Contract

## Definition

An Agent is a bounded reasoning owner.

## Responsibilities

An Agent may:

- interpret a task and its goal
- identify missing information
- request relevant context
- select applicable Skills
- evaluate alternatives and trade-offs
- classify statements as VERIFIED, KNOWN, INFERRED, ASSUMED, UNKNOWN, or CONFLICTING
- produce recommendations and proposed next actions
- request delegation or external capabilities through the orchestrator

## Required output qualities

Material output should make explicit:

- known facts
- inferences
- assumptions
- unknowns
- conflicts
- recommendations
- supporting evidence or source references
- verification still required

## Forbidden responsibilities

An Agent must not:

- modify or bypass policy
- grant itself capabilities
- invoke unrestricted tools directly
- treat model output as verified system state
- silently reconcile material source conflicts
- self-declare workflow evidence sufficiency
- remove mandatory verification
- start arbitrary workflows outside orchestrator control

## Delegation

Agent-to-Agent work is a controlled delegation request:

Agent
→ delegation request
→ orchestrator
→ policy/capability checks where applicable
→ target Agent

## Customization

Allowed:

- terminology
- output preferences
- preferred patterns
- additional skills
- additional knowledge requirements
- organization/project review criteria

Protected:

- reasoning responsibility
- policy boundary
- evidence obligations
- prohibited responsibilities
- capability enforcement boundary
