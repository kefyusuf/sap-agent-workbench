# Workflow Contract

## Definition

A Workflow defines the ordered coordination of work.

It owns:

- sequence
- dependencies
- gates
- handoffs
- required approvals
- required verification
- completion conditions

It does not own SAP domain reasoning.

## Base work-item lifecycle

PROPOSED
→ READY
→ IN_PROGRESS
→ VERIFYING
→ DONE

Supporting states may include BLOCKED, FAILED, and CANCELLED.

Gate status should not create unnecessary lifecycle-state explosion.

## Actors

Workflow steps may delegate to:

- Agents
- Skills
- deterministic runtime checks
- approval gates
- verification checks

## Extension points

Base workflows may declare named hooks such as:

- after_intake
- after_context
- before_architecture_decision
- after_architecture_decision
- before_verification
- before_completion

Customization may extend only declared hooks.

## Mandatory steps

A base workflow may mark safety- or verification-critical steps as mandatory.
Lower-level customization may not remove or disable them.

## Completion

The Workflow defines sufficient evidence for DONE.
An Agent or successful Tool call cannot independently declare completion.
