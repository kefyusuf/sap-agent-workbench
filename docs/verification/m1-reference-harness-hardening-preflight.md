# M1 Reference Harness Hardening Preflight

## Status

PASS for repository-content/static boundary checks.

The exact Node 24.21.0 / TypeScript 7.0.2 compile-and-test gate remains pending.

## Decision continuity

M1 architecture decisions currently cover:

```text
SAP-AW-D087 through SAP-AW-D145
```

Static registry inspection found:

```text
unique decisions: 59
missing IDs:       0
cross-ADR dupes:   0
```

## Provenance hardening

ADR-014 adds invocation-aware result provenance integrity:

- result evidence references must resolve to the input evidence catalog
- result factual/conflict source references must resolve to the validated input snapshot
- the provider cannot create new system evidence
- assumption references must point only to ASSUMED result claims
- the TypeScript validator must preserve all contract-critical boundaries

The reference runtime now passes the exact invocation reference set into result validation.

## Runtime boundary static scan

Scanned:

- `src/m1/contracts.ts`
- `src/m1/fingerprint.ts`
- `src/m1/provider-adapter.ts`
- `src/m1/validation.ts`
- `src/m1/runtime.ts`
- `src/m1/fixture-provider.ts`
- `src/m1/index.ts`
- `test/m1/runtime.test.ts`
- `package.json`
- `tsconfig.json`
- `.nvmrc`

No matches were found for:

- OpenAI SDK imports
- Anthropic SDK imports
- Google provider SDK imports
- SAP SDK package imports
- `fetch(...)`
- Axios
- hard-coded HTTP URLs

No real-provider adapter file is present in the M1 stack.

## Test inventory

The TypeScript reference test file currently contains:

```text
11 tests
```

Coverage includes:

1. TA-002 cross-language canonical input fingerprint
2. TA-003 cross-language canonical input fingerprint
3. valid BLOCKED result acceptance
4. valid COMPLETED result acceptance
5. provider-authored runtime provenance rejection
6. COMPLETED + unresolved blocker rejection
7. invalid input rejected before provider invocation
8. provider failure kept distinct from BLOCKED behavior
9. fabricated evidence reference rejection
10. fabricated factual source reference rejection
11. assumption reference to non-ASSUMED claim rejection

## Toolchain pin

Current exact verification target:

```text
Node.js       24.21.0
npm           11.19.0
TypeScript    7.0.2
@types/node   24.13.6
```

Repository metadata:

- `.nvmrc` → `24.21.0`
- `packageManager` → `npm@11.19.0`
- Node engine → `>=24.21 <25`
- npm engine → `>=11.19 <12`

The Node test glob is quoted so the npm test script remains portable across shells supported by Node's test-runner glob semantics.

## Stack scope

Compared with `feat/m0-foundation`:

```text
status:        ahead
behind:        0
M1 changed files: 44
live provider files: 0
```

The child branch remains within M1 contracts/evals/reference-runtime scope.

## Not yet verified

This report does not claim:

- generated `package-lock.json`
- `npm ci`
- strict TypeScript 7 compilation
- Node 24 offline test execution
- runtime test PASS
- real provider behavior

## Gate result

```text
M1 CONTRACT DESIGN                 COMPLETE
M1 REFERENCE HARNESS MATERIALIZED  YES
PROVENANCE INTEGRITY HARDENING     PASS (static)
PROVIDER-INDEPENDENCE SCAN         PASS
DECISION CONTINUITY                PASS
STACK SCOPE                        PASS

LOCKFILE                           PENDING
STRICT COMPILE                     PENDING
NODE TEST EXECUTION                PENDING
REFERENCE HARNESS VERIFIED         NO
REAL PROVIDER GATE                 CLOSED
```

The next safe action remains exact-toolchain verification, not provider integration.
