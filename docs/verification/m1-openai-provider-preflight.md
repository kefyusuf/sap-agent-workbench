# M1 OpenAI Provider Adapter Deterministic Verification

## Status

PASS — deterministic adapter implementation is verified.

Live provider smoke remains credential-gated.

## Verified implementation revision

```text
aa67fdfa784f9cff3c2132e36c98f3c92070ba97
```

Toolchain:

```text
Node.js    24.21.0
npm        11.19.0
TypeScript 7.0.2
```

## Implementation boundary

Added:

```text
src/m1/openai-provider.ts
test/provider/openai-provider.test.ts
```

Package scripts add one provider-specific deterministic test command.

No OpenAI SDK dependency was added.

The adapter uses Node.js native `fetch` and the existing provider-neutral `ProviderAdapter` interface.

## Existing M1 baseline

Authoritative M1 runner:

```text
node scripts/verify_m1_reference_harness.mjs
```

Result:

```text
overall: PASS
tests:   11
pass:    11
fail:     0
```

The strict TypeScript build includes the new adapter and provider tests.

## OpenAI adapter deterministic suite

Command:

```text
npm run test:openai-provider
```

Result:

```text
tests: 8
pass:  8
fail:  0
exit:  0
```

Covered behaviors:

1. one stateless Responses API request
2. external exact model selection
3. `store=false`
4. `stream=false`
5. medium reasoning effort
6. strict structured-output JSON Schema
7. runtime-owned fields excluded from provider schema
8. API key only in Authorization header, not request body
9. valid structured draft passes the existing M1 runtime
10. HTTP/provider failure maps to existing `PROVIDER_FAILURE`
11. missing credential fails before network invocation
12. refusal remains an explicit provider failure
13. invalid provider response shape fails explicitly
14. every structured-output object is closed and fully required
15. malformed output text maps to `MALFORMED_PROVIDER_OUTPUT`

## Provider-independence scan

Static scan outside the concrete adapter:

```text
grep -RniE 'openai|api.openai.com|OPENAI_API_KEY' src/m1 --exclude='openai-provider.ts'
```

Result:

```text
0 matches
```

No provider-specific dependency or identifier leaked into existing M1 core modules.

## Foundation/downstream regression

The same exact implementation revision also produced:

```text
M0 foundation: 20/20 PASS
M2 contracts:    7/7 PASS
M3 contracts:   13/13 PASS
```

No M0 capability/safety boundary changed.

## First implementation defect

The first strict build exposed:

```text
TS2322: string | undefined is not assignable to string
```

in the single-output-text extraction path under `noUncheckedIndexedAccess`.

The adapter was corrected only after confirming exactly one output text block is present.

No compiler strictness was weakened.

## Remaining live gate

The adapter cannot be marked fully VERIFIED until one synthetic/anonymized live invocation succeeds using:

```text
Provider: OpenAI
API:      Responses API
Model:    gpt-5.6-terra
store:    false
attempts: 1
```

Repository evidence does not establish availability of an OpenAI API credential.

Current state:

```text
deterministic adapter implementation: VERIFIED
live provider smoke:                  PENDING / CREDENTIAL-GATED
adapter fully VERIFIED:               NO
```

Do not add retry, repair, fallback, tools, another provider, live SAP, or M2/M3 runtime while this live gate remains open.
