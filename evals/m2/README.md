# M2 ABAP Development Evaluation Fixtures

These fixtures evaluate the design boundary defined by ADR-015 and ADR-016.

They are synthetic/anonymized and intentionally do not require a live SAP system.

## Initial cases

- ABAP-001 — sufficient scoped BAdI-style implementation context
- ABAP-002 — architecture selects extension strategy but exact extension object is unknown
- ABAP-003 — S/4HANA modernization forbids direct standard-table mutation
- ABAP-004 — existing PI/PO integration path must remain unchanged

## Fixture purpose

The first cases test:

- architecture fidelity
- existing-vs-proposed object identity
- missing-context behavior
- verification honesty
- no-mutation capability boundary
- implementation handoff quality

They do not yet define the final M2 input/result contract.
