# Policy, Capability & Approval Model

## Capability descriptor

A capability is evaluated as:

ACTION + RESOURCE + TARGET

A verb alone is not sufficient.

Example:

READ + SAP_SOURCE + DEVELOPMENT

is materially different from:

WRITE + BUSINESS_DATA + PRODUCTION

## Capability verbs

Initial verbs:

- READ
- QUERY
- ANALYZE
- PROPOSE
- WRITE
- DEPLOY
- TRANSPORT
- ADMIN

Capabilities do not implicitly inherit one another.

WRITE does not imply READ.
ADMIN does not imply every operation.
TRANSPORT does not imply arbitrary WRITE.

## Initial resource classes

The SAP domain may register resource kinds such as:

- SAP_SOURCE
- SAP_OBJECT
- SAP_CONFIGURATION
- BUSINESS_DATA
- MASTER_DATA
- INTEGRATION_CONFIG
- API_CONFIG
- TRANSPORT
- IDENTITY
- AUTHORIZATION
- LOG
- MONITORING_DATA

Generic resources may include REPOSITORY, DOCUMENT, TICKET, and LOCAL_ARTIFACT.

## Target environments

Initial normalized environments:

- LOCAL
- SANDBOX
- DEVELOPMENT
- QUALITY
- STAGING
- PRODUCTION
- EXTERNAL

Organization landscape configuration maps real system identifiers to normalized environments.

## Tool capability boundary

Authorization is evaluated against explicit tool operations, not tool names.

A tool named "ADT" does not imply unrestricted ADT access.

## Action Intent

Agents request external effects by producing an Action Intent containing at least:

- task
- requester
- verb
- resource
- target
- purpose
- expected side effects
- relevant parameters
- revision/preconditions where applicable

Material Action Intents receive a deterministic semantic fingerprint.

Any fingerprint-significant change creates a different action.

## Risk dimensions

Risk is represented by explicit dimensions rather than a synthetic numeric score.

Initial dimensions:

- mutation
- environment
- blast radius
- reversibility
- privilege
- data sensitivity
- external effect
- automation scope

## Policy evaluation

Pipeline:

Action Intent
→ Schema Validation
→ Capability Availability
→ Target Resolution
→ Risk Classification
→ Applicable Policies
→ Policy Resolution
→ Decision

Canonical decisions:

AUTO_EXECUTE
< EXECUTE_AND_RECORD
< REQUEST_APPROVAL
< MUST_NOT_PROCEED

The most restrictive applicable decision wins.

## Evaluation states

Policy authorization is separate from capability availability.

Evaluation may also fail structurally with:

- INSUFFICIENT_CONTEXT
- CONFLICTING_CONTEXT
- INVALID_ACTION

Side-effecting execution is not eligible when material policy context is unresolved.

## Policy monotonicity

Lower customization layers may make policy more restrictive.
They may not silently weaken inherited policy.

MVP includes no exception, emergency bypass, or super-admin override mechanism.

## Approval semantics

Approval is bound to:

- exact action fingerprint
- target
- resource scope
- relevant parameters
- revision/preconditions
- policy evaluation snapshot

Approval is not transitive.

Approval for WRITE does not approve TRANSPORT.
Approval for DEVELOPMENT does not approve PRODUCTION.
Approval for object A does not approve object B.

Approval cannot override MUST_NOT_PROCEED.

## Approval lifecycle

REQUESTED
→ APPROVED
→ CONSUMED

Alternative terminal states:

- REJECTED
- EXPIRED
- REVOKED

Default approval scope is one action / one fingerprint / one consumption.

## Pre-execution revalidation

Before any future side-effecting execution:

Approval
→ Preflight
→ Policy Re-evaluation
→ Fingerprint Validation
→ Execute

Any material change invalidates the prior approval.

## MVP boundary

The initial product registers SAP-system capabilities only for:

- READ
- QUERY
- ANALYZE
- PROPOSE

SAP-system WRITE, DEPLOY, TRANSPORT, and ADMIN capabilities are unavailable in the MVP.
