# Tool Contract

## Definition

A Tool is an external capability adapter.

Examples may eventually include SAP ADT, ATC, abapGit, BTP APIs, Integration Suite APIs,
Git, ticket systems, or documentation systems.

## Tool identity vs capability

Authorization is based on explicit operations, not tool names.

A tool may expose one or more capability descriptors.
No capability is implied merely by selecting an adapter.

## Invocation path

Agent
→ Action Intent
→ Orchestrator
→ Capability Resolver
→ Policy Engine
→ Tool Runtime

Direct unrestricted Agent-to-Tool privilege paths are forbidden.

## Side effects

Each tool operation must declare:

- capability verb
- resource kind
- target
- mutation characteristics
- evidence it can produce
- authentication requirement
- relevant preconditions

## Secrets

Tools may use runtime credentials through secret-management facilities.

Raw credentials must never be injected into general Agent context or customization content.

## MVP

SAP-system Tool operations are limited to READ, QUERY, ANALYZE, and PROPOSE capabilities.
