# GitHub Actions Runner Probe

## Purpose

Determine whether the red repository-native CI signal is caused by the M0 foundation workflow/runner itself
or occurs before any project-specific execution step begins.

This is a delivery/operations diagnostic. It does not change M0 architecture semantics.

## Probe design

A temporary workflow was committed with exactly one GitHub-hosted job:

```yaml
runs-on: ubuntu-latest

steps:
  - name: Probe runner execution
    run: |
      echo "github-actions-runner-started"
      uname -a
      python3 --version
```

The probe intentionally did **not**:

- checkout the repository
- invoke the foundation fitness runner
- parse fixtures
- use secrets
- call SAP
- call an LLM
- depend on project code

## Observed run

```text
probe commit:
65b9f5ba0116b097b7d2e6f5fe7f4f955f38a988

workflow:
CI Probe

run id:
36358477236

job id:
108730802126

job:
GitHub-hosted Runner Probe

status:
completed

conclusion:
failure

observable steps:
none

logs_url:
null
```

The run completed in approximately three seconds.

## Interpretation

The same pre-step failure shape is reproduced by a trivial workflow that does not execute project code.

This evidence rules out the following as the demonstrated cause of the observed CI failure:

- the M0 Python fitness runner
- FIT-001 through FIT-020 fixture semantics
- repository checkout
- the `--suite all` invocation
- project-specific shell commands

The evidence supports classification at the repository/account/GitHub-hosted-runner operational layer.

It does **not** establish the specific root cause.

Possible causes such as billing/quota state, repository Actions policy, hosted-runner provisioning,
or account-level restrictions remain hypotheses only and must not be recorded as facts without direct evidence.

## Connector limitation

The available GitHub connector can inspect workflow runs/jobs, but repository Actions administration,
runner inventory, and billing/quota endpoints are not exposed through the current connector path.

Therefore the exact operational root cause cannot be verified from this environment.

## Classification

```text
FOUNDATION_FAILURE = false
WORKFLOW_CONTENT_FAILURE = false
PRE_STEP_OPERATIONAL_FAILURE = true
ROOT_CAUSE = UNKNOWN

SAFETY_BLOCKER = false
ARCHITECTURE_BLOCKER = false
MERGE_BLOCKER = true
```

## Cleanup

The temporary probe workflow is not part of the product or M0 foundation design and should be removed
after this evidence is recorded.

The normal `foundation-fitness.yml` workflow remains the canonical repository-native verification workflow.
