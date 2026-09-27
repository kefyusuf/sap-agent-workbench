# Architecture Decision Registry

This directory contains canonical architecture decisions for SAP Agent Workbench.

## Materialized ADRs

| ADR | Decision IDs | Topic |
|---|---|---|
| [ADR-001](./ADR-001-product-and-safety-boundary.md) | D001–D009 | Product & Safety Boundary |
| [ADR-002](./ADR-002-component-responsibility-model.md) | D010–D020 | Component Responsibility Model |
| [ADR-003](./ADR-003-context-evidence-and-provenance.md) | D021–D034 | Context, Evidence & Provenance |
| [ADR-004](./ADR-004-capability-policy-and-approval.md) | D035–D050 | Capability, Policy & Approval |
| [ADR-005](./ADR-005-customization-and-extension-resolution.md) | D051–D070 | Customization & Extension Resolution |
| [ADR-006](./ADR-006-foundation-evaluation-and-m0-gate.md) | D071–D083 | Foundation Evaluation & M0 Gate |\n| [ADR-007](./ADR-007-foundation-fitness-runner.md) | D084–D086 | Deterministic M0 Foundation Fitness Runner |
| [ADR-008](./ADR-008-technical-architect-agent-boundary.md) | D087–D094 | SAP Technical Architect Agent Boundary |
| [ADR-009](./ADR-009-technical-architect-evaluation.md) | D095–D101 | Technical Architect Evaluation Model |

The ADRs above materialize every currently accepted decision ID from SAP-AW-D001 through SAP-AW-D101.

## Decision groups

### D001–D009 — Product and foundation direction

WorkBench scope, provider independence, component separation, customization outside core,
evidence requirements, reuse-before-create, least context, and verification-based completion.

### D010–D020 — Component model

Agent, Skill, Workflow, Policy, Tool, Knowledge Pack, dependency, lifecycle,
and new-Agent justification rules.

### D021–D034 — Context, evidence, claims, and provenance

Task-scoped context, source metadata, authority, claim classification, conflict handling,
revision binding, evidence immutability, provenance, secret isolation, and evidence-bound completion.

### D035–D050 — Capability, policy, approval, and execution safety

Action/resource/target capabilities, explicit tool operations, Action Intents, risk dimensions,
Policy resolution, availability vs authorization, approval binding, revalidation, and the no-mutation MVP boundary.

### D051–D070 — Customization and extension

Namespaces, ADD/EXTEND/REPLACE/RESTRICT/DISABLE, protected fields, Workflow hooks,
Policy monotonicity, compatibility, private Customization Packs, semantic configuration fingerprints,
and customization fitness.

### D071–D083 — Evaluation and M0 closure

Deterministic foundation fitness, criticality, negative-path testing, Safety Kernel,
reproducibility, public/private eval separation, and M0 exit conditions.

## Record format

New architecture decisions use [ADR-000-template.md](./ADR-000-template.md).

Each ADR records:

- stable decision ID(s)
- status
- context
- decision
- consequences
- verification / fitness implications
- supersedes / superseded by

A decision ID is materialized only when its exact decision is present in an accepted ADR.


### D087–D094 — M1 Technical Architect Agent boundary

Defines the first concrete Agent responsibility boundary, task-scoped context expectations,
existing-solution discovery discipline, output classification, SAP object-name safety,
explicit non-goals, unknown/conflict handling, and preservation of the M0 no-mutation capability boundary.


### D095–D101 — M1 Technical Architect evaluation

Defines property-based Agent evaluation, synthetic/anonymized fixtures, zero-critical-failure acceptance,
explicit unsupported-object and conflict-handling checks, reuse-before-create evaluation,
and the rule that model-based grading cannot be the sole oracle for CRITICAL boundaries.
