# Foundation Fitness Fixtures

This directory materializes deterministic M0 architecture fitness scenarios.

## Scope

These fixtures validate foundation semantics, not SAP domain reasoning quality.

The fixture serialization is an **internal M0 test format**, not a public product manifest contract.
It may evolve with the runner as long as scenario meaning and stable scenario IDs remain traceable.

## Result model

Each scenario expects one of:

- PASS
- FAIL
- BLOCKED
- NOT_APPLICABLE

All CRITICAL scenarios must PASS before M0 can close.
All REQUIRED scenarios must also PASS unless an explicit non-safety blocker is accepted.

## Fixture structure

Each JSON fixture contains:

- `id` — stable scenario identity
- `revision` — fixture revision
- `criticality` — CRITICAL / REQUIRED / ADVISORY
- `category` — foundation area
- `kind` — deterministic runner handler
- `title` — human-readable invariant
- `given` — input state
- `when` — deterministic operation under test
- `then` — expected result
- `invariant` — canonical rule being protected
- `decision_refs` — architecture decisions supporting the scenario

## Safety Kernel — FIT-001 through FIT-012

The initial Safety Kernel covers:

- Agent/policy/tool boundary
- restrictive Policy resolution
- Policy monotonicity
- unknown target fail-closed behavior
- model-output/evidence boundary
- VERIFIED-claim evidence requirement
- evidence revision binding
- approval fingerprint binding
- approval/deny precedence
- mandatory verification protection
- protected customization fields
- no SAP mutation capabilities in the MVP

## Resolution Suite — FIT-013 through FIT-020

The secondary suite covers:

- context shadowing with provenance preservation
- same-scope conflict surfacing
- Customization Pack compatibility
- declared Workflow extension hooks
- rejection of undeclared hooks
- Knowledge supersession without destructive history loss
- raw-secret rejection from customization content
- capability availability remaining distinct from Policy authorization

## Execution

```bash
python scripts/run_foundation_fitness.py
python scripts/run_foundation_fitness.py --suite resolution
python scripts/run_foundation_fitness.py --suite all
```

The runner treats stable scenario IDs and expected semantics as authoritative deterministic test inputs.
