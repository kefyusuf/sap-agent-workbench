# M3 Independent Semantic Replay

## Status

PASS — 13 / 13 expected outcomes reproduced from the exact current GitHub branch fixtures.

This is an independent deterministic semantic replay.
It is **not** the authoritative Python-process execution record for `scripts/selftest_m3_contracts.py`.

## Current scope

The replay reflects ADR-024 verification-evidence compatibility hardening.

It evaluates:

```text
4 normalized input cases
9 positive/negative result cases
-------------------------------
13 scenarios
```

## Result

```text
PASS  REVIEW-001-input
PASS  REVIEW-002-input
PASS  TEST-001-input
PASS  TEST-002-input

PASS  valid-review-acceptable-review001
PASS  valid-changes-required-review002
PASS  invalid-review-acceptable-review002

PASS  valid-test-plan-test001
PASS  valid-test-plan-test002
PASS  invalid-test-plan-missing-critical-coverage
PASS  invalid-test-pass-without-evidence

PASS  invalid-review-compile-with-document
PASS  invalid-test-atc-with-document

Summary: 13/13 expected outcomes reproduced
```

For negative cases, PASS means the result was rejected as expected.

## Reproduced canonical input fingerprints

```text
REVIEW-001
sha256:b1a71700b2834fc7eb1694a4999f7d7c5564c83acd00fa0ed8e65cdde1e17a96

REVIEW-002
sha256:f3556956782c1213ed5ea51e87f912b79cfa4d8fe838196d3db72a3f9d93e3fe

TEST-001
sha256:b0312a283ffcd74b4a46062f8673947bd30bc0e964c3a90279b45439bea4d9fe

TEST-002
sha256:cedf20f7393f1c90a53f923437ea7a8fdfd46ae104dbf0de832e3279712ae928
```

TEST-001 changed from the earlier replay because the hardened fixture now contains an APPROVED_DOCUMENT evidence record used
to prove that evidence existence is insufficient when its type is incompatible with an executed verification claim.

## Negative-path evidence

### Architecture violation cannot be accepted

`invalid-review-acceptable-review002` is rejected because:

- architecture alignment is violated
- a review-blocking finding remains
- REVIEW_ACCEPTABLE is inconsistent with the case
- proceed-to-verification is inconsistent with the case

### Critical requirement coverage cannot silently disappear

`invalid-test-plan-missing-critical-coverage` is rejected because:

- critical `REQ-002` has no coverage
- the case-required `REQ-002` assertion is unsatisfied

### PASS cannot reference absent evidence

`invalid-test-pass-without-evidence` is rejected because:

- `E-999` is absent from the invocation evidence catalog
- the case requires zero executed verification claims

### Reviewer cannot use a document as compile evidence

`invalid-review-compile-with-document` is rejected because:

```text
claim/debt: COMPILE EVIDENCE_PRESENT
evidence:   E-001
type:       APPROVED_DOCUMENT
```

but COMPILE requires:

```text
EXECUTION_RESULT or STATIC_ANALYSIS
```

### Test Engineer cannot use a document as ATC evidence

`invalid-test-atc-with-document` is rejected because:

```text
claim:    ATC PASS
evidence: E-001
type:     APPROVED_DOCUMENT
```

while ATC requires:

```text
STATIC_ANALYSIS
```

The case also requires zero executed verification claims.

## Decision/tooling consistency

Current M3 decision continuity:

```text
SAP-AW-D192 through SAP-AW-D244
unique: 53
missing: 0
cross-ADR duplicates: 0
```

Current validator/self-test static scan:

```text
provider SDK references: 0
SAP SDK references:      0
HTTP clients:            0
subprocess/system calls: 0
```

## What this proves

The current committed fixtures are mutually consistent with the hardened M3 deterministic semantics for all 13 self-test scenarios.

The replay specifically confirms the new evidence-type compatibility negatives behave as intended.

## What this does not prove

This replay does not replace:

```text
python scripts/selftest_m3_contracts.py
```

It does not prove:

- Python syntax/import execution of the committed validator
- exact execution of the committed self-test module
- Python-process exit code
- provider/model behavior
- SAP/compiler/ATC/test execution

## Gate implication

```text
M3 FIXTURE / SEMANTIC CONSISTENCY:      PASS
M3 INDEPENDENT HARDENED REPLAY:         13/13 PASS
M3 VERIFICATION-EVIDENCE COMPATIBILITY: PASS (semantic replay)
M3 EXACT PYTHON SELF-TEST EXECUTION:    PENDING

M3 PRODUCT RUNTIME:                     BLOCKED
LIVE VERIFICATION TOOLS:                BLOCKED
```

No runtime or parent gate is opened by this replay.
