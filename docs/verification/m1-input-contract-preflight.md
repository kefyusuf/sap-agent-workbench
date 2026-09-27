# M1 Technical Architect Input Contract Preflight

## Status

PASS for repository-content structural preflight.

This is not yet a Python execution record for `scripts/validate_m1_input.py`.

## Scope

The preflight covers:

- `contracts/technical-architect-input.md`
- `evals/m1/technical-architect-input.schema.json`
- `scripts/validate_m1_input.py`
- normalized inputs embedded in TA-001 through TA-004

## Case input checks

All four initial cases now contain a normalized:

```text
m1.technical-architect-input.v1
```

envelope and request:

```text
m1.technical-architect-result.v1
```

### Repository-content findings

| Case | Task ID match | Config fingerprint | Evidence refs resolve | Invalid capabilities | Raw secret keys | Output assertions |
|---|---|---|---|---|---|---|
| TA-001 | PASS | PASS | PASS | none | none | present |
| TA-002 | PASS | PASS | PASS | none | none | present |
| TA-003 | PASS | PASS | PASS | none | none | present |
| TA-004 | PASS | PASS | PASS | none | none | present |

Evidence catalogs are intentionally empty in TA-001 and TA-003 because those cases contain no VERIFIED input claim.

TA-002 and TA-004 each contain two evidence records, and all claim evidence references resolve inside their input envelope.

## Capability boundary

Every case declares only:

```text
READ
QUERY
ANALYZE
PROPOSE
```

No WRITE / DEPLOY / TRANSPORT / ADMIN capability is present.

## Secret isolation

No forbidden raw-secret key was found in the normalized input fixtures.

The preflight checked the input trees for keys such as:

- password
- client_secret
- api_key
- private_key
- access_token
- refresh_token

## Provenance binding

TA-002 canonical input fingerprint:

```text
sha256:0e53b901edf843755955da772659b47487f09b91f7d205dce1c4769fa39bb017
```

TA-003 canonical input fingerprint:

```text
sha256:b5ebfd7352cfca70bc92528146a2d4239fcdfc242c215afe1eabeec176e79d05
```

The committed TA-002 and TA-003 result examples use these exact input fingerprints and the same synthetic resolved configuration fingerprint carried by their inputs.

## What is not yet verified

This preflight does not prove:

- Python execution of `validate_m1_input.py`
- Python execution of the M1 result/self-test scripts
- provider adapter behavior
- model semantic quality
- live SAP behavior

## Gate implication

The M1 provider-neutral **input/invocation data contract design is complete**.

The next design concern is runtime invocation semantics: which fields are runtime-owned, how raw provider output becomes a normalized result, and what failure states exist before a provider-specific implementation is selected.
