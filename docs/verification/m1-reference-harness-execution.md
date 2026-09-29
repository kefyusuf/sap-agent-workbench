# M1 Reference Harness Exact Execution

## Status

PASS — exact selected toolchain execution completed successfully.

## Verified revision

```text
6bb388af42e4e0d9fce11df3b78b5e3eb221c78f
```

This revision contains two verification-driven defect fixes discovered during execution:

1. the valid COMPLETED fixture now references evidence IDs (`E-001`, `E-002`) instead of evidence source refs
2. the verification runner accepts the Node 24 test runner summary prefix (`ℹ`) in addition to `#`

No new M1 product behavior, provider adapter, SAP integration, or capability was introduced.

## Execution environment

The repository was freshly cloned into an isolated Linux sandbox and checked out at the exact revision above.

Selected toolchain:

```text
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2
```

The authoritative command executed was:

```text
node scripts/verify_m1_reference_harness.mjs
```

The runner itself performed:

- exact Git revision capture
- clean-tree precondition
- `npm ci --ignore-scripts`
- installed TypeScript version check
- `npm run check`
- strict TypeScript compile
- all 11 offline Node tests
- clean-tree postcondition
- revision-bound JSON report generation

## Final result

```text
overall: PASS

revision:
6bb388af42e4e0d9fce11df3b78b5e3eb221c78f

observed:
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2

tests: 11
pass:  11
fail:  0

clean_before: true
clean_after:  true
```

Dependency installation:

```text
npm ci --ignore-scripts
exit code: 0

added 4 packages
audited 5 packages
found 0 vulnerabilities
```

Strict build/test command:

```text
npm run check
exit code: 0
```

Node test summary:

```text
tests     11
pass      11
fail       0
cancelled  0
skipped    0
todo       0
```

## Artifact fingerprints from execution report

```text
package.json
sha256:dbb1b80420bb1b6420e2e5dffe074abd2f178e12ff0bb63c5d5415a1cc9afd19

package-lock.json
sha256:738ba5586f985075dc64762a0981810779c5715487008670a9f03ba298998405
```

Relevant Git blob identities at the verified revision:

```text
scripts/verify_m1_reference_harness.mjs
b0c4c835e3523ddf1f978b908a28f74a7d574679

evals/m1/result-examples/valid-completed.json
f03754757cb57a7c35eb55a79d4bd29f3f3036ef

test/m1/runtime.test.ts
120bc2fcfe0262ef6d3329954a37161c7d1d7028

package.json
292ecc3a2407fc4530e1cec3a322c48358a5f4ed

package-lock.json
25ec7de9ef19b3f473e67fc7613a1ca273d40b1f
```

## Verification history

### Attempt 1

Revision:

```text
1c044c83aee9b25ec05fa828234f65f2de362f45
```

Result:

```text
10 pass / 1 fail
```

The failing valid-COMPLETED scenario exposed a fixture defect: result `evidence_refs` contained evidence `source_ref` values rather than invocation evidence IDs.

Runtime correctly rejected those references.

The fixture was corrected without changing runtime semantics.

### Attempt 2

Revision:

```text
1c2ade64a138b064966af70b2824a76ce7f2c022
```

The actual Node tests passed:

```text
11 pass / 0 fail
```

but the verification runner reported FAIL because it parsed the historical `# tests` summary format while Node 24 emitted:

```text
ℹ tests 11
ℹ pass 11
ℹ fail 0
```

The runner parser was corrected to accept both forms.

### Attempt 3

Revision:

```text
6bb388af42e4e0d9fce11df3b78b5e3eb221c78f
```

Result:

```text
PASS
11/11 tests
exit code 0
clean before/after
exact toolchain matched
```

## Gate implication

```text
M1 REFERENCE HARNESS EXACT EXECUTION     PASS
M1 REFERENCE HARNESS VERIFIED            YES

REAL PROVIDER IMPLEMENTATION             STILL NOT STARTED
LIVE SAP                                 STILL NOT STARTED

M2 PARENT REFRESH                        NOW ALLOWED
M2 POST-REFRESH 7/7 REVALIDATION         REQUIRED
M3 REFRESH                               WAITS FOR M2 REVALIDATION
```

Repository-native GitHub Actions replay remains desirable when Actions capacity is available, but it is no longer the blocker for the provider-neutral M1 reference-harness gate because exact revision-bound execution evidence now exists.
