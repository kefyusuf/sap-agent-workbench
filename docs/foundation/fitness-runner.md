# M0 Foundation Fitness Runner

## Purpose

Execute deterministic M0 foundation invariants without depending on an LLM, SAP system, external service,
or product runtime.

## Runtime

Python 3 standard library only.

This is a test-harness choice, not a product-runtime choice.

## Suites

The runner exposes three deterministic suite selections:

- `safety-kernel` — FIT-001 through FIT-012
- `resolution` — FIT-013 through FIT-020
- `all` — both suites in stable directory/path order

The default remains `safety-kernel` so the original critical gate can be executed independently.

## Commands

From the repository root:

```bash
python scripts/run_foundation_fitness.py
python scripts/run_foundation_fitness.py --suite resolution
python scripts/run_foundation_fitness.py --suite all
```

Windows environments may use `py -3` instead of `python`.

Optional machine-readable output:

```bash
python scripts/run_foundation_fitness.py --suite all --json
```

Optional file report:

```bash
python scripts/run_foundation_fitness.py --suite all --report build/foundation-fitness.json
```

## Runner responsibilities

The runner:

1. loads `evals/foundation/scenario.schema.json`
2. discovers the selected fixture suite(s)
3. validates fixture structure against the committed M0 schema subset
4. rejects duplicate scenario IDs
5. rejects unknown deterministic scenario kinds
6. executes each scenario
7. compares observed result with the fixture's expected `then`
8. emits PASS/FAIL
9. returns a non-zero process status on any CRITICAL failure
10. records a deterministic configuration fingerprint

## Exit codes

- `0` — no CRITICAL scenario failed
- `1` — one or more CRITICAL scenarios failed
- `2` — runner/fixture/schema error prevented a valid run

REQUIRED failures remain visible in the report and must still be resolved before M0 closure even though only CRITICAL
failures determine process exit code.

## Configuration fingerprint

Runner contract v2 computes a deterministic SHA-256 fingerprint from:

- runner contract version
- selected suite identity
- committed scenario schema
- normalized selected fixture content in stable path order

The fingerprint identifies the exact foundation configuration evaluated by that run.
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

## CI

`.github/workflows/foundation-fitness.yml` is configured to execute `--suite all`.

CI availability is operational infrastructure, not a substitute for the deterministic runner contract.
A CI infrastructure failure must be distinguished from a fixture/runner fitness failure.
