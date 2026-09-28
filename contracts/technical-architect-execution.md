# SAP Technical Architect Execution Contract

## Purpose

Define provider-neutral runtime semantics for executing the M1 SAP Technical Architect Agent.

This contract sits between:

`m1.technical-architect-input.v1`

and:

`m1.technical-architect-result.v1`

It does not select a provider SDK or product implementation language.

## Authoritative runtime-owned fields

The final normalized result contains fields that are **owned by the runtime**, not trusted from provider/model output:

- `contract_version`
- `task_id`
- `provenance.input_fingerprint`
- `provenance.configuration_fingerprint`

The runtime derives them from the validated input and execution configuration.

A provider response may not override these fields.

## Provider semantic draft

Provider/model output is treated as an untrusted semantic draft.

The draft may contribute:

- status
- requirement summary
- scope interpretation
- claims
- unknowns
- conflicts
- existing-solution discovery
- solution options
- proposal
- required verification
- implementation handoff
- requested capabilities
- next action

It is not a valid Technical Architect result until runtime normalization and deterministic validation succeed.

## Invocation sequence

Canonical M1 v1 sequence:

1. receive input envelope
2. validate input contract
3. compute deterministic input fingerprint
4. freeze the validated input snapshot
5. select a provider adapter from external execution configuration
6. serialize the immutable semantic input for that adapter
7. invoke the provider once
8. parse provider output into a semantic draft
9. attach runtime-owned fields
10. validate the normalized result contract
11. validate result evidence/source references against the immutable invocation input
12. return either an accepted result or a typed execution failure

Evaluation mode may additionally apply case-specific assertions after step 10.

## Input immutability

After fingerprint calculation, the semantic input snapshot is immutable for the invocation.

If task context changes, a new input envelope and fingerprint are required.

A retry against materially changed input is a new invocation, not continuation of the prior one.

## Provider selection

The Agent does not choose its provider/model.

Provider/model selection belongs to external execution configuration.

This preserves:

- provider independence
- reproducibility
- policy separation
- evaluation comparability

## Capability requests

M1 provider execution does not execute SAP side effects.

If the result contains `requested_capabilities`, they are only requests/proposals for later orchestration.

They remain subject to the M0 capability/policy path.

The runtime must reject mutation/admin capability requests before accepting the result.

## Failure taxonomy

Initial execution failures:

- `INVALID_INPUT`
- `ADAPTER_UNAVAILABLE`
- `PROVIDER_FAILURE`
- `MALFORMED_PROVIDER_OUTPUT`
- `RESULT_CONTRACT_VIOLATION`
- `EVALUATION_REJECTED` — evaluation mode only

Failure is distinct from an Agent result whose status is:

- `NEEDS_CLARIFICATION`
- `BLOCKED`

A valid BLOCKED result is a successful invocation outcome, not a runtime failure.

## Retry / repair

M1 v1 performs one provider attempt per invocation.

It does not silently:

- ask the provider to repair malformed output
- retry a semantically invalid result
- switch models/providers
- mutate the input/context

Automatic retry or repair requires a later explicit design decision.

This makes initial evaluation results attributable to one input, one configuration, and one provider attempt.

## Execution record

Execution metadata is stored separately from the normalized Agent result.

A minimal execution record may include:

- execution ID
- input fingerprint
- resolved configuration fingerprint
- adapter identity/version
- provider/model execution metadata
- start/end timestamps
- outcome
- failure code when applicable
- raw provider-response reference when retained
- normalized result reference when accepted

Provider/model metadata is execution provenance, not SAP system evidence.

## Raw provider output

Raw provider output is not:

- verified SAP evidence
- a normalized result
- a policy decision
- a workflow completion signal

If retained, it is diagnostic/evaluation material subject to applicable data-handling rules.

## Acceptance rule

A provider invocation produces an accepted Technical Architect result only when:

1. input validation passed
2. input fingerprint was computed
3. provider output was parsed
4. runtime-owned fields were attached
5. deterministic result validation passed
6. result evidence/source provenance resolves against the invocation input snapshot

In evaluation mode, case-specific deterministic assertions may add an additional acceptance gate.

Semantic SAP architecture quality remains a separate evaluation layer.
