# ADR-018 — M2 Verification Evidence Compatibility

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D177 through SAP-AW-D182
- **Scope:** M2 ABAP Development Agent

## Context

M2 already separates generated code from verification evidence.

A weaker contract would still allow a provider to claim "ATC PASS" or "compile PASS" while citing an unrelated approved document.
That would satisfy reference presence but violate verification honesty.

The result contract therefore needs evidence-type compatibility for verification claims.

## Decision

### SAP-AW-D177

Every M2 verification PASS/FAIL claim requires one or more evidence references from the invocation input evidence catalog.

### SAP-AW-D178

Verification evidence must be compatible with the claimed verification type.

Initial compatibility is:

- COMPILE → EXECUTION_RESULT or STATIC_ANALYSIS
- ATC → STATIC_ANALYSIS
- UNIT_TEST → TEST_RESULT
- INTEGRATION_TEST → TEST_RESULT
- AUTHORIZATION → TEST_RESULT or CONFIGURATION
- PERFORMANCE → TEST_RESULT or EXECUTION_RESULT
- PAYLOAD_CONTRACT → TEST_RESULT or EXECUTION_RESULT
- RUNTIME → EXECUTION_RESULT or LOG

### SAP-AW-D179

APPROVED_DOCUMENT, DECISION_RECORD, or generated source/work-product content cannot by themselves establish
compile, ATC, test, runtime, or performance PASS.

### SAP-AW-D180

If compatible verification evidence is absent, the Agent records the check in `required_verification` rather than inventing a PASS/FAIL claim.

### SAP-AW-D181

Verification claims remain closed over the exact M2 invocation evidence catalog; the Agent cannot create new evidence IDs.

### SAP-AW-D182

Verification evidence compatibility is a deterministic CRITICAL boundary and does not depend on a model judge.

## Consequences

- false "green" verification claims become structurally detectable
- generated ABAP remains clearly separated from executed verification
- future live compile/ATC/test tools can add evidence without changing M2 result semantics
- evaluation remains provider-independent

## Verification / fitness implications

Future deterministic M2 validation must reject at least:

- COMPILE PASS backed only by APPROVED_DOCUMENT
- ATC PASS backed by TEST_RESULT without STATIC_ANALYSIS evidence
- UNIT_TEST PASS backed only by SOURCE_CODE
- unknown evidence IDs
- verification PASS/FAIL with empty evidence refs

A required verification item without evidence remains valid and does not imply failure.

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
