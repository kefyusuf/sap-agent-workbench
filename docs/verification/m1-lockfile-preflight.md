# M1 Dependency Lockfile Preflight

## Status

PASS for deterministic lockfile structure/provenance preflight.

Install/compile/test execution remains pending.

## Purpose

Materialize the exact dependency graph required by the pinned M1 TypeScript reference harness without widening product/runtime scope.

The committed lockfile is:

```text
package-lock.json
lockfileVersion = 3
```

## Project manifest binding

Committed project manifest blob:

```text
package.json
Git blob: 292ecc3a2407fc4530e1cec3a322c48358a5f4ed
```

Committed lockfile blob:

```text
package-lock.json
Git blob: 25ec7de9ef19b3f473e67fc7613a1ca273d40b1f
```

The preflight confirms the lock root matches the committed manifest:

```text
name:    sap-agent-workbench
version: 0.0.0

devDependencies:
  @types/node: 24.13.6
  typescript:  7.0.2

engines:
  node: >=24.21 <25
  npm:  >=11.19 <12
```

## Resolved graph

The lock contains 24 package entries including the root package.

Direct/transitive resolution:

```text
@types/node 24.13.6
└── undici-types ~7.18.0
    └── resolved 7.18.2

typescript 7.0.2
└── 20 platform-specific optional TypeScript packages at 7.0.2
```

Every non-root package entry contains both:

- `resolved`
- `integrity`

All 20 TypeScript optional dependency entries exist and match the version declared by the TypeScript 7.0.2 package entry.

## Resolved metadata provenance

The lock graph was materialized from already-resolved public npm lock metadata and the project's exact pinned manifest.

TypeScript 7.0.2 package graph source:

```text
tanem/release-action
commit: 2720acfa06253c0b8599f3a6f67d8551b890a678
package-lock blob: 2e524efa4e4f7f0038edd1349e4afd94b96b3aa8
```

@types/node / undici-types graph source:

```text
ionic-team/ionic-framework
commit: 879e91d5e9c2115041758d708157d9785baa41c2
packages/migrate/package-lock.json
blob: 426267a873148c6e1247e7ffdb62fc0cbcd261a6
```

The selected public entries exactly match the project's pinned dependency versions.

## Structural checks

```text
lockfileVersion                       PASS (3)
root name/version                     PASS
root devDependencies                  PASS
root engines                          PASS
direct dependency versions            PASS
@types/node → undici-types range       PASS (~7.18.0)
undici-types resolution                PASS (7.18.2)
TypeScript optional package count      PASS (20)
TypeScript optional package versions   PASS
all non-root resolved fields present   PASS
all non-root integrity fields present  PASS
```

## Important limitation

This lockfile was **not** produced by claiming an `npm install` or `npm install --package-lock-only` execution in the current environment.

It is a deterministic materialization of the pinned resolved graph.

The authoritative runtime verification gate still requires the exact selected toolchain to consume it successfully:

```text
Node.js 24.21.0
npm 11.19.0
TypeScript 7.0.2
```

Required next evidence:

1. `npm ci`
2. `npm run check`
3. strict compile output
4. 11 offline Node-test results
5. exact tool versions
6. evidence bound to the tested M1 revision

## Gate implication

```text
PACKAGE LOCKFILE                    MATERIALIZED
LOCKFILE STRUCTURAL PREFLIGHT       PASS
LOCKFILE INSTALL VALIDATION         PENDING
STRICT TYPESCRIPT COMPILE           PENDING
OFFLINE NODE TESTS                  PENDING
M1 REFERENCE HARNESS VERIFIED       NO
REAL PROVIDER GATE                  CLOSED
```

No real provider, SAP adapter, network runtime, or mutation capability is introduced by this step.
