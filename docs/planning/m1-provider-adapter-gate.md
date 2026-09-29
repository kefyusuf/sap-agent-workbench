# M1 Real Provider Adapter Implementation Gate

## Status

IMPLEMENTED / DETERMINISTICALLY VERIFIED / LIVE SMOKE PENDING

The bounded implementation gate is closed.

Deterministic implementation evidence:

`docs/verification/m1-openai-provider-preflight.md`

Selected provider boundary:

```text
Provider: OpenAI
API:      Responses API
Model:    gpt-5.6-terra
Mode:     one-shot structured output
```

Implementation has not started in this document.

This gate authorizes only the smallest concrete adapter slice described below.

## Why this provider/model

Current official OpenAI API documentation confirms:

- the Responses API supports structured JSON output
- Structured Outputs can enforce a supplied JSON Schema
- `gpt-5.6-terra` is an active model positioned as a balance of intelligence and cost
- `gpt-5.6-terra` supports reasoning effort control
- Responses are stored by default unless `store: false` is supplied

For this slice, those properties fit the existing M1 contract better than adding prompt-only JSON formatting or an adapter that requires repair/retry to become usable.

The selection is deliberately an implementation choice, not a core architecture dependency.

## Exact execution configuration for this slice

```text
endpoint:          POST /v1/responses
model:             gpt-5.6-terra
reasoning.effort:  medium
store:             false
stream:            false
tools:             none
attempts:          exactly 1
```

Model selection remains external execution configuration, but the deterministic/live verification target for this first adapter slice is `gpt-5.6-terra`.

Do not use a moving alias for the verification target.

## Transport choice

Use Node.js 24 native `fetch`.

Do not add the OpenAI SDK for the first slice.

Rationale:

- the required API surface is one HTTP POST
- Node 24 already provides `fetch`
- avoiding an SDK keeps the dependency surface minimal
- provider-specific request/response types remain isolated in one adapter module
- the project can add the SDK later only if concrete complexity justifies it

This decision does not create a generic HTTP/provider abstraction.

## Secret boundary

Credential source:

```text
OPENAI_API_KEY
```

The secret belongs to external execution configuration/environment.

It must not appear in:

- TechnicalArchitectInput
- TechnicalArchitectResult
- fixtures
- logs
- evidence records
- Git-tracked configuration

Missing credentials must fail before network invocation with an adapter-configuration failure path defined by the adapter boundary; they must never be converted into a valid Agent BLOCKED result.

## Request boundary

The adapter receives the existing immutable:

```text
TechnicalArchitectInput
```

from the M1 runtime.

It may serialize:

- bounded system/instruction text
- the complete validated invocation input
- an adapter-owned JSON Schema describing only the provider semantic draft

The schema must exclude runtime-owned fields:

- `contract_version`
- `task_id`
- `provenance`

The provider must never be asked to author those fields.

## Structured output rule

Use Responses API Structured Outputs through:

```text
text.format.type = json_schema
strict = true
```

The provider-facing schema represents:

```text
TechnicalArchitectDraft
```

not:

```text
TechnicalArchitectResult
```

The existing runtime remains authoritative for binding result identity/provenance and for deterministic validation.

Structured Outputs reduce format variance but do not replace the project validator.

## Response boundary

The adapter returns only the parsed semantic draft object to:

```text
executeTechnicalArchitect(...)
```

The adapter does not:

- validate final M1 result semantics
- bind provenance
- resolve evidence references
- retry malformed semantic output
- repair invalid output
- select another model/provider
- execute tools
- call SAP

## Error mapping

The adapter must expose provider/transport failures to the existing runtime.

Required behavior:

- HTTP/network/provider refusal/error → provider invocation failure
- no hidden retry
- no fallback
- no conversion to BLOCKED
- malformed/unusable semantic draft remains visible to the existing output/result validation path

If the provider API returns a successful HTTP response that does not contain one usable structured semantic draft, the invocation must fail explicitly.

## Deterministic test seam

A test-only request seam is allowed inside the OpenAI adapter module.

Its only purpose is to supply a deterministic fake HTTP response without live network access.

Do not generalize this seam into:

- provider registry
- transport framework
- multi-provider abstraction
- retry middleware
- agent framework

## Minimum implementation files

The implementation should aim to add only:

```text
src/m1/openai-provider.ts
test/m1/openai-provider.test.ts
```

A dedicated provider-draft JSON Schema file may be added only if keeping the schema colocated in the adapter makes the implementation materially less readable or testable.

Do not split the repository into packages/workspaces.

## Required deterministic scenarios

At minimum:

1. request targets the Responses API
2. model is the externally supplied exact model
3. `store=false`
4. structured-output schema excludes runtime-owned fields
5. API key is sent only in the Authorization header
6. successful structured draft is returned to the runtime
7. HTTP/provider error becomes provider failure
8. invalid provider response shape fails explicitly
9. one invocation causes one HTTP request
10. existing M1 11/11 runtime suite remains green
11. provider-specific imports/types do not leak into M1 core

## Live smoke gate

The adapter is not VERIFIED from deterministic tests alone.

One synthetic/anonymized live invocation is required.

The live smoke must:

- use no SAP connection
- contain no customer secret/business data
- use one existing synthetic M1 case
- use `gpt-5.6-terra`
- use `store:false`
- perform one provider attempt
- capture provider/model/execution metadata separately from SAP evidence
- pass the existing M1 normalized-result validator

Credential availability is currently not established by repository evidence.

Therefore:

```text
deterministic implementation: VERIFIED
live smoke:                    CREDENTIAL-GATED / PENDING
adapter fully VERIFIED:        NO
```

## Explicit non-goals

This gate does not authorize:

- Anthropic adapter
- Gemini adapter
- second OpenAI model adapter
- provider routing
- provider fallback
- retries
- semantic repair
- streaming
- tools/function calling
- MCP
- prompt registry/platform
- response persistence
- M2 runtime
- M3 runtime
- live SAP reads
- SAP writes
- deployment/transport/admin capability
- production deployment

## Stop conditions

Stop and reopen the gate if implementation requires:

- changes to M0 capability/policy semantics
- provider-specific types in M1 core modules
- automatic repair/retry for basic operation
- more than one provider request per invocation
- a generalized provider framework
- live SAP access
- changes to M2/M3 contracts

## Acceptance sequence

```text
implement one OpenAI adapter
→ strict TypeScript compile
→ existing M1 11/11 PASS
→ adapter deterministic tests PASS
→ provider-independence static scan PASS
→ synthetic live gpt-5.6-terra smoke
→ normalized M1 result validation PASS
→ record revision-bound evidence
→ adapter VERIFIED
```

No later slice is authorized by this gate.
