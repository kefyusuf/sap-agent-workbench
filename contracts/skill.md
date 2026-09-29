# Skill Contract

## Definition

A Skill is reusable, scoped expertise applied by an Agent or Workflow.

Examples include BAdI analysis, ABAP OO review, RAP design, OData troubleshooting,
Kafka integration guidance, SmartForms, or Clean Core assessment.

## Characteristics

A Skill should:

- have a narrow purpose
- be reusable across tasks
- be as stateless as practical
- declare required knowledge/context
- declare expected inputs and outputs
- expose checks or invariants where useful

## A Skill is not

- an autonomous long-lived actor
- an authorization engine
- a workflow coordinator
- a tool runtime
- a secret store

## Composition

Skills may compose other Skills when:

- dependencies are explicit
- cycles are rejected
- resolved composition remains visible
- provenance is preserved

## Customization

Organization/project Skills may EXTEND a base Skill.
Silent replacement is not allowed unless a field is explicitly marked replaceable.

A resolved task should be able to report exactly which Skill versions were active.
