# M3 Independent Semantic Replay

## Status

PASS — 11 / 11 expected outcomes reproduced from the exact GitHub branch fixtures.

This is an independent deterministic replay of the committed contract semantics.
It is **not** the authoritative execution record for `scripts/selftest_m3_contracts.py`.

## Source

The replay read the current files directly from:

```text
feat/m3-review-test-agents
```

through the authenticated GitHub connector.

It evaluated:

```text
REVIEW-001
REVIEW-002
TEST-001
TEST-002

valid-review-acceptable-review001
valid-changes-required-review002
invalid-review-acceptable-review002
valid-test-plan-test001
valid-test-plan-test002
invalid-test-plan-missing-critical-coverage
invalid-test-pass-without-evidence
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

Summary: 11/11 expected outcomes reproduced
```

For negative cases, PASS means the result was rejected as expected.

## Reproduced input fingerprints

```text
REVIEW-001
sha256:b1a71700b2834fc7eb1694a4999f7d7c5564c83acd00fa0ed8e65cdde1e17a96

REVIEW-002
sha256:f3556956782c1213ed5ea51e87f912b79cfa4d8fe838196d3db72a3f9d93e3fe

TEST-001
sha256:0feb95b7e90704bee56debb47ff4296ae3ae6447a87f38342f38ab04797d2094

TEST-002
sha256:cedf20f7393f1c90a53f923437ea7a8fdfd46ae104dbf0de832e3279712ae928
```

These match the fingerprints bound into the committed positive/negative result examples.

## Negative-path evidence

### Architecture violation cannot be accepted

`invalid-review-acceptable-review002` was rejected because the replay observed:

- architecture alignment violation
- review-blocking finding
- outcome assertion mismatch
- invalid proceed-to-verification handoff

### Critical requirement cannot silently lose coverage

`invalid-test-plan-missing-critical-coverage` was rejected because:

- critical `REQ-002` had no coverage
- the case-required `REQ-002` coverage assertion was unsatisfied

### PASS cannot be invented without invocation evidence

`invalid-test-pass-without-evidence` was rejected because:

- `E-999` is not in the invocation evidence catalog
- the case requires zero executed verification claims

## What this proves

The exact committed fixtures are mutually consistent with the intended deterministic M3 semantics for all 11 self-test scenarios.

It increases confidence that the materialized Python validator/self-test should behave as intended.

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
M3 FIXTURE / SEMANTIC CONSISTENCY: PASS
M3 INDEPENDENT REPLAY:             11/11 PASS
M3 PYTHON SELF-TEST EXECUTION:     STILL PENDING
M3 PRODUCT RUNTIME:                BLOCKED
LIVE VERIFICATION TOOLS:           BLOCKED
```

No runtime or parent gate is opened by this replay.
