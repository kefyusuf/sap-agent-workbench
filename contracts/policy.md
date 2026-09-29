# Policy Contract

## Definition

A Policy is an enforceable rule governing capabilities and execution eligibility.

Policy is not prompt advice.

## Canonical decisions

From least to most restrictive:

1. AUTO_EXECUTE
2. EXECUTE_AND_RECORD
3. REQUEST_APPROVAL
4. MUST_NOT_PROCEED

When multiple applicable policies match, the most restrictive decision wins.

## Resolution requirements

A side-effecting action cannot execute when policy resolution is:

- INSUFFICIENT_CONTEXT
- CONFLICTING_CONTEXT
- INVALID_ACTION

## Monotonic customization

Lower customization layers may tighten policy.
They may not weaken inherited policy.

## Invariants

Customization cannot:

- disable policy evaluation
- replace core policy semantics
- use approval to bypass MUST_NOT_PROCEED
- silently reinterpret unknown target/environment as safe

## MVP

No policy exception, emergency bypass, or super-admin override mechanism is part of the initial architecture.
