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
| [ADR-006](./ADR-006-foundation-evaluation-and-m0-gate.md) | D071–D083 | Foundation Evaluation & M0 Gate |
| [ADR-007](./ADR-007-foundation-fitness-runner.md) | D084–D086 | Deterministic M0 Foundation Fitness Runner |
| [ADR-008](./ADR-008-technical-architect-agent-boundary.md) | D087–D094 | SAP Technical Architect Agent Boundary |
| [ADR-009](./ADR-009-technical-architect-evaluation.md) | D095–D101 | Technical Architect Evaluation Model |
| [ADR-010](./ADR-010-technical-architect-result-contract.md) | D102–D110 | Technical Architect Structured Result Contract |
| [ADR-011](./ADR-011-technical-architect-input-invocation.md) | D111–D119 | Technical Architect Input & Invocation Contract |
| [ADR-012](./ADR-012-technical-architect-runtime-invocation.md) | D120–D130 | Technical Architect Runtime Invocation Semantics |
| [ADR-013](./ADR-013-m1-runtime-technology.md) | D131–D140 | M1 Runtime Technology Boundary |
| [ADR-014](./ADR-014-m1-result-provenance-integrity.md) | D141–D145 | M1 Result Provenance Integrity |
| [ADR-015](./ADR-015-abap-development-agent-boundary.md) | D146–D156 | ABAP Development Agent Boundary |
| [ADR-016](./ADR-016-abap-development-evaluation.md) | D157–D164 | ABAP Development Evaluation Model |
| [ADR-017](./ADR-017-abap-development-contracts.md) | D165–D176 | ABAP Development Input & Result Contracts |
| [ADR-018](./ADR-018-m2-verification-evidence-compatibility.md) | D177–D182 | M2 Verification Evidence Compatibility |

The ADRs above materialize every currently accepted decision ID from SAP-AW-D001 through SAP-AW-D182.

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


### D102–D110 — M1 Technical Architect structured result

Defines the provider-independent result contract, status semantics, traceable claim support,
blocker/status consistency, nullable proposal semantics, explicit existing-solution discovery,
deterministic structural validation, preservation of the READ/QUERY/ANALYZE/PROPOSE capability boundary, and binding of results to input/configuration fingerprints.


### D111–D119 — M1 Technical Architect input & invocation data

Defines the provider-independent input envelope, resolved context/evidence snapshot boundary,
deterministic input fingerprint, evidence-catalog integrity, explicit read-only capability boundary,
secret isolation, provider semantic-preservation rule, and result provenance binding.


### D120–D130 — M1 Technical Architect runtime invocation

Defines runtime-owned result provenance, untrusted provider draft semantics, immutable fingerprinted input,
external provider selection, no side-effecting tool execution, one-attempt/no-hidden-repair behavior,
typed execution failures, BLOCKED-vs-runtime-failure separation, execution-record separation,
deterministic acceptance, and evaluation-only case assertions.


### D131–D140 — M1 runtime technology

Defines TypeScript/Node.js LTS as the product/reference runtime, ESM/strict compiler posture,
framework-free/provider-SDK-free core boundaries, deterministic Fixture Provider first,
synthetic/offline tests, Node standard-library preference, Python tooling separation,
minimal pinned dependencies, and deferred workspace splitting.


### D141–D145 — M1 result provenance integrity

Requires accepted result evidence/source references to remain closed over the validated invocation snapshot,
forbids model-created system evidence, restricts assumption references to ASSUMED claims,
and requires the TypeScript reference validator to preserve all contract-critical boundaries.


### D146–D156 — M2 ABAP Development Agent boundary

Defines implementation ownership downstream from architecture, architecture-fidelity rules,
system-object identity discipline, generated-code vs verification-evidence separation,
verification honesty, reuse-before-create, no-mutation boundaries, revision-bound handoff,
and synthetic/offline-first M2 scope.

### D157–D164 — M2 ABAP Development evaluation

Defines property-based implementation evaluation, synthetic fixtures, architecture-fidelity testing,
system-object hallucination failures, false verification failures, no-mutation checks,
missing-context behavior, and the rule that model grading cannot solely decide CRITICAL boundaries.


### D165–D176 — M2 ABAP Development contracts

Defines the provider-independent M2 input/result contracts, architecture-handoff binding,
existing-vs-proposed object identity, WORK_PRODUCT_READY semantics, object-reference integrity,
generated-code/evidence separation, provenance binding, and preservation of the no-mutation boundary.

### D177–D182 — M2 verification evidence compatibility

Requires evidence-backed verification claims, defines initial verification/evidence-type compatibility,
forbids documents/generated code from standing in for compile/ATC/test evidence,
keeps missing verification as required work, closes claims over the input evidence catalog,
and makes compatibility a deterministic CRITICAL boundary.
