# ADR-012 — Technical Architect Runtime Invocation Semantics

- **Status:** Accepted
- **Decision IDs:** SAP-AW-D120 through SAP-AW-D130
- **Scope:** M1 Technical Architect

## Context

M1 now has stable provider-independent input and result contracts.

Before choosing a provider SDK or runtime technology, the project needs a clear boundary between authoritative runtime state
and untrusted provider/model output.

Without that boundary, a model could fabricate provenance, provider failures could be confused with legitimate BLOCKED results,
and automatic repair/retry could hide reliability problems during early evaluation.

## Decision

### SAP-AW-D120

Final result fields `contract_version`, `task_id`, and `provenance` are runtime-owned.

Provider/model output cannot authoritatively set or override them.

### SAP-AW-D121

Provider/model output is an untrusted semantic draft until normalization and deterministic result validation succeed.

### SAP-AW-D122

The validated input snapshot becomes immutable after its deterministic fingerprint is computed.

Material input changes require a new invocation/fingerprint.

### SAP-AW-D123

Provider/model selection belongs to external execution configuration, not Agent reasoning.

### SAP-AW-D124

The initial M1 invocation performs no side-effecting SAP Tool execution.

Result capability requests are returned to orchestration and remain governed by M0 capability/policy enforcement.

### SAP-AW-D125

M1 v1 performs one provider attempt per invocation.

No automatic retry, semantic repair, provider fallback, or hidden input mutation is performed.

### SAP-AW-D126

Initial execution failure codes are:

- INVALID_INPUT
- ADAPTER_UNAVAILABLE
- PROVIDER_FAILURE
- MALFORMED_PROVIDER_OUTPUT
- RESULT_CONTRACT_VIOLATION
- EVALUATION_REJECTED

### SAP-AW-D127

A valid `BLOCKED` or `NEEDS_CLARIFICATION` Agent result is a successful runtime invocation, not an execution failure.

### SAP-AW-D128

Execution metadata is recorded separately from the normalized Agent result.

Provider/model metadata and raw response material are execution provenance, not SAP system evidence.

### SAP-AW-D129

A Technical Architect result is accepted only after runtime-owned fields are bound and deterministic result validation passes.

### SAP-AW-D130

Case-specific assertions belong only to evaluation mode.

Production/runtime contract validation must not silently depend on a test-case fixture.

## Consequences

- provenance cannot be delegated to the model
- provider reliability is measurable without hidden repair
- legitimate architectural blocking behavior stays distinct from infrastructure failures
- provider comparison remains fair and replayable
- initial runtime can remain single-turn and tool-free
- retry/tool-loop complexity is deferred to later design gates

## Verification / fitness implications

A future provider-neutral reference harness must demonstrate:

- invalid input fails before provider invocation
- input fingerprint is stable for the exact envelope
- provider cannot override runtime-owned fields
- valid BLOCKED result is accepted
- malformed output maps to MALFORMED_PROVIDER_OUTPUT
- structurally invalid normalized output maps to RESULT_CONTRACT_VIOLATION
- mutation capability request prevents result acceptance
- one invocation causes at most one provider attempt in M1 v1
- evaluation assertions are opt-in and absent from normal runtime acceptance

## Supersedes / superseded by

- **Supersedes:** none
- **Superseded by:** none
