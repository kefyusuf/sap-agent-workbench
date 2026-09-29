# Customization & Extension Model

## Goal

Keep the core and SAP domain packs reusable while allowing organization-, landscape-, project-, team-,
user-, and task-specific behavior without forking the core.

## Layer order

Core
→ SAP Domain Pack
→ Organization
→ Landscape
→ Project
→ Team
→ User
→ Task

This is not a universal "last one wins" override chain.
Resolution semantics depend on component type.

## Namespaces

Suggested namespaces:

- core.*
- sap.*
- org.*
- landscape.*
- project.*
- team.*
- user.*
- task.*

Component identity is namespace + stable component id.

## Customization operations

Initial operations:

- ADD
- EXTEND
- REPLACE
- RESTRICT
- DISABLE

REPLACE is not a general-purpose override.
It is allowed only on explicitly replaceable fields.

## Protected fields

Customization cannot replace or disable core safety invariants, including:

- component identity/kind
- policy evaluation semantics
- approval binding rules
- provenance requirements
- evidence semantics
- capability enforcement boundaries

Changing these requires a new compatible core contract/version.

## Agents

Agents should be extended through declared overlays rather than copied and forked.

Typical extensible fields:

- terminology
- preferred architectural patterns
- output format
- additional review checklists
- additional skills
- required organization/project knowledge

Reasoning responsibility, policy boundaries, evidence obligations, and prohibited responsibilities are protected.

## Skills

Skills may be composed with organization and project expertise.

Resolved skill composition must remain visible and attributable.

## Workflows

Workflow customization uses declared extension points.

Mandatory steps such as policy evaluation or required verification cannot be removed by lower-level customization.

## Policies

Policy customization is monotonic toward restriction:

AUTO_EXECUTE
→ EXECUTE_AND_RECORD
→ REQUEST_APPROVAL
→ MUST_NOT_PROCEED

Lower layers cannot move in the opposite direction.

## Tools

Customize tools through adapter registration rather than silent replacement.

Capability identity is stable; provider/adapter implementation may vary.

## Knowledge

Knowledge accumulates with scope, authority, freshness, revision, and conflict detection.

New knowledge revisions supersede old revisions without destructive deletion.
More-specific facts may shadow less-specific facts while preserving provenance.

## Resolution outcomes

A resolver may produce:

- RESOLVED
- RESOLVED_WITH_SHADOWING
- RESOLVED_WITH_WARNINGS
- CONFLICT
- INCOMPATIBLE
- INVALID

Material security, target, transport, or capability conflicts fail closed.

## Compatibility

Customization packs declare compatibility with:

- core contract/version
- required SAP domain packs
- dependent component contracts

Content version and contract version are separate concepts.

## Customization pack

A logical pack may contain:

- manifest
- agents/
- skills/
- workflows/
- policies/
- knowledge/
- landscape/
- tests/

Packs are validated before activation.

Possible lifecycle states:

INSTALLED
→ VALIDATED
→ ENABLED
→ ACTIVE

Additional states may include DISABLED, INCOMPATIBLE, and QUARANTINED.

## Private customization

Organization and project intelligence may live in a separate private repository without forking the core.

The private repository may contain configuration and credential references, but never raw secrets.

## Configuration fingerprint

The resolved runtime configuration receives a deterministic semantic fingerprint derived from relevant:

- core version
- domain pack versions
- active customization pack versions
- active policy set
- workflow extensions
- agent overlays

This allows work products and evaluations to record the exact configuration that produced them.
