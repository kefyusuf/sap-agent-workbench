# Evidence Contract

## Definition

Evidence is verifiable support for a claim or completion condition.

## Initial evidence types

- LIVE_SYSTEM
- SOURCE_CODE
- EXECUTION_RESULT
- TEST_RESULT
- STATIC_ANALYSIS
- LOG
- CONFIGURATION
- APPROVED_DOCUMENT
- DECISION_RECORD
- OFFICIAL_DOCUMENTATION
- USER_CONFIRMATION

## Evidence strength

- DIRECT
- CORROBORATED
- INDIRECT
- UNVERIFIED

Evidence strength is distinct from source authority and reasoning confidence.

## Immutability

Evidence is append-oriented and should not be destructively overwritten.

## Revision binding

When evidence verifies a revision-sensitive artifact, it must bind to the relevant revision.

Evidence for revision A must not verify revision B.

## VERIFIED claims

A claim classified VERIFIED must reference valid supporting evidence.

## Model boundary

Model-generated text is not evidence of SAP system state.

## Provenance

Evidence preserves source and capture metadata so the path from observation to claim,
recommendation, decision, and verification can be reconstructed.
