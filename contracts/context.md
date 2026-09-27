# Context Contract

## Definition

Context is the task-scoped subset of available knowledge, evidence, constraints, and workflow state
actually supplied to reasoning.

## Principle

available knowledge != injected context

Context should be selected by relevance, authority, scope, freshness, and task dependency.

## Context layers

Potential layers include:

- task
- workflow
- SAP domain
- organization
- landscape
- project
- team/user
- retrieved knowledge
- live evidence

## Required metadata

Material context items preserve:

- source
- authority
- scope
- freshness
- revision
- provenance

## Resolution

More-specific facts may shadow less-specific facts for the same claim scope,
while preserving the shadowed source in provenance.

Policy is not context and cannot be overridden by a more-specific fact.

## Conflict

Material conflicts produce CONFLICTING context and require explicit resolution or verification.
They are not silently reconciled by the model.
