# ADR-013 — M1 Runtime Technology Boundary

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D131 through SAP-AW-D140
- **Scope:** M1 Technical Architect

## Context

M1 input, result, evaluation, and runtime invocation semantics are now provider independent.

The project can therefore choose a reference/product runtime technology without allowing that choice to redefine Agent,
Policy, Evidence, or provider contracts.

The runtime needs strong JSON/type support, adapter boundaries, deterministic hashing, CLI/library ergonomics,
and future provider/MCP integration. It does not need Python-specific ML libraries.

## Decision

### SAP-AW-D131

The M1 product/reference runtime uses TypeScript on the current supported Node.js LTS line.

### SAP-AW-D132

The M1 runtime uses ESM and strict TypeScript compiler settings.

### SAP-AW-D133

The initial runtime is framework-free.

No agent framework, workflow framework, web framework, or DI container is introduced for the first slice.

### SAP-AW-D134

The core runtime is provider-SDK independent.

Concrete provider SDK imports are allowed only inside provider-specific adapters.

### SAP-AW-D135

The first executable provider adapter is a deterministic in-memory Fixture Provider with no network access.

It exists to verify runtime contracts before real-provider integration.

### SAP-AW-D136

The first runtime tests use synthetic/anonymized fixtures and no credentials, network, or SAP connection.

### SAP-AW-D137

Node standard-library facilities are preferred for hashing, filesystem operations, and the initial test runner.

### SAP-AW-D138

Python remains deterministic evaluation tooling and is not invoked by the normal TypeScript product runtime.

### SAP-AW-D139

Runtime dependencies are kept minimal and pinned by the repository lockfile.

A dependency requires explicit implementation value; provider SDKs do not leak into core.

### SAP-AW-D140

A repository-root package is sufficient for M1.

Workspace/multi-package splitting is deferred until independently versioned runtime packages actually exist.

## Consequences

- the first real runtime has a concrete implementation language
- provider independence remains architectural rather than aspirational
- the M0/M1 Python fitness tooling remains usable without becoming a production dependency
- a Fixture Provider can prove orchestration semantics before API credentials exist
- the repository avoids early framework/package fragmentation
- a future provider adapter can be replaced without rewriting core contracts

## Verification / fitness implications

The first TypeScript slice must demonstrate:

- strict compilation
- no concrete provider import in core
- deterministic input SHA-256 matching the Python contract algorithm
- Fixture Provider invocation without network
- runtime-owned provenance binding
- valid BLOCKED result acceptance
- contract-invalid result rejection
- one provider attempt per invocation

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
