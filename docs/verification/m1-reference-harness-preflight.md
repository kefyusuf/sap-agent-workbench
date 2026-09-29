# M1 Reference Harness Preflight

## Status

MATERIALIZED / EXECUTABLE VERIFICATION PENDING

The provider-neutral TypeScript reference harness is present on the M1 branch, but it has not yet been compiled and
executed with the pinned Node 24 / TypeScript 7 toolchain.

No build/test PASS is claimed by this report.

## Materialized runtime slice

```text
package.json
tsconfig.json

src/m1/
├── contracts.ts
├── fingerprint.ts
├── provider-adapter.ts
├── validation.ts
├── runtime.ts
├── fixture-provider.ts
└── index.ts

test/m1/
└── runtime.test.ts
```

## Intended runtime flow

```text
validate input
→ fingerprint exact input
→ freeze input snapshot
→ invoke one ProviderAdapter attempt
→ parse untrusted provider draft
→ reject provider-authored runtime fields
→ bind task/provenance in runtime
→ validate normalized result
→ accepted result OR typed failure
```

## Provider independence static scan

A branch-content scan found no imports/usages matching:

- OpenAI SDK
- Anthropic SDK
- Google provider SDK
- SAP SDK package imports
- `fetch(...)`
- Axios
- hard-coded HTTP URLs

in the M1 runtime source/test/package baseline.

The only provider implementation currently present is the in-memory `FixtureProvider`.

## Stack scope check

Compared with `feat/m0-foundation`, the M1 branch contains only M1 contracts, ADRs, evals, scripts,
TypeScript runtime/reference files, tests, and package/compiler metadata.

No live SAP connector or real provider adapter is present.

## Reference tests materialized

The Node test suite covers:

1. TA-002 canonical input fingerprint compatibility
2. TA-003 canonical input fingerprint compatibility
3. valid BLOCKED result accepted as successful invocation
4. valid COMPLETED result accepted with runtime-bound provenance
5. provider attempt to author runtime-owned provenance rejected
6. COMPLETED result with unresolved blocker rejected
7. invalid input rejected before provider invocation
8. provider failure kept distinct from BLOCKED Agent behavior

## Toolchain state

The package manifest pins:

- Node engine: `>=24 <25`
- TypeScript: `7.0.2`
- `@types/node`: `24.13.6`

A repository lockfile is now committed and has passed deterministic structural/provenance preflight. Exact npm install validation remains pending.

The current execution environment available during this preflight has Node 22 and TypeScript 5.8.3 and cannot reach
the package registry. It therefore cannot provide authoritative build/test evidence for the selected Node 24 /
TypeScript 7 baseline.

Remote GitHub Actions is also currently unavailable due the user-reported Actions capacity/quota constraint.

## Verification debt

Before this implementation slice can be marked VERIFIED, capture:

1. `npm ci` against the committed lockfile
2. `npm run check`
3. the exact Node / npm / TypeScript versions used
4. test output bound to the exact tested M1 revision

Any compile or test failure must be fixed before adding a real provider adapter.

## Gate result

```text
REFERENCE_HARNESS_DESIGN       COMPLETE
REFERENCE_HARNESS_MATERIALIZED YES
STATIC_PROVIDER_BOUNDARY       PASS
STACK_SCOPE                    PASS

LOCKFILE                       MATERIALIZED / PREFLIGHT PASS
LOCKFILE_INSTALL_VALIDATION    PENDING
STRICT_COMPILE                 PENDING
OFFLINE TEST EXECUTION         PENDING
REFERENCE_HARNESS_VERIFIED     NO
REAL_PROVIDER_GATE             CLOSED
```

The next safe step is verification of this exact reference slice, not provider integration.


## Lockfile follow-up

See:

`docs/verification/m1-lockfile-preflight.md`

The lockfile materialization step does not claim successful npm installation or TypeScript execution.
