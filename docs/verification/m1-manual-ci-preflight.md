# M1 Manual Repository-Native Verification Workflow

## Status

MATERIALIZED / STATIC PREFLIGHT PASS / EXECUTION PENDING

## Purpose

Provide a repository-native verification entry point for the exact M1 reference-harness gate without enabling automatic CI
while GitHub Actions capacity is unavailable.

Workflow:

```text
.github/workflows/m1-reference-harness.yml
```

## Trigger policy

The workflow currently exposes only:

```text
workflow_dispatch
```

It intentionally does **not** trigger on:

- push
- pull_request

This prevents avoidable failing/red runs while the user-reported GitHub Actions capacity constraint remains active.

Automatic PR verification can be added only after Actions capacity is restored and the manual workflow has produced a valid run.

## Execution path

The workflow:

1. checks out the exact selected revision
2. sets up Node.js 24.21.0
3. uses the committed package lock for npm caching
4. prints Node/npm versions
5. runs:
   `node scripts/verify_m1_reference_harness.mjs`
6. prints the revision-bound JSON verification report even when the verification step fails, when that report exists

Permissions:

```text
contents: read
```

Job timeout:

```text
10 minutes
```

## Static workflow preflight

Committed workflow blob:

```text
6782ca90218f2a184c95bacd685d41417d84512f
```

Checks:

```text
workflow_dispatch only             PASS
contents permission read-only      PASS
Node version = 24.21.0             PASS
package-lock cache binding         PASS
exact verification runner command  PASS
always-print report path           PASS
10-minute timeout                  PASS
```

## Important limitation

The workflow has not been executed because GitHub Actions capacity is currently unavailable according to the repository owner.

Therefore this document does not claim:

- setup-node execution
- npm ci success
- TypeScript compile success
- Node test success
- GitHub-hosted runner success

## Future activation sequence

When Actions capacity returns:

```text
manual workflow_dispatch
→ exact M1 runner executes
→ inspect revision-bound JSON/log evidence
→ require PASS
→ only then consider automatic pull_request trigger
```

## Gate implication

```text
LOCAL/DOCKER VERIFICATION PATH     MATERIALIZED
MANUAL REPOSITORY-NATIVE WORKFLOW  MATERIALIZED
WORKFLOW STATIC PREFLIGHT          PASS

WORKFLOW EXECUTION                 PENDING
M1 EXACT VERIFICATION              PENDING
M1 REFERENCE HARNESS VERIFIED      NO
REAL PROVIDER GATE                 CLOSED
```

No provider, SAP, mutation, or product-runtime capability is introduced.
