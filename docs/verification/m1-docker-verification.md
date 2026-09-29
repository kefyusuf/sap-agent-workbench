# M1 Docker Verification Path

## Purpose

Provide a reproducible local execution path for the M1 reference-harness verification gate while GitHub Actions capacity is unavailable.

This is verification tooling only.

It does not add:

- provider integration
- SAP connectivity
- product runtime behavior
- mutation capability

## Image

The compose file pins the multi-platform Docker Hub index digest:

```text
node:24.21.0-bookworm
sha256:6dac556d980b7f0e5498d08f08cee0ca67798b4ad6c23964a9214920e67758d0
```

Node.js 24.21.0 bundles npm 11.19.0.

The M1 verification runner independently checks both versions and fails closed if the observed toolchain differs.

## Command

From the exact `feat/m1-technical-architect` revision:

```text
docker compose -f compose.m1-verify.yml run --rm m1-verify
```

The container then runs:

```text
node scripts/verify_m1_reference_harness.mjs
```

## Workspace mounts

The repository is mounted read/write at:

```text
/workspace
```

Ephemeral Docker volumes isolate:

```text
/workspace/node_modules
/workspace/dist
```

This avoids leaving container-owned dependency/build files in the host checkout.

The revision-bound verification report remains on the host under the ignored:

```text
build/m1-reference-harness-verification.json
```

directory.

## Network boundary

Network access may be required by:

```text
npm ci --ignore-scripts
```

to retrieve the exact lockfile packages when they are not already cached.

After installation, the M1 reference tests themselves use:

- FixtureProvider only
- no provider SDK
- no live SAP
- no credentials
- no network behavior

## Expected authoritative PASS

The verification report must show:

```text
overall: PASS

Node.js:    24.21.0
npm:        11.19.0
TypeScript: 7.0.2

tests: 11
pass:  11
fail:  0

clean_before: true
clean_after:  true
```

## Failure handling

Any failure remains a closed gate.

Do not:

- add a real model provider
- open M2 runtime
- open M3 runtime
- add live SAP tooling

until the failure is understood and the exact M1 verification passes.

## Scope implication

This path removes the dependency on repository-native GitHub Actions for obtaining local execution evidence,
but it does not weaken the later requirement to replay canonical CI when Actions capacity becomes available.


## Image pin audit

The image pin was revalidated against Docker Hub's current metadata for `node:24.21.0-bookworm`.

Verified metadata:

```text
tag:          node:24.21.0-bookworm
Node version: 24.21.0
index digest: sha256:6dac556d980b7f0e5498d08f08cee0ca67798b4ad6c23964a9214920e67758d0
```

For linux/amd64, Docker Hub currently reports manifest digest:

```text
sha256:b977d0f785d96029d8d4c0790b6bf1c2a4c72e0f26319808e7ba2e9d966a1ac3
```

The compose file intentionally pins the multi-platform **index digest**, not one architecture-specific manifest digest.

This audit corrects an earlier unverified digest value. No execution PASS is inferred from the correction.


## Git safe-directory handling

The official `node:24.21.0-bookworm` Dockerfile does not switch away from the default root user.

On Linux bind mounts, a host checkout commonly remains owned by the host UID rather than container root. Modern Git may then reject:

```text
git rev-parse HEAD
git status --porcelain
```

with:

```text
fatal: detected dubious ownership in repository
```

The M1 verification runner requires both Git commands for revision binding and clean-tree checks.

The compose service therefore supplies process-scoped Git configuration:

```text
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0=/workspace
```

This does not modify repository config or the container's global Git config. It marks only the mounted verification checkout as safe for the verification process.

A disposable ownership-mismatch probe reproduced the Git refusal without the override and returned exit code 0 with the scoped override.

This is a verification-infrastructure correction only; no M1 product/runtime behavior changed.
