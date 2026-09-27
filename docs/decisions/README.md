# Architecture Decision Registry

This directory contains canonical architecture decisions for SAP Agent Workbench.

## Decision groups

### D001–D009 — Product and foundation direction

Covers workbench scope, provider independence, component separation, customization outside core,
evidence requirements, reuse-before-create, least context, and verification-based completion.

### D010–D020 — Component model

Covers Agent, Skill, Workflow, Policy, Tool, Knowledge Pack, dependency, lifecycle,
and new-agent justification rules.

### D021–D034 — Context, evidence, claims, and provenance

Covers task-scoped context, source metadata, authority, claim classification, conflict handling,
revision binding, evidence immutability, provenance, secret isolation, and evidence-bound completion.

### D035–D050 — Capability, policy, approval, and execution safety

Covers action/resource/target capabilities, explicit tool operations, Action Intents, risk dimensions,
policy resolution, availability vs authorization, approval binding, revalidation, and the no-mutation MVP boundary.

### D051–D070 — Customization and extension

Covers namespaces, ADD/EXTEND/REPLACE/RESTRICT/DISABLE, protected fields, workflow hooks,
policy monotonicity, compatibility, private customization packs, semantic configuration fingerprints,
and customization fitness.

### D071–D083 — Evaluation and M0 closure

Covers deterministic foundation fitness, criticality, negative-path testing, Safety Kernel,
reproducibility, public/private eval separation, and M0 exit conditions.

## Record format

Individual decision records will be materialized incrementally using a stable template:

- ID
- Status
- Context
- Decision
- Consequences
- Verification / fitness implications
- Supersedes / superseded by

The registry is an index only; an entry is not considered fully materialized until its individual record exists.
