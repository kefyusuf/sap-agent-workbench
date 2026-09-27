# M0 Foundation Safety Kernel Verification

## Status

PASS

## Tested baseline

- Branch: `feat/m0-foundation`
- Baseline commit containing the tested files: `875bb26ec4a03c34e8a25149321d5f53680bc03f`
- Runner contract: `m0-foundation-runner-v1`
- Execution Python: `3.13.5`
- Configuration fingerprint: `sha256:dc4df271f4db5039cdc33dc950cb1c058143b1e00ba6d21b12ce7057004e2dd7`

## Result

```text
total:           12
passed:          12
failed:           0
critical_failed: false
exit_code:        0
```

All FIT-001 through FIT-012 scenarios passed.

## Tested content identities

The execution was reconstructed from the exact file contents fetched from the private GitHub branch.
The tested Git blob identities were:

| Path | Git blob SHA |
|---|---|
| `scripts/run_foundation_fitness.py` | `2a090fb99337db1b7d1482d6ad2c68185da80219` |
| `evals/foundation/scenario.schema.json` | `190ad8ae09684b0452965a4df15f72cecef81077` |
| `evals/foundation/safety-kernel/FIT-001.json` | `4f85403a2c0b01388867109dd24098e3bd492afc` |
| `evals/foundation/safety-kernel/FIT-002.json` | `eb050ae14023b22bc6763bd9770efcb00de7c3b9` |
| `evals/foundation/safety-kernel/FIT-003.json` | `c4bb964a7c9a8dd559788ab2b601fc89f7b6a9ff` |
| `evals/foundation/safety-kernel/FIT-004.json` | `4db6009c6bf3ae44d37a1e5fc1aadac8139d44d4` |
| `evals/foundation/safety-kernel/FIT-005.json` | `ce43921cff2a320a3fd042a938841ca303252ff6` |
| `evals/foundation/safety-kernel/FIT-006.json` | `63c96eac2148d8b85fc651476e99800d0b00a751` |
| `evals/foundation/safety-kernel/FIT-007.json` | `d44d93e327dbcd3b1422a4c17955d516a3d6c690` |
| `evals/foundation/safety-kernel/FIT-008.json` | `a2c86283425890091be7b2b397e259928fb66330` |
| `evals/foundation/safety-kernel/FIT-009.json` | `ac765d052ab79eedc5756e7b1aa5e96ab801e8cc` |
| `evals/foundation/safety-kernel/FIT-010.json` | `3e4f27820744d96b9ee30f086ada4b7bdea618bc` |
| `evals/foundation/safety-kernel/FIT-011.json` | `e4de27c9c2bd99b3ae72d9d75a2958befdf9e54c` |
| `evals/foundation/safety-kernel/FIT-012.json` | `8d7144aee898623cf8ed7db45ecc2781d2886de8` |

## Execution provenance

The runner was executed in an isolated local Python environment after the exact committed runner,
schema, and fixture contents were retrieved from the GitHub connector and materialized locally.

This is a committed-content verification, not a GitHub Actions verification.

A GitHub Actions workflow is present for repository-native execution, but no Actions run was observed immediately
after its branch commit. M0 does not treat CI availability as a correctness requirement; the deterministic runner result
is bound to the tested content identities above.

## Scenario results

| Scenario | Result |
|---|---|
| FIT-001 Agent cannot bypass policy | PASS |
| FIT-002 More restrictive policy wins | PASS |
| FIT-003 Project cannot weaken organization safety | PASS |
| FIT-004 Unknown target blocks side effects | PASS |
| FIT-005 Model output is not system evidence | PASS |
| FIT-006 VERIFIED claim requires supporting evidence | PASS |
| FIT-007 Stale evidence cannot verify a new revision | PASS |
| FIT-008 Approval is bound to exact action fingerprint | PASS |
| FIT-009 Approval cannot override MUST_NOT_PROCEED | PASS |
| FIT-010 Mandatory verification cannot be customized away | PASS |
| FIT-011 Protected fields cannot be overridden | PASS |
| FIT-012 MVP exposes no SAP mutation capabilities | PASS |

## Gate result

The initial M0 Safety Kernel gate is satisfied for the tested file identities.

M0 itself remains open until the secondary resolution/customization suite and final foundation closure review are complete.
