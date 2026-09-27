# Capability Contract

## Definition

A capability instance is:

ACTION + RESOURCE + TARGET

## Verbs

- READ
- QUERY
- ANALYZE
- PROPOSE
- WRITE
- DEPLOY
- TRANSPORT
- ADMIN

No implicit inheritance exists among verbs.

## Descriptor

A material capability request should identify:

- verb
- resource kind
- resource identity/scope where applicable
- target system
- normalized environment
- relevant operation parameters

## Availability

Capability availability and policy authorization are independent.

An unavailable capability does not become a policy denial; it is unavailable.

## Risk

Risk classification may consider:

- mutation
- environment
- blast radius
- reversibility
- privilege
- data sensitivity
- external effect
- automation scope

No synthetic numeric score is required.

## MVP

The SAP runtime registers no WRITE, DEPLOY, TRANSPORT, or ADMIN system capabilities.
