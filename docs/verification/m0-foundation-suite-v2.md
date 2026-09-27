# M0 Foundation Suite Verification — Runner v2

## Status

PASS for deterministic local content-equivalent execution.

M0 remains open pending final closure review.

## Runner

- Runner contract: `m0-foundation-runner-v2`
- Python: `3.13.5`
- Product runtime implication: none

## Verified suites

### Safety Kernel

```text
suite:            safety-kernel
total:            12
passed:           12
failed:            0
critical_failed: false
exit_code:         0
fingerprint:
sha256:8f4648e93baa7fd401017cb9690beecd3a699abcb9e76a28038792776e896178
```

### Resolution Suite

```text
suite:            resolution
total:             8
passed:            8
failed:            0
critical_failed: false
exit_code:         0
fingerprint:
sha256:82564885e1628269ff6ce5b927487d38c78b9b6687ff2bb355ae293af4cc228f
```

### Combined Foundation Suite

```text
suite:            all
total:            20
passed:           20
failed:            0
critical_failed: false
exit_code:         0
fingerprint:
sha256:daebc644923708fbed58f25a36bf6db7f03ccf41cfb279c40e1642ccf1fb03cc
```

## Resolution coverage added

FIT-013 through FIT-020 verify:

- more-specific context shadowing with provenance preservation
- same-scope material conflict surfacing
- Customization Pack compatibility
- declared Workflow hook acceptance
- undeclared Workflow hook rejection
- Knowledge supersession without destructive history loss
- raw-secret rejection from customization content
- capability availability remaining distinct from Policy authorization

FIT-019 is CRITICAL. The remaining secondary scenarios are REQUIRED.

## Execution provenance

The GitHub-connected branch content was materialized into an isolated local execution workspace.

For the runner source, a normalized source comparison between the GitHub branch file and the executed local file matched:

```text
normalized FNV-1a 32: f579f3c1
normalized length: 20931
normalized lines:  555
```

The difference from raw Git blob identity was formatting-only in the reconstructed local copy; normalized source content
matched the committed runner source used as the implementation basis.

JSON fixtures were reconstructed from their committed payloads. The runner canonicalizes JSON for configuration
fingerprinting, so formatting differences do not affect the recorded suite fingerprints.

## GitHub Actions observation

Repository-native GitHub Actions execution is configured with:

```text
python3 scripts/run_foundation_fitness.py --suite all
```

Multiple push-triggered workflow runs were observed, but they completed with failure before observable job steps were
returned by the GitHub connector. The latest inspected job exposed no steps and no retrievable job log through the connector.

Therefore:

- deterministic foundation execution is PASS locally
- GitHub Actions execution is currently an operational/CI issue
- the root cause of the CI failure is not yet verified
- the CI failure must not be mislabeled as a foundation invariant failure

## Gate result

For the committed foundation semantics represented by runner v2 and FIT-001 through FIT-020:

- all CRITICAL scenarios passed locally
- all REQUIRED scenarios passed locally
- no deterministic foundation failure was observed

The remaining M0 task is the final closure review, including deciding whether the unresolved CI execution issue is
a non-safety operational blocker or must be resolved before merging the foundation branch.
