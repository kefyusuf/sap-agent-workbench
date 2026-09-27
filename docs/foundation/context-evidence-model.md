# Context & Evidence Model

## Knowledge vs Context

Knowledge is information available to the system.

Context is the task-scoped subset actually supplied to reasoning.

available knowledge != injected context

The Context Builder selects only task-relevant material.

## Context layers

A task may draw from:

- Task Context
- Workflow Context
- SAP Domain Context
- Organization Context
- Landscape Context
- Project Context
- Team/User Context
- Retrieved Knowledge
- Live Evidence

Not every layer is loaded for every task.

## Context item metadata

Material context should preserve:

- source
- authority
- scope
- freshness
- revision
- provenance
- content

## Claim classification

Material claims use:

- VERIFIED
- KNOWN
- INFERRED
- ASSUMED
- UNKNOWN
- CONFLICTING

### VERIFIED

Direct supporting evidence exists.

### KNOWN

A trustworthy context source states the claim, but it has not been live-verified during the current task.

### INFERRED

The claim is a reasoning result based on other facts or evidence.

### ASSUMED

The claim is temporarily accepted to continue work but remains unverified.

### UNKNOWN

Required information is unavailable.

### CONFLICTING

Relevant sources disagree.

Material conflicts must not be silently reconciled.

## Authority is claim-dependent

There is no single global source ranking valid for every claim.

Examples:

- user/approved requirement is authoritative for business intent
- live system evidence is authoritative for current system state
- current source is authoritative for current implementation
- organization policy is authoritative for organization rules
- official SAP documentation is authoritative for SAP product semantics

Authority must not be confused with reasoning confidence.

## Authority labels

Initial labels:

- SYSTEM_VERIFIED
- PROJECT_APPROVED
- ORGANIZATION_APPROVED
- OFFICIAL_VENDOR
- INTERNAL_REFERENCE
- USER_PROVIDED
- MODEL_BACKGROUND

These labels are metadata, not universal numeric scores.

## Freshness

Context may be classified as:

- STATIC
- SLOW_CHANGING
- PROJECT_LIFETIME
- DEPLOYMENT_SENSITIVE
- LIVE

Freshness requirements depend on the claim.

## Revision binding

Source, architecture, and verification artifacts should be revision-bound when practical.

"Review passed" is weaker than:

"Review passed for revision R."

Evidence for revision A must not verify revision B.

## Evidence

Evidence is verifiable support for a claim or completion condition.

Initial evidence types:

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

Model-generated text is not evidence of SAP system state.

## Evidence strength

Avoid synthetic numeric precision.

Use:

- DIRECT
- CORROBORATED
- INDIRECT
- UNVERIFIED

Reasoning confidence may separately be low, medium, or high.

## Traceability

Preferred chain:

Source
→ Context Item / Evidence
→ Claim
→ Assessment
→ Recommendation
→ Decision
→ Work Product
→ Verification

Provenance must survive retrieval and transformation.

## Evidence immutability

Evidence records are append-oriented.
A newer observation creates a new evidence record rather than rewriting historical evidence.

## Completion

The Workflow, not the Agent, defines evidence sufficiency.

Tool success is not equivalent to workflow completion.
Output generation is not equivalent to workflow completion.
