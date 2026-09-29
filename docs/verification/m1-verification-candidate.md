# M1 Verification Candidate Manifest

## Status

CANDIDATE ARTIFACT SET FROZEN / EXACT EXECUTION PENDING

This manifest freezes the M1 reference-harness artifact set that must be exercised by the next exact verification run.

It does not claim that the candidate has passed install, compile, or test execution.

## Candidate boundary

From this point until exact verification completes, M1 may change only for:

1. verification evidence/status documentation
2. a defect exposed by the exact verification run
3. a correction to verification infrastructure that is required to obtain trustworthy evidence

Do not add:

- new M1 product behavior
- a real provider adapter
- live SAP integration
- WRITE / DEPLOY / TRANSPORT / ADMIN
- new architecture scope

Any change to a frozen runtime/test/fixture artifact invalidates this candidate set and requires a new manifest/reverification.

## Toolchain contract

```text
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2
@types/node 24.13.6
tests      11
```

## Dependency and execution artifacts

| Path | Git blob SHA |
|---|---|
| `.nvmrc` | `df6ae3370f9f89272d88629c442cf554d6c1f9fb` |
| `package.json` | `292ecc3a2407fc4530e1cec3a322c48358a5f4ed` |
| `package-lock.json` | `25ec7de9ef19b3f473e67fc7613a1ca273d40b1f` |
| `tsconfig.json` | `27c1d75cc42b4e5de645414b5d4d4b02ef18d0b1` |
| `scripts/verify_m1_reference_harness.mjs` | `44ba22f71194d4796e67c6d8a78b1e3374cbc1a3` |
| `compose.m1-verify.yml` | `b024d3b56d1178fc1828af58aaba195027d5c224` |
| `.github/workflows/m1-reference-harness.yml` | `6782ca90218f2a184c95bacd685d41417d84512f` |

## M1 runtime artifact set

| Path | Git blob SHA |
|---|---|
| `src/m1/contracts.ts` | `f4496d9ad2d4b20e898b3e82c42e2a9a2c011e2f` |
| `src/m1/fingerprint.ts` | `f2caf2306c5d899a1c77d3823400ff68e5bba441` |
| `src/m1/provider-adapter.ts` | `859c52fee315f2436175d09ed1ae98048ff009ab` |
| `src/m1/validation.ts` | `932098134baa6edcd726610bc5441fa0b4cfffac` |
| `src/m1/runtime.ts` | `da2dd01175d8f3d6692a2b9145a8bcb60b836557` |
| `src/m1/fixture-provider.ts` | `0c41538a30faa6de8ace79441551f53c2fc159a3` |
| `src/m1/index.ts` | `dfc676267b20b4dcb8ca4dbe3e42beae054e9a46` |

## Test artifact

| Path | Git blob SHA |
|---|---|
| `test/m1/runtime.test.ts` | `120bc2fcfe0262ef6d3329954a37161c7d1d7028` |

The committed test file contains 11 offline Node tests.

## Exercised fixture/result subset

| Path | Git blob SHA |
|---|---|
| `evals/m1/technical-architect/TA-002.json` | `76a26531e6546659958c485d41e1c86bde5bbe96` |
| `evals/m1/technical-architect/TA-003.json` | `430a0ffb94c2b11795294cd5e94e55ec90341e76` |
| `evals/m1/result-examples/valid-blocked.json` | `861eb37f887bc5f2bea3fa67412ca5f948510e3b` |
| `evals/m1/result-examples/valid-completed.json` | `b11374d74058f35827c97448fd68a583041ad139` |
| `evals/m1/result-examples/invalid-completed-with-blocker.json` | `ab662a866d2e08559921e4478c9a8ef0f4c95e1f` |

## Verification paths

### Local Docker

```text
docker compose -f compose.m1-verify.yml run --rm m1-verify
```

### Repository-native manual workflow

```text
.github/workflows/m1-reference-harness.yml
trigger: workflow_dispatch
```

Both paths execute the same authoritative runner:

```text
node scripts/verify_m1_reference_harness.mjs
```

## Acceptance evidence

The next authoritative PASS must be revision-bound and show:

```text
overall = PASS

Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2

tests = 11
pass  = 11
fail  = 0

clean_before = true
clean_after  = true
```

The generated report is:

```text
build/m1-reference-harness-verification.json
```

## Freeze implication

```text
M1 PRODUCT/DESIGN SCOPE          FROZEN
M1 CANDIDATE ARTIFACT SET        FROZEN

EXACT INSTALL/COMPILE/TEST       PENDING
M1 REFERENCE HARNESS VERIFIED    NO
REAL PROVIDER GATE               CLOSED
M2/M3 PRODUCT RUNTIME GATES      CLOSED
```

The next M1 engineering action is execution or defect repair only.


## Git safe-directory correction

The frozen verification-infrastructure artifact `compose.m1-verify.yml` changed under the explicitly allowed
"correction required to make verification trustworthy" exception.

Reason:

- the pinned Node Bookworm image runs the verification command as root
- a Linux host bind mount may be owned by a different UID
- Git can reject revision/clean-tree checks as dubious ownership before the M1 harness is exercised

The compose path now supplies a process-scoped `safe.directory=/workspace` override.

No `src/m1/*`, `test/m1/*`, fixture, package manifest, lockfile, or authoritative verification-runner artifact changed.

The compose blob recorded above is the new frozen verification candidate identity.
