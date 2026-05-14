---
id: RS0001
record_type: research_scan
created_at: '2026-05-15T04:05:23+09:00'
status: captured
scope: kansei target repository
existing_dossier:
classification:
  capability: release_metadata
  failure_class: protected_branch_drift
evidence:
  local:
  - summary: origin HEAD points to main and no origin/master branch is listed
    ref: git branch -r
  codebase:
  - summary: pyproject Documentation URL points to /tree/master/docs while AGENTS requires GitHub Flow with protected main
    ref: pyproject.toml:55; AGENTS.md
  external: []
  risk:
  - summary: Low-risk metadata/docs patch; no private instance data and no runtime behavior change
    ref: local inspection
candidates:
- title: Update public metadata and CI branch references to main
  relation: selected_for_execution
  recommendation: keep public package links aligned with protected branch policy
  next_command: edit pyproject.toml and .github/workflows/ci.yml
recommendation: Execute a T2 metadata/workflow cleanup, then validate with tests/lint/type/build plus HOPS doctor/migrate.
---

# RS0001: Branch naming drift in public package metadata

## Scope

- scope: kansei target repository
- existing_dossier: 未設定
- capability: release_metadata
- failure_class: protected_branch_drift

## Evidence

### Local

- origin HEAD points to main and no origin/master branch is listed (ref: git branch -r)

### Codebase

- pyproject Documentation URL points to /tree/master/docs while AGENTS requires GitHub Flow with protected main (ref: pyproject.toml:55; AGENTS.md)

### External

- なし

### Risk And Counterexample

- Low-risk metadata/docs patch; no private instance data and no runtime behavior change (ref: local inspection)

## Candidates

| candidate | relation | recommendation | next_command |
|---|---|---|---|
| Update public metadata and CI branch references to main | selected_for_execution | keep public package links aligned with protected branch policy | edit pyproject.toml and .github/workflows/ci.yml |

## Recommendation

Execute a T2 metadata/workflow cleanup, then validate with tests/lint/type/build plus HOPS doctor/migrate.

## Next Commands

- `edit pyproject.toml and .github/workflows/ci.yml`
