# M1 Status — SAP Technical Architect Agent

## Branch

`feat/m1-technical-architect`

Base:

`feat/m0-foundation`

Stack:

- PR #1 — M0 foundation → `main`
- PR #2 — M1 Technical Architect → `feat/m0-foundation`

Remote GitHub Actions capacity is currently unavailable, so review may continue while merges remain deferred.

## Current state

```text
M1 boundary design: COMPLETE
M1 evaluation contract: COMPLETE
Initial synthetic cases: 4 MATERIALIZED
Structured result contract: COMPLETE
Deterministic result validator: MATERIALIZED
Result validator self-test: MATERIALIZED / EXECUTION PENDING
Input/invocation data contract: COMPLETE
Runtime invocation semantics: COMPLETE
Deterministic input validator: MATERIALIZED
Runtime technology boundary: COMPLETE
Reference harness implementation: VERIFIED — exact revision 6bb388af42e4e0d9fce11df3b78b5e3eb221c78f
Result provenance integrity: COMPLETE
M1 decisions D087–D145 continuity: PASS
Exact Node/npm verification baseline: PINNED
Package lockfile: VERIFIED BY npm ci
Static provider-independence/hardening preflight: PASS
TypeScript runtime tests materialized: 11
Reference verification runner: MATERIALIZED / FAIL-CLOSED PREFLIGHT PASS
Pinned Docker verification path: MATERIALIZED / IMAGE PIN AUDIT PASS / GIT SAFE-DIRECTORY PREFLIGHT PASS
Manual repository-native M1 workflow: MATERIALIZED / STATIC PREFLIGHT PASS
Frozen candidate integrity: PASS — 20/20 blob identities
Strict compile/test: PASS — 11/11
Provider integration: NOT STARTED — requires separate next-scope gate
SAP live adapters: NOT_STARTED
```

## Materialized

### Agent boundary

- bounded architecture-reasoning responsibility
- input/context expectations
- requirement-to-architecture reasoning sequence
- existing-solution discovery discipline
- system-specific object-name hallucination guardrail
- M1 non-goals
- preservation of M0 capability boundary
- ADR-008 / SAP-AW-D087 through SAP-AW-D094

### Evaluation

- property-based evaluation contract
- CRITICAL vs REQUIRED failure semantics
- synthetic/anonymized-first policy
- explicit unsupported-object evaluation
- material unknown/conflict evaluation
- reuse-before-create evaluation
- no single model judge for CRITICAL boundaries
- TA-001 through TA-004 with machine-readable output assertions
- ADR-009 / SAP-AW-D095 through SAP-AW-D101

### Structured result

- `m1.technical-architect-result.v1`
- explicit COMPLETED / NEEDS_CLARIFICATION / BLOCKED semantics
- typed claims / unknowns / conflicts
- explicit existing-solution discovery
- candidate options separated from selected proposal
- deterministic blocker/status invariants
- READ/QUERY/ANALYZE/PROPOSE-only requested capabilities
- input/configuration provenance fingerprints
- provider-independent deterministic validator
- positive and negative result examples
- self-test harness
- ADR-010 / SAP-AW-D102 through SAP-AW-D110

## Verification state

Repository-content preflight confirms:

- all four M1 cases contain machine-readable output assertions
- valid BLOCKED example satisfies the core blocker/status rules
- valid COMPLETED example satisfies the core proposal/handoff rules
- invalid COMPLETED-with-blocker example is shaped to be rejected
- result schema identity matches the documented v1 contract

See:

`docs/verification/m1-result-contract-preflight.md`

Exact Python execution of the committed validator/self-test remains pending while remote CI is unavailable.

## Input/invocation data contract

Materialized:

- `m1.technical-architect-input.v1`
- exact task/scope/constraint envelope
- resolved context claims / unknowns / conflicts
- evidence catalog with reference integrity
- explicit READ/QUERY/ANALYZE/PROPOSE capability boundary
- resolved configuration fingerprint
- deterministic canonical input fingerprint
- secret isolation
- requested result-contract binding
- normalized TA-001 through TA-004 inputs
- `scripts/validate_m1_input.py`
- ADR-011 / SAP-AW-D111 through SAP-AW-D119

See:

`docs/verification/m1-input-contract-preflight.md`

## Runtime invocation semantics

Materialized:

- runtime-owned result identity/provenance fields
- untrusted provider semantic-draft boundary
- immutable fingerprinted input snapshot
- externally selected provider adapter
- no side-effecting SAP Tool execution
- one provider attempt per invocation
- no hidden repair/retry/fallback
- typed execution failures
- valid BLOCKED/NEEDS_CLARIFICATION separated from runtime failure
- execution metadata separated from SAP evidence
- evaluation-only case assertions
- ADR-012 / SAP-AW-D120 through SAP-AW-D130

See:

- `contracts/technical-architect-execution.md`
- `docs/m1/runtime-invocation.md`

## Runtime technology boundary

Materialized:

- TypeScript + Node.js LTS product/reference runtime
- ESM + strict TypeScript
- framework-free first slice
- provider-SDK-free core
- deterministic in-memory Fixture Provider first
- Node built-in test baseline
- no credentials/network/SAP connection
- Python retained only as evaluation tooling
- minimal pinned dependencies
- repository-root package for M1
- ADR-013 / SAP-AW-D131 through SAP-AW-D140

See:

`docs/m1/runtime-technology.md`

## Reference harness implementation

Materialized:

- strict TypeScript contract types
- canonical SHA-256 input fingerprinting
- provider-neutral `ProviderAdapter`
- deterministic in-memory `FixtureProvider`
- input/result invariant validation
- provider-neutral execution runtime
- runtime-owned task/provenance binding
- typed runtime failures
- offline Node test suite
- invocation-aware evidence/source provenance validation
- assumption-reference integrity
- exact Node 24.21.0 / npm 11.19.0 verification baseline
- no provider SDK / network / credentials / SAP connectivity

See:

`docs/verification/m1-reference-harness-preflight.md`

Latest hardening preflight:

`docs/verification/m1-reference-harness-hardening-preflight.md`

Dependency lockfile preflight:

`docs/verification/m1-lockfile-preflight.md`

Verification runner preflight:

`docs/verification/m1-verification-runner-preflight.md`

Pinned Docker verification path:

`docs/verification/m1-docker-verification.md`

Docker image pin audit:

`docs/verification/m1-docker-image-pin-audit.md`

Manual repository-native workflow preflight:

`docs/verification/m1-manual-ci-preflight.md`

Frozen verification candidate manifest:

`docs/verification/m1-verification-candidate.md`

## Exact verification result

Verified revision:

`6bb388af42e4e0d9fce11df3b78b5e3eb221c78f`

Result:

```text
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2

npm ci     PASS
compile    PASS
tests      11
pass       11
fail       0

clean_before true
clean_after  true
overall      PASS
```

See:

`docs/verification/m1-reference-harness-execution.md`

## Next gate

M1 product/runtime verification is complete.

The next safe action is stack maintenance only:

1. refresh M2 onto the finalized M1 branch
2. re-run `python scripts/selftest_m2_contracts.py`
3. require 7/7 PASS
4. only then refresh M3 onto M2

Do not add a real provider adapter during this stack-maintenance gate.

## Guardrail

Do not introduce:

- live SAP connectors
- mutation capabilities
- ABAP implementation Agent
- provider-specific orchestration
- production access

during the next gate.


## Verification candidate freeze

The M1 runtime/test/fixture artifact set was frozen and has now passed exact execution.

Until the verification run completes, allowed M1 changes are limited to:

- verification evidence/status documentation
- defects exposed by verification
- corrections required to make verification trustworthy

Do not add new M1 behavior or provider integration.

See:

`docs/verification/m1-verification-candidate.md`


## Docker Git ownership correction

The pinned Node Bookworm image executes as root. A Linux host bind mount may be owned by a different UID, causing Git to reject the mounted checkout as dubious ownership before revision/clean-tree evidence can be collected.

The Docker verification service now passes a process-scoped:

`safe.directory=/workspace`

through `GIT_CONFIG_COUNT/GIT_CONFIG_KEY_0/GIT_CONFIG_VALUE_0`.

A disposable ownership-mismatch probe reproduced the Git failure without the override and returned exit code 0 with the scoped override.

No product/runtime/test/fixture artifact changed. The verification candidate was re-frozen and re-audited:

```text
frozen artifacts: 20
matched:          20
mismatches:        0
integrity:         PASS
```
