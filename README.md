# SAP Agent Workbench

Provider-independent, evidence-aware SAP engineering agent workbench.

## Status

Verified baseline through M3 is merged to `main`.

Current state:

- M0 foundation architecture and deterministic fitness: VERIFIED
- M1 provider-neutral Technical Architect reference runtime: VERIFIED
- M2 ABAP Development contracts/evaluation tooling: VERIFIED
- M3 Reviewer/Test Engineer contracts/evaluation tooling: VERIFIED
- stacked M0 → M1 → M2 → M3 lineage: MERGED / NORMALIZED
- SAP-system mutation capabilities: NOT REGISTERED
- live SAP adapters: NOT STARTED
- real provider adapter: NOT STARTED

The selected next implementation slice is exactly one real M1 provider adapter. Its provider/model and adapter boundary are defined by the dedicated implementation gate before code is added.

## Initial scope

- SAP Technical Architect
- ABAP development assistance
- SAP review and test support
- S/4HANA modernization guidance
- BTP and integration guidance
- Fiori/OData technical analysis
- Incident/RCA assistance

Initial runtime capabilities remain limited to read/query/analyze/propose semantics.

SAP system mutation, deployment, transport, and administrative capabilities remain out of scope for the MVP.

See:

- `PROJECT.md`
- `docs/foundation/`
- `docs/m1/`
- `docs/m2/`
- `docs/m3/`
- `docs/planning/next-slice-reassessment.md`
