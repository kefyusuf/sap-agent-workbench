# Knowledge Pack Contract

## Definition

A Knowledge Pack contains facts, references, standards, documentation, or other information
that may be retrieved into task context.

Knowledge is not executable behavior.

## Examples

- official SAP documentation
- ABAP coding standards
- organization architecture
- landscape registry
- project specifications
- interface catalog
- custom-object registry
- incident history
- architecture decisions

## Metadata

Material knowledge should preserve:

- identity
- scope
- source
- authority
- freshness
- revision
- provenance
- lifecycle status

## Revision

Knowledge changes are append/revision oriented.
A newer version supersedes an older version without destroying historical provenance.

## Conflict

Same-scope material conflicts must be surfaced.
Knowledge retrieval must not silently choose a conflicting fact as truth.

## Customization

Organization and project packs may add knowledge freely within policy and secret-isolation boundaries.

Private does not mean secret-safe: raw credentials remain outside Knowledge Packs.
