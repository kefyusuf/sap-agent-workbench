# M1 Runtime Technology Boundary

## Decision

The product/reference runtime for M1 will use:

- TypeScript
- Node.js 24 LTS line
- ESM modules
- strict TypeScript compiler settings

Python remains available for deterministic evaluation tooling but is not a product-runtime dependency.

## Why TypeScript / Node.js

The M1 runtime is primarily:

- JSON contract handling
- provider adapter orchestration
- deterministic fingerprinting
- structured-result normalization
- CLI/library integration
- future MCP/API integration

It does not require Python-specific ML/runtime libraries.

TypeScript provides a good fit for:

- explicit input/output contracts
- adapter interfaces
- JSON-heavy integration code
- provider SDK isolation
- Node/MCP ecosystem compatibility
- SAP BTP / CAP-adjacent development familiarity
- future CLI or service packaging

## Runtime boundary

The core runtime must not import a concrete model-provider SDK.

Preferred dependency direction:

```text
core runtime
    ↑
provider adapter interface
    ↑
provider-specific adapter
```

Not:

```text
core runtime
    → OpenAI SDK
    → Anthropic SDK
    → vendor-specific types
```

Provider-specific types must be translated at the adapter boundary.

## Initial implementation strategy

The first executable runtime slice uses a deterministic in-memory Fixture Provider.

It performs no network request.

Purpose:

1. prove input validation/fingerprinting flow
2. prove runtime-owned provenance binding
3. prove raw draft → normalized result flow
4. prove typed failure mapping
5. prove valid BLOCKED result acceptance
6. prove invalid output rejection

Only after this reference path is stable should a real provider adapter be added.

## Module system

Use ESM.

Core modules should be importable as ordinary TypeScript/JavaScript modules and not depend on a web framework.

## Compiler posture

Use strict TypeScript settings.

At minimum:

- `strict: true`
- no implicit provider-specific `any` escape at core boundaries
- explicit result/failure unions
- explicit adapter interfaces

## Dependency policy

M1 starts dependency-light.

Initial principles:

- no agent framework
- no workflow framework
- no DI container
- no provider SDK in core
- no runtime schema framework unless justified by the contract implementation
- prefer Node standard library for hashing, filesystem, and test harness
- pin dependencies through the repository lockfile

A dependency is added only when it removes meaningful complexity without weakening contracts or portability.

## Test baseline

Use Node's built-in test runner for the first runtime slice where practical.

Tests use:

- synthetic M1 fixtures
- Fixture Provider
- no credentials
- no network
- no SAP connection

Remote GitHub Actions availability is not required to author these tests; local deterministic evidence can be accumulated
and CI can replay the same commands when capacity returns.

## Python boundary

Existing Python scripts remain valid M0/M1 evaluation utilities:

- foundation fitness
- input validator/fingerprint utility
- result validator
- result-contract self-test

The TypeScript runtime must not shell out to Python as part of normal product execution.

This prevents the test harness language from leaking into the production runtime architecture.

## Verification toolchain baseline

The current pinned M1 verification baseline is:

- Node.js `24.21.0`
- npm `11.19.0`
- TypeScript `7.0.2`
- `@types/node` `24.13.6`

The Node/npm pin establishes a reproducible verification target; compatible Node 24 releases may be considered later
through an explicit dependency/toolchain update.

## Package baseline

The initial Node package will be repository-root scoped.

A committed package manifest and lockfile will pin the implementation baseline.

Multi-package/workspace splitting is explicitly deferred until there is more than one independently versioned runtime package.

## Not decided here

This decision does not select:

- OpenAI
- Anthropic
- Google
- local-model provider
- model name
- live SAP adapter
- deployment platform
- web framework
- database

Those remain separate later decisions.
