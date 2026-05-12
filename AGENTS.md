# AGENTS.md

This repository builds `kansei`, a public Python package and CLI that maintains a
private local control plane for AI-assisted research operations.

## Ground Rules

- Treat this repo as public package code. Do not add private project data, HPC
  credentials, unpublished notes, API keys, tokens, or local-only collaborator
  details.
- Assume other agents may be editing the repo at the same time. Check the
  current diff before editing and do not revert unrelated changes.
- Keep target project state in target projects. Kansei stores registries,
  provider configuration, dashboard views, knowledge references, prompts,
  runbooks, and MCP access.
- Keep read/plan/apply separate. Preview changes before applying them, and never
  overwrite user-owned instance files such as `projects.toml`, `providers.toml`,
  `knowledge/`, or `dashboards/today.md`.
- Prefer the `kansei` CLI as the state-changing surface. MCP and Codex workflows
  should call or mirror CLI behavior instead of inventing a second source of
  truth.
- When adding provider behavior, implement a safe read/status/plan path first.
  Remote write, HPC submit/cancel, delete/archive, and manuscript rewrite flows
  must require explicit approval.

## Implementation Conventions

- Package source lives under `src/kansei`.
- CLI commands live under `src/kansei/cli/commands`.
- Templates for private instances live under `src/kansei/templates`.
- The Codex agent skill lives under `.agents/skills/kansei-control-plane`.
  Keep `SKILL.md` concise; put procedural detail in `references/` and only add
  deterministic helpers in `scripts/` when they reduce repeated manual work.
- Tests live under `tests` and should use temporary directories for generated
  Kansei instances.
- Use structured TOML parsing/writing APIs. Avoid ad hoc string rewriting of
  registries or lock files.

## Agent Workflow

1. Inspect the repo state and relevant files before planning edits.
2. For Kansei instance work, use the `kansei-control-plane` skill as the
   procedural harness and prefer CLI previews over direct file edits.
3. Keep generated/demo instances under `.tmp/` or another disposable directory.
4. Do not contact remote providers, submit or cancel HPC work, delete/archive
   remote files, or rewrite manuscripts unless the user explicitly asks for that
   action in the current task.

## Validation

Run the smallest meaningful checks after edits:

```powershell
uv run pytest -q
uv run kansei version
```

For init/update work, also run:

```powershell
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp --no-bootstrap
uv run --directory . kansei doctor --root .tmp/kansei-demo
uv run --directory . kansei update-harness --root .tmp/kansei-demo
```

## Agent Harness

The repo includes a versioned Codex skill at
`.agents/skills/kansei-control-plane`. Use it as the procedural harness for
working on private Kansei instances without leaking private state back into the
public package.
