# ADR-005 — Customization & Extension Resolution

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D051 through SAP-AW-D070
- **Scope:** M0 Foundation

## Context

The core should remain reusable and potentially publishable while real SAP landscapes require company-specific naming,
interfaces, Z objects, architecture standards, project decisions, and terminology.

Forking core Agents or silently overriding foundation behavior would make upgrades, provenance, and safety validation unreliable.
Customization therefore needs explicit identities, compatibility contracts, extension operations, and resolution semantics.

## Decision

### SAP-AW-D051

Customization uses explicit namespaces and stable component identities.

### SAP-AW-D052

Customization operations are:

- ADD
- EXTEND
- REPLACE
- RESTRICT
- DISABLE

Their availability is component- and field-specific.

### SAP-AW-D053

REPLACE is not a general override mechanism.

It is available only for fields explicitly declared replaceable.

### SAP-AW-D054

Core safety invariants and protected component fields cannot be replaced or disabled by customization.

### SAP-AW-D055

Workflow customization occurs only through declared extension points.

### SAP-AW-D056

Mandatory Workflow steps cannot be removed by lower-level customization.

### SAP-AW-D057

Policy customization is monotonic toward greater restriction.

### SAP-AW-D058

Policy exception/bypass mechanisms are outside the initial architecture.

### SAP-AW-D059

Knowledge evolves through revision and supersession rather than destructive replacement.

### SAP-AW-D060

More-specific facts may shadow less-specific facts without deleting their provenance.

### SAP-AW-D061

Same-scope material conflicts must be surfaced instead of silently resolved.

### SAP-AW-D062

Customization Packs declare compatibility with core and SAP domain contracts.

### SAP-AW-D063

Component content version and component contract version are separate concepts.

### SAP-AW-D064

Production-grade resolved configurations may be pinned to exact versions.

### SAP-AW-D065

Organization and project intelligence may live in private Customization Packs without forking the core repository.

### SAP-AW-D066

Secrets are never Customization content.

Customization stores credential references only.

### SAP-AW-D067

Task and user customization cannot alter safety, approval, provenance, or mandatory verification boundaries.

### SAP-AW-D068

Every resolved component preserves extension and resolution provenance.

### SAP-AW-D069

Resolved runtime configuration receives a deterministic semantic fingerprint.

### SAP-AW-D070

Customization Packs must be validated before activation and may include compatibility and fitness tests.

## Consequences

- Company-specific behavior can evolve without creating "company copies" of every core Agent.
- Effective runtime configuration becomes inspectable and reproducible.
- Core upgrades can check pack compatibility and private fitness tests before activation.
- Private repositories can contain internal SAP intelligence while raw credentials remain external.
- Resolution conflicts become explicit runtime/configuration states.

## Verification / fitness implications

Foundation fitness must prove that:

- protected fields cannot be overridden
- mandatory verification cannot be removed
- undeclared Workflow hooks are rejected
- incompatible packs cannot become ACTIVE
- same-scope material conflicts remain conflicts
- policy customization never weakens inherited Policy
- resolved configuration preserves provenance/fingerprint information

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
