---
name: kansei-control-plane
description: Operate Kansei private local control-plane instances safely. Use when Codex is working inside or against a Kansei instance root; needs to inspect, initialize, doctor, or update a Kansei harness; review project/provider registries; plan dashboards, knowledge search, MCP exposure, or delegation; or avoid leaking private target-project state back into the public kansei package.
---

# Kansei Control Plane

## Core Rule

Treat a Kansei root as a control plane, not a place to directly reorganize
target projects. Read first, plan second, apply only through the `kansei` CLI or
an explicitly approved safe write path.

## Workflow

1. Locate the instance root by finding both `kansei.toml` and
   `.kansei/manifest.toml`.
2. Run read-only checks before proposing writes:
   `kansei doctor`, `kansei project list`, `kansei provider list`,
   `kansei status`, `kansei dashboard today`, or
   `scripts/check_instance.py <instance-root>`.
3. Classify the files you may touch. Treat `projects.toml`, `providers.toml`,
   `knowledge/`, `dashboards/today.md`, `.env`, and `.secrets/` as user-owned.
4. Preview harness updates with `kansei update-harness`. Use `--apply` only
   when the user requested the update and the preview is understood.
5. For target-project work, change cwd to the target project or delegate through
   the configured provider. Do not make target-project edits from the Kansei
   root.
6. Keep MCP/provider work read-only or plan-only by default. Remote writes, HPC
   submit/cancel, delete/archive, and manuscript rewrite actions require
   explicit approval in the current task.

## Common Commands

```powershell
Push-Location <instance-root>
uv run kansei doctor --root <instance-root>
uv run kansei project list
uv run kansei provider list
uv run kansei status
uv run kansei dashboard today
uv run kansei search "query"
uv run kansei update-harness --root <instance-root>
uv run kansei mcp inspect --root <instance-root>
Pop-Location
```

## Bundled Resources

- Read `references/control-plane-workflow.md` when ownership, preview/apply
  boundaries, delegation, or MCP safety is ambiguous.
- Run `scripts/check_instance.py <instance-root>` for a deterministic
  no-import structural check before operating on an unfamiliar instance.
