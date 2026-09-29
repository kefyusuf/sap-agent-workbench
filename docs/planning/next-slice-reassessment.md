# Next Slice Product/Scope Reassessment

## Status

CLOSED — next implementation candidate selected.

Selected slice:

```text
ONE REAL M1 PROVIDER ADAPTER
```

This gate selects the next product slice only.

It does not select a provider vendor/model and does not authorize implementation yet.

## Current verified baseline

```text
M1 provider-neutral reference harness: VERIFIED
M2 deterministic tooling:             VERIFIED
M3 deterministic tooling:             VERIFIED

M1 → M2 lineage: NORMALIZED
M2 → M3 lineage: NORMALIZED
```

Current capability boundary remains:

```text
READ
QUERY
ANALYZE
PROPOSE
```

No live SAP mutation capability is opened by this decision.

## Candidates considered

### A — M2 product runtime

Status:

```text
DEFER
```

Why not next:

- M2 contracts and deterministic tooling are already verified.
- Building M2 runtime now would extend another synthetic runtime path before validating the existing provider boundary against a real model.
- It risks duplicating M1 execution mechanics or motivating premature generalized runtime abstractions.
- It would not yet validate real provider structured-output reliability.

### B — M3 product runtime

Status:

```text
DEFER
```

Why not next:

- M3 is downstream of implementation work products.
- Reviewer/Test Engineer runtime is less useful before the system has a real model execution path for an upstream reasoning owner.
- It would expand two additional reasoning owners before validating the existing M1 provider boundary.

### C — one real provider adapter for M1

Status:

```text
SELECTED
```

Why selected:

- M1 already has a verified provider-neutral runtime and `ProviderAdapter` boundary.
- ADR-013 explicitly established Fixture Provider first and real-provider integration only after that path is stable.
- The reference harness is now exact-execution verified.
- This is the smallest slice that validates whether the workbench can turn a structured Technical Architect input into a real model-generated semantic draft while preserving deterministic runtime ownership and validation.
- It exercises the highest remaining product uncertainty without adding SAP connectivity or mutation.
- It provides more product evidence than adding another fixture-only runtime.

### D — no further runtime expansion

Status:

```text
NOT SELECTED
```

Reason:

The verified baseline is sufficient to justify one bounded real-provider experiment. No architectural or safety blocker currently requires stopping all runtime work.

## Selected slice boundary

The next implementation slice may introduce exactly one concrete provider adapter implementing the existing:

```text
ProviderAdapter
```

interface.

The slice must preserve the existing M1 invocation semantics:

```text
validated input
→ immutable fingerprinted snapshot
→ one provider invocation
→ raw semantic draft
→ runtime-owned field binding
→ deterministic result validation
→ accepted result or typed failure
```

## In scope

- one provider-specific adapter
- external provider/model selection
- provider-specific request/response translation at the adapter boundary
- one provider attempt per invocation
- deterministic adapter tests without live SAP
- one synthetic/anonymized live-provider smoke before declaring the adapter verified
- provider failure mapping into the existing failure taxonomy
- preservation of runtime-owned provenance fields
- preservation of evidence/source reference closure

## Explicitly out of scope

- multiple provider adapters
- provider fallback
- automatic retry
- semantic repair loops
- tool loops
- streaming
- agent framework adoption
- workflow framework adoption
- DI container
- generalized multi-provider request abstraction unless the selected adapter proves it necessary
- M2 product runtime
- M3 product runtime
- live SAP retrieval
- SAP WRITE / DEPLOY / TRANSPORT / ADMIN
- ABAP compile/ATC execution
- provider comparison/routing
- token/cost optimization
- production deployment

## Provider-independence rule

Selecting one concrete adapter does not make that provider part of core architecture.

Required dependency direction remains:

```text
M1 core runtime
    ↑
ProviderAdapter
    ↑
one concrete provider adapter
```

Provider SDK/types, if used, must remain inside the adapter boundary.

Core M1 modules must not import provider-specific packages or types.

## Vendor/model selection

Provider/model selection is intentionally not decided by this reassessment.

The implementation gate must choose one provider based on concrete execution needs such as:

- structured JSON/output support
- available credentials/account access
- API stability
- compatibility with one-shot invocation
- minimal adapter complexity
- ability to run a synthetic verification case

Do not add a generic provider registry or routing layer merely to postpone this choice.

## Required acceptance evidence

Before the selected adapter may be called VERIFIED:

1. existing M1 reference harness remains green
2. strict TypeScript compile passes
3. current 11 M1 runtime tests remain 11/11 PASS
4. adapter-specific deterministic tests pass
5. core provider-independence static scan passes
6. provider cannot author runtime-owned fields
7. provider/model failure maps to `PROVIDER_FAILURE`
8. malformed provider output remains visible as typed failure; no hidden repair
9. evidence/source references still close against the immutable invocation input
10. one synthetic/anonymized live-provider invocation is captured as execution evidence
11. no SAP connection or mutation capability is introduced

## Stop conditions

Stop implementation and reopen the gate if the selected adapter requires any of:

- changes to M0 safety/capability semantics
- hidden retry/repair to achieve basic correctness
- provider-specific types leaking into core
- a generalized agent/provider framework
- live SAP access
- mutation capability
- changes to M2/M3 scope

## After this slice

After one provider adapter is verified, open a fresh reassessment before choosing among:

```text
M2 product runtime
M3 product runtime
second provider adapter
live read/query SAP tooling
no further expansion
```

No follow-on slice is pre-authorized by this decision.
