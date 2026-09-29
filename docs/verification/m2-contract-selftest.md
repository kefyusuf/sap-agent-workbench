# M2 Deterministic Contract Self-Test Verification

## Status

PASS

## Execution environment

```text
Python 3.13.5
exit code: 0
```

## Result

```text
PASS  ABAP-001-input
PASS  ABAP-002-input
PASS  ABAP-003-input
PASS  ABAP-004-input
PASS  valid-ready-abap001
PASS  valid-blocked-abap002
PASS  invalid-atc-pass-with-document
Summary: 7/7 PASS
```

## Exact committed-content identity

The verification workspace was reconstructed from the GitHub-connected branch content.
The executed validator and self-test bytes match the Git blob identities returned by GitHub:

| Path | Git blob SHA |
|---|---|
| `scripts/validate_m2_contracts.py` | `65854596fea6ca08ac33939fa91b9c4b9dabb59b` |
| `scripts/selftest_m2_contracts.py` | `fcdb952b6a19b92ea35869fc625b418b948ea7e3` |
| `evals/m2/abap-development/ABAP-001.json` | `c80c69c12dedfec1a1efe13b74b14ead95715987` |
| `evals/m2/abap-development/ABAP-002.json` | `8cf1ba8653c69a28d6754ec114ff6aec692e4a87` |
| `evals/m2/abap-development/ABAP-003.json` | `a3b0ec0b1df6290edfdd8c92760ac1fa9c082d8e` |
| `evals/m2/abap-development/ABAP-004.json` | `ad7c2d272ccd484fd69d741f9d2300748573a381` |
| `evals/m2/result-examples/valid-ready-abap001.json` | `a82dbd8767bca68317523eccf2f269dda6f808dd` |
| `evals/m2/result-examples/valid-blocked-abap002.json` | `809e143ba9d6dcaca9b251d9a8bb4b4aec528795` |
| `evals/m2/result-examples/invalid-atc-pass-with-document.json` | `98e35f8f5c9fdc13c887f3f6699d6691fe70d728` |

The canonical case input fingerprints were also reproduced:

```text
ABAP-001
sha256:49e80ef7d0bbaec545de3e87d7f97167fe885f797f6b73a0475590de97841f54

ABAP-002
sha256:2fe8ead84e065d658667b857be8e6e75bd7a74a3c026c5aa65d8ee73d27488b0

ABAP-003
sha256:406516383ef6a6be43034303ec962ef0335e65fd239ca8ffc850db055dff1d19

ABAP-004
sha256:a5b501867e585f6f3066b6d847f1d74a44c1a567c760d552356bc741dcdb52c7
```

## Verified invariants

The passing self-test demonstrates the committed deterministic tooling accepts:

- all four normalized M2 input cases
- a valid WORK_PRODUCT_READY result
- a valid BLOCKED result

and rejects:

- ATC PASS backed only by APPROVED_DOCUMENT evidence

The negative case therefore confirms the ADR-018 verification-evidence compatibility boundary is executable.

## Gate implication

```text
M2 DETERMINISTIC CONTRACT TOOLING: VERIFIED
M2 PRODUCT RUNTIME:                STILL BLOCKED
```

This verification does not override the parent M1 reference-harness gate.
No provider invocation, SAP connection, ABAP compiler, ATC service, transport, or mutation was used.
