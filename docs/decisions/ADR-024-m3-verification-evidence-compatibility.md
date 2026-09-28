# ADR-024 — M3 Verification Evidence Compatibility

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D237 through SAP-AW-D244
- **Scope:** M3 Review & Verification

## Context

M3 already requires verification claims to reference evidence from the invocation snapshot.

Reference existence alone is insufficient: an APPROVED_DOCUMENT must not be able to support an ATC PASS,
and generated/planning text must not stand in for compile, test, runtime, or performance evidence.

M2 established evidence-type compatibility for implementation verification.
M3 Reviewer/Test Engineer must preserve that boundary when consuming or representing verification state.

## Decision

### SAP-AW-D237

M3 verification PASS/FAIL claims require evidence references from the exact invocation evidence catalog.

### SAP-AW-D238

Verification evidence must be compatible with the claimed verification type.

Initial compatibility:

- COMPILE → EXECUTION_RESULT or STATIC_ANALYSIS
- ATC → STATIC_ANALYSIS
- UNIT_TEST → TEST_RESULT
- INTEGRATION_TEST → TEST_RESULT
- AUTHORIZATION → TEST_RESULT or CONFIGURATION
- PERFORMANCE → TEST_RESULT or EXECUTION_RESULT
- PAYLOAD_CONTRACT → TEST_RESULT or EXECUTION_RESULT
- RUNTIME → EXECUTION_RESULT or LOG
- REGRESSION → TEST_RESULT

### SAP-AW-D239

APPROVED_DOCUMENT, DECISION_RECORD, OFFICIAL_DOCUMENTATION, and generated review/test-plan text cannot by themselves
establish compile, ATC, test, runtime, performance, payload-contract, or regression PASS/FAIL.

### SAP-AW-D240

Reviewer input verification claims are validated for evidence-type compatibility before they may reduce outstanding verification debt.

### SAP-AW-D241

Reviewer result verification-debt items marked EVIDENCE_PRESENT require compatible evidence.
PENDING debt must not be presented as evidence-backed verification.

### SAP-AW-D242

Test Engineer result verification claims require both invocation evidence-reference integrity and evidence-type compatibility.

### SAP-AW-D243

The generic OTHER verification category may remain a planned/required verification item, but M3 v1 does not accept
EVIDENCE_PRESENT or PASS/FAIL claims for OTHER without a later explicit compatibility decision.

### SAP-AW-D244

Evidence-type compatibility is a deterministic CRITICAL boundary and cannot depend solely on a model judge.

## Consequences

- review acceptance cannot be strengthened by unrelated documents masquerading as executed verification
- test plans cannot inherit or invent false green verification state
- verification debt remains semantically meaningful across M2 → M3 handoff
- future compiler/ATC/test executors can add compatible evidence without changing M3 result semantics

## Verification / fitness implications

M3 deterministic evaluation must reject at least:

- COMPILE EVIDENCE_PRESENT backed only by APPROVED_DOCUMENT
- ATC PASS backed only by APPROVED_DOCUMENT
- unknown evidence IDs
- PASS/FAIL claims with empty evidence refs
- OTHER PASS/FAIL or EVIDENCE_PRESENT without a later compatibility decision

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
