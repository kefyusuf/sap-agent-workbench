# M1 Reference Harness Verification Runner Preflight

## Status

MATERIALIZED / FAIL-CLOSED PREFLIGHT PASS / SELECTED-TOOLCHAIN EXECUTION PENDING

## Purpose

Provide one revision-bound verification entry point for the M1 TypeScript reference harness without adding a provider,
SAP adapter, framework, or production capability.

Committed runner:

```text
scripts/verify_m1_reference_harness.mjs
```

Git blob:

```text
44ba22f71194d4796e67c6d8a78b1e3374cbc1a3
```

## Required toolchain

The runner fails closed unless the exact selected baseline is present:

```text
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2
Node tests 11
```

## Verification sequence

The runner:

1. fingerprints `package.json` and `package-lock.json`
2. records the exact Git revision
3. requires a clean Git working tree
4. validates exact Node version
5. validates exact npm version
6. runs `npm ci --ignore-scripts`
7. executes the installed TypeScript compiler and requires 7.0.2
8. runs `npm run check`
9. requires Node test summary:
   - tests = 11
   - pass = 11
   - fail = 0
10. requires the Git working tree to remain clean
11. writes:
    `build/m1-reference-harness-verification.json`

The report is ignored through the existing `build/` ignore rule.

## Static script preflight

Committed-content inspection confirms the runner includes:

```text
exact Node pin           yes
exact npm pin            yes
exact TypeScript pin     yes
exact test count         yes
npm ci                   yes
npm run check            yes
Git revision capture     yes
clean-tree checks        yes
```

No references were found for:

- OpenAI
- Anthropic
- SAP SDK packages
- fetch/network clients
- Axios

The runner is verification tooling and is not imported by the M1 product runtime.

## Syntax preflight

The authored runner was syntax-checked with:

```text
node --check scripts/verify_m1_reference_harness.mjs
```

using an available Node 22 environment.

Result:

```text
syntax check: PASS
```

This is only a syntax preflight; Node 22 is not the selected verification runtime.

## Fail-closed probe

A disposable clean Git repository was used to exercise the runner under an intentionally incorrect toolchain:

```text
Node observed: 22.16.0
npm observed:  10.9.2
```

Observed runner behavior:

```text
overall: FAIL
runner exit code: 1
npm ci attempted: no
clean_before: true
clean_after: true
```

Failure reasons:

```text
Node version mismatch: expected 24.21.0, observed 22.16.0.
npm version mismatch: expected 11.19.0, observed 10.9.2.
```

This confirms the verification runner does not continue into installation/testing under the wrong toolchain.

## Authoritative execution still pending

The following command must still be run from the exact committed M1 revision with the selected toolchain:

```text
node scripts/verify_m1_reference_harness.mjs
```

Authoritative PASS requires:

```text
overall = PASS
Node = 24.21.0
npm = 11.19.0
TypeScript = 7.0.2
tests = 11
pass = 11
fail = 0
clean_before = true
clean_after = true
```

## Gate implication

```text
LOCKFILE                       MATERIALIZED / PREFLIGHT PASS
VERIFICATION RUNNER            MATERIALIZED
RUNNER SYNTAX PREFLIGHT        PASS
RUNNER FAIL-CLOSED PROBE       PASS

EXACT npm ci                   PENDING
STRICT TYPESCRIPT COMPILE      PENDING
11 OFFLINE NODE TESTS          PENDING
REVISION-BOUND PASS REPORT     PENDING

M1 REFERENCE HARNESS VERIFIED  NO
REAL PROVIDER GATE             CLOSED
```
