# Approval Contract

## Definition

Approval authorizes an exact action that policy classified as REQUEST_APPROVAL.

Approval does not override policy.

## Binding

Approval is bound to:

- action fingerprint
- verb
- resource and scope
- target
- material parameters
- relevant revision/preconditions
- policy-evaluation snapshot

## Lifecycle

REQUESTED
→ APPROVED
→ CONSUMED

Alternative terminal states:

- REJECTED
- EXPIRED
- REVOKED

## Default semantics

An approval is one-time and non-transitive.

Changing a fingerprint-significant field invalidates the approval.

Approval for:

- one object does not approve another object
- one environment does not approve another environment
- WRITE does not approve TRANSPORT
- one revision does not approve a materially changed revision

## Policy interaction

MUST_NOT_PROCEED remains MUST_NOT_PROCEED even if a human expresses approval.

## Execution revalidation

Immediately before future side-effecting execution:

- preconditions are checked
- action fingerprint is checked
- policy is re-evaluated
- approval validity is checked

Any material mismatch blocks execution and requires a new decision path.
