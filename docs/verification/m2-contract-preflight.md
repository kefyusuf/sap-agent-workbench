# M2 Contract & Evaluation Tooling Preflight

## Status

PASS for repository-content/static contract integrity.

Executable Python self-test evidence is still pending.

## Decision continuity

M2 currently covers:

```text
SAP-AW-D146 through SAP-AW-D191
```

Repository inspection found:

```text
unique decision IDs: 46
missing IDs:         0
cross-ADR duplicates: 0
```

## Contracts

Input:

```text
m2.abap-development-input.v1
evals/m2/abap-development-input.schema.json
```

Result:

```text
m2.abap-development-result.v1
evals/m2/abap-development-result.schema.json
```

The result contract distinguishes:

```text
WORK_PRODUCT_READY
NEEDS_CLARIFICATION
BLOCKED
```

and explicitly separates:

- existing object facts
- proposed new objects
- generated work products
- evidence-backed verification claims
- review readiness
- delivery/transport readiness

## Normalized case integrity

All four cases contain normalized M2 input envelopes and machine-readable output assertions.

Static findings:

| Case | Blocking input unknown | Existing object refs | Mutation capabilities |
|---|---:|---|---|
| ABAP-001 | no | OBJ-001, OBJ-002 | none |
| ABAP-002 | yes | none | none |
| ABAP-003 | yes | none | none |
| ABAP-004 | no | OBJ-001 | none |

All requirement/object evidence references resolve inside their case evidence catalogs.

Architecture handoff and resolved-configuration fingerprints have the required SHA-256 format.

## Canonical example fingerprints

The exact canonical M2 input fingerprints used by the committed examples are:

```text
ABAP-001
sha256:49e80ef7d0bbaec545de3e87d7f97167fe885f797f6b73a0475590de97841f54

ABAP-002
sha256:2fe8ead84e065d658667b857be8e6e75bd7a74a3c026c5aa65d8ee73d27488b0
```

The valid result examples carry those fingerprints together with the matching configuration and architecture-handoff fingerprints.

## Verification-evidence negative case

`invalid-atc-pass-with-document.json` intentionally claims:

```text
ATC = PASS
evidence_ref = E-003
```

For ABAP-001, `E-003` is:

```text
APPROVED_DOCUMENT
```

not:

```text
STATIC_ANALYSIS
```

The deterministic validator is therefore expected to reject this result under ADR-018.

## Evaluation tooling

Materialized:

```text
scripts/validate_m2_contracts.py
scripts/selftest_m2_contracts.py
```

The validator is Python-standard-library-only and performs no:

- provider invocation
- network request
- SAP call
- ABAP compile
- ATC execution
- mutation

The self-test is designed to cover:

```text
4 normalized input cases
1 valid WORK_PRODUCT_READY result
1 valid BLOCKED result
1 invalid false-ATC-verification result
----------------------------------------
7 scenarios
```

## Stack scope

Compared with `feat/m1-technical-architect`:

```text
runtime source changes: 0
package/runtime changes: 0
live provider changes: 0
live SAP changes: 0
```

Only M2 docs/contracts/evals and deterministic evaluation scripts are added.

## Not yet verified

This report does not claim execution of:

```text
python scripts/selftest_m2_contracts.py
```

The committed self-test must execute successfully before the M2 contract/evaluation tooling is marked VERIFIED.

This does not unblock the M2 product runtime; parent M1 reference-harness verification remains a separate prerequisite.

## Gate result

```text
M2 AGENT BOUNDARY                 COMPLETE
M2 EVALUATION CONTRACT            COMPLETE
M2 INPUT/RESULT CONTRACTS         COMPLETE
M2 CASE NORMALIZATION             COMPLETE
M2 EVIDENCE-COMPATIBILITY DESIGN  COMPLETE
M2 DETERMINISTIC VALIDATOR        MATERIALIZED
M2 STATIC PREFLIGHT               PASS

M2 VALIDATOR EXECUTION            PENDING
M2 PRODUCT RUNTIME                BLOCKED
M2 REAL PROVIDER                  BLOCKED
M2 LIVE SAP                       BLOCKED
```
