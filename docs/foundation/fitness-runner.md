# M0 Foundation Fitness Runner

## Purpose

Execute the deterministic Foundation Safety Kernel without depending on an LLM, SAP system, external service,
or product runtime.

## Runtime

Python 3 standard library only.

This is a test-harness choice, not a product-runtime choice.

## Command

From the repository root:

```bash
python scripts/run_foundation_fitness.py
```

Windows environments may also use:

```powershell
py -3 scripts/run_foundation_fitness.py
```

Optional machine-readable report:

```bash
python scripts/run_foundation_fitness.py --json
```

Optional file report:

```bash
python scripts/run_foundation_fitness.py --report build/foundation-fitness.json
```

## Runner responsibilities

The runner:

1. loads `evals/foundation/scenario.schema.json`
2. discovers `FIT-*.json` under `evals/foundation/safety-kernel/`
3. validates fixture structure against the committed M0 schema subset
4. rejects duplicate scenario IDs
5. rejects unknown deterministic scenario kinds
6. executes each scenario
7. compares observed result with the fixture's expected `then`
8. emits PASS/FAIL
9. returns a non-zero process status on any CRITICAL failure
10. records a deterministic configuration fingerprint

## Exit codes

- `0` — all CRITICAL scenarios PASS
- `1` — one or more CRITICAL scenarios FAIL
- `2` — runner/fixture/schema error prevented a valid run

## Configuration fingerprint

For the static M0 Safety Kernel, the runner computes a deterministic SHA-256 fingerprint from:

- runner contract version
- committed scenario schema
- normalized active fixture content in stable path order

This fingerprint identifies the exact foundation configuration evaluated by that run.
It is not a Git commit identifier and does not replace revision provenance.

## Scope boundary

The runner does not:

- call an LLM
- call SAP
- execute external tools
- mutate project configuration
- decide the future application runtime
- evaluate SAP domain-answer quality

It exists only to prove M0 foundation invariants.
