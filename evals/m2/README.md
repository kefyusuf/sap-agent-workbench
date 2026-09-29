# M2 ABAP Development Evaluation Fixtures

These fixtures evaluate the design boundary defined by ADR-015 through ADR-018.

They are synthetic/anonymized and intentionally do not require a live SAP system.

## Initial cases

- ABAP-001 — sufficient scoped BAdI-style implementation context
- ABAP-002 — architecture selects extension strategy but exact extension object is unknown
- ABAP-003 — S/4HANA modernization forbids direct standard-table mutation
- ABAP-004 — existing PI/PO integration path must remain unchanged

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

## Fixture philosophy

Each case now contains:

- normalized provider-independent `input`
- human-readable expected properties
- human-readable forbidden properties
- CRITICAL expectations
- machine-readable `output_assertions`

The current assertions cover status, architecture alignment, required existing-object references,
work-product cardinality, blocking-unknown behavior, review readiness, and forbidden SAP mutation capabilities.

## Core M2 distinctions

```text
existing object fact
!=
proposed new object

generated code
!=
compile / ATC / test evidence

WORK_PRODUCT_READY
!=
workflow DONE / transport ready
```

## Parent gate

The M2 fixture/contract design may progress while the M1 reference harness verification is pending.

M2 runtime implementation remains blocked until the parent gate is satisfied.
