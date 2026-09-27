# M1 Technical Architect Evaluation Fixtures

These fixtures evaluate the SAP Technical Architect Agent defined by ADR-008 through ADR-010.

They are intentionally synthetic/anonymized.

## Fixture philosophy

Cases specify:

- input requirement
- scoped context/evidence
- material unknowns/conflicts
- semantic expected properties
- semantic prohibited properties
- critical expectations
- machine-readable `output_assertions`

They do not prescribe exact prose or one LLM provider.

## Initial cases

- TA-001 — external sales-order notification with insufficient system-specific evidence
- TA-002 — project integration fact shadows organization default
- TA-003 — conflicting authentication facts require blocking/clarification
- TA-004 — S/4HANA modernization with evidenced direct table update

## Result contract

Canonical machine-readable result schema:

```text
evals/m1/technical-architect-result.schema.json
```

Contract:

```text
m1.technical-architect-result.v1
```

Deterministic validator:

```text
python scripts/validate_m1_result.py <result.json> --case <TA-case.json>
```

Self-test:

```text
python scripts/selftest_m1_result_contract.py
```

## Evaluation split

Deterministic validation checks structural/safety invariants and machine-readable case assertions.

Semantic checks such as requirement fidelity, architecture option quality, and unsupported implicit SAP claims remain
Agent-quality evaluation concerns and are not silently converted into deterministic string matching.

No live SAP adapter is required for this set.
