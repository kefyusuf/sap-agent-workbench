# ADR-007 — Deterministic M0 Foundation Fitness Runner

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D084 through SAP-AW-D086
- **Scope:** M0 Foundation

## Context

The Safety Kernel fixtures are now materialized, but M0 cannot close until they are executable.

The runner must be:

- deterministic
- dependency-light
- cross-platform
- CI-friendly
- JSON-native
- independent from any LLM provider
- explicitly non-binding on the future product/runtime language

Choosing a test harness language must not accidentally decide the implementation language of the SAP Agent Workbench.

## Decision

### SAP-AW-D084

The M0 foundation fitness runner uses **Python 3 standard library only**.

No third-party Python package is required to execute the Safety Kernel.

### SAP-AW-D085

The foundation fitness runner is a test harness, not a product-runtime commitment.

Future Agent, orchestration, adapter, or product runtime implementation may use a different language without violating this decision.

### SAP-AW-D086

The M0 runner validates the committed fixture contract deterministically before executing scenarios.

It may implement the subset of JSON Schema semantics used by the committed M0 scenario schema without introducing an external JSON Schema dependency.

## Rationale

Python 3 provides sufficient standard-library support for:

- JSON parsing
- filesystem traversal
- regular expressions
- deterministic hashing
- CLI argument parsing
- structured report generation

The runner remains small enough to replace later if the project develops a different tooling baseline.

## Consequences

Positive:

- no package installation is required
- no provider/model dependency exists
- fixture validation and execution can run locally or in CI
- the product runtime remains undecided

Trade-offs:

- the runner supports only the schema features currently needed by the M0 fixture contract
- adding richer schema features may require extending the internal validator or adopting a dependency later
- Python 3 must be available where the M0 fitness suite is executed

## Verification / fitness implications

The runner must:

- reject malformed fixtures before scenario execution
- execute all known Safety Kernel kinds deterministically
- reject unknown scenario kinds
- emit PASS/FAIL per scenario
- exit non-zero when a CRITICAL scenario fails
- report a deterministic configuration fingerprint for the exact schema + fixture set + runner contract version

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
