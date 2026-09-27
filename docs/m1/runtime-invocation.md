# M1 Runtime Invocation Semantics

## Status

Design contract only.

No provider SDK or live SAP adapter is introduced here.

## Pipeline

```text
TechnicalArchitectInput
        │
        ▼
Input Validator
        │
        ▼
Input Fingerprint
        │
        ▼
Immutable Input Snapshot
        │
        ▼
Externally Selected Provider Adapter
        │
        ▼
Provider Raw Output
        │
        ▼
Parse / Normalize Draft
        │
        ▼
Bind Runtime-Owned Fields
        │
        ▼
TechnicalArchitectResult Validator
        │
        ├── invalid → typed execution failure
        │
        ▼
Accepted TechnicalArchitectResult
```

Evaluation mode adds:

```text
Accepted Result Candidate
        ↓
Case Assertions
        ↓
Evaluation Accepted / EVALUATION_REJECTED
```

## Runtime-owned vs model-owned boundary

### Runtime-owned

- result contract version
- task ID
- input fingerprint
- resolved configuration fingerprint

### Provider semantic draft

- status
- requirement summary
- scope
- claims
- unknowns
- conflicts
- discovery
- options
- proposal
- verification
- handoff
- requested capabilities
- next action

This distinction prevents a model from fabricating provenance binding.

## BLOCKED is not execution failure

Example:

A provider returns a valid result with:

```text
status = BLOCKED
proposal = null
material unresolved conflict = present
```

If the normalized result passes contract validation, the invocation is successful.

The Agent correctly refusing to make an unsupported architecture choice is product behavior, not provider failure.

## Provider failures

A transport/API/provider failure never becomes:

`BLOCKED`

It becomes:

`PROVIDER_FAILURE`

This keeps engineering uncertainty separate from infrastructure failure.

## No hidden repair

Initial M1 must expose malformed/invalid provider output rather than hiding it behind automatic retries.

This is particularly important while comparing providers and evaluating:

- structured-output reliability
- hallucination pressure
- blocker handling
- provenance preservation

## Future extension points

Outside the current gate:

- provider retry policy
- structured-output repair
- provider fallback
- tool loops
- live SAP retrieval
- caching
- streaming
- cost/token optimization

Each requires a later explicit decision if introduced.
