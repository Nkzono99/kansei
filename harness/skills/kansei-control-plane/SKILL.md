---
name: kansei-control-plane
description: Operate and maintain Kansei private local control-plane instances safely. Use when Codex needs to inspect a Kansei instance, initialize or update its harness, review project/provider registries, plan dashboards or delegation, expose read-only MCP tools, or avoid direct edits to target project files while working from a Kansei root.
---

# Kansei Control Plane

## Overview

Use this skill to work on Kansei instances as control planes, not as mega
workspaces. Keep private state local, inspect before planning, and apply only
through the CLI or an explicitly approved safe write path.

## Workflow

1. Find the instance root with `kansei.toml` and `.kansei/manifest.toml`.
2. Run read-only checks first: `kansei doctor`, `kansei project list`,
   `kansei provider list`, `kansei status`, or `kansei dashboard today`.
3. Treat `projects.toml`, `providers.toml`, `knowledge/`, and
   `dashboards/today.md` as user-owned unless the user explicitly asks for an
   edit.
4. Use `kansei update-harness` for dry-run previews. Add `--apply` only after
   the requested update is clear.
5. Delegate target-specific work by changing cwd to the target project or using
   the target provider. Do not reorganize target project files from the Kansei
   root.
6. Keep MCP tools read-only or plan-only by default. Remote writes, HPC job
   submission/cancel, deletes, archives, and manuscript rewrites need explicit
   approval.

## Common Commands

```powershell
kansei doctor
kansei project list
kansei provider list
kansei status
kansei dashboard today
kansei search "query"
kansei update-harness
kansei mcp serve --transport stdio
```

## References

- Read `references/control-plane-workflow.md` when deciding whether a file is
  managed, generated, or user-owned.
- Run `scripts/check_instance.py <instance-root>` for a deterministic structural
  check that does not require importing the package.
