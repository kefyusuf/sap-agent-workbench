# M1 Docker Image Pin Audit

## Status

PASS — image identity corrected and revalidated.

## Scope

This audit covers only the container image identity used by:

```text
compose.m1-verify.yml
```

It does not claim the M1 reference harness has executed successfully.

## Verified image metadata

Docker Hub metadata for:

```text
node:24.21.0-bookworm
```

reports:

```text
Node version: 24.21.0
multi-platform index digest:
sha256:6dac556d980b7f0e5498d08f08cee0ca67798b4ad6c23964a9214920e67758d0

linux/amd64 manifest digest:
sha256:b977d0f785d96029d8d4c0790b6bf1c2a4c72e0f26319808e7ba2e9d966a1ac3
```

Node.js release metadata independently reports:

```text
Node.js: 24.21.0
npm:     11.19.0
```

## Correction

The previously committed image digest:

```text
sha256:64af3819f9275802414d7cdc38c27e9d82bd564dec4d4da87d008255d36c63b4
```

was not supported by the Docker Hub metadata retrieved during this audit.

It has been replaced with the verified multi-platform index digest:

```text
sha256:6dac556d980b7f0e5498d08f08cee0ca67798b4ad6c23964a9214920e67758d0
```

## Why index digest

The compose verification path should remain reproducible while allowing Docker to select the correct architecture-specific
manifest from the pinned multi-platform image index.

The verification runner still checks the observed Node/npm versions at runtime and fails closed on mismatch.

## Gate implication

```text
DOCKER IMAGE IDENTITY AUDIT      PASS
DOCKER IMAGE PIN                 CORRECTED
NODE/NPM VERSION EXPECTATION     VERIFIED FROM NODE RELEASE METADATA

IMAGE PULL/EXECUTION             PENDING
npm ci                           PENDING
TYPECHECK/TEST                   PENDING
M1 REFERENCE HARNESS VERIFIED    NO
```

No provider, SAP, mutation, or product-runtime capability is introduced.
