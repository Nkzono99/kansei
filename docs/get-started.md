# Get Started

This guide creates a throwaway Kansei instance and exercises the v0.1 CLI
surface without requiring private project data.

## Requirements

- Python 3.11 or newer.
- `uv` for local development commands in this repository.
- Optional: `git`, if you want `kansei init --git` to create a repository for
  the private instance.

## Create an instance

From the public package repository:

```powershell
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp
```

This writes a private control-plane layout under `.tmp/kansei-demo`:

- `kansei.toml`: instance settings and safety policy.
- `projects.toml`: project registry.
- `providers.toml`: provider registry.
- `knowledge/`, `runbooks/`, `prompts/`, `dashboards/`: private operating
  surfaces.
- `.kansei/manifest.toml` and `.kansei/lock.toml`: package-managed metadata for
  safe updates.
- `.codex/config.toml`: generated only when `--with-codex` is passed.

The generated instance is private workspace state. Do not copy real local paths,
credentials, unpublished notes, or collaborator-specific details back into the
public package repository.

If HarnessOps is available as `hops`, initialization also runs
`hops init --profile generic-code` inside the generated instance. When working
from a local HarnessOps checkout instead of an installed command, set:

```powershell
$env:KANSEI_HARNESSOPS_SOURCE = "C:\path\to\harnessops"
```

Use `--no-harnessops` when you want a plain Kansei instance without the
HarnessOps feedback overlay.

## Validate the instance

```powershell
uv run --directory . kansei doctor --root .tmp/kansei-demo
uv run --directory . kansei version
```

`doctor` checks the expected layout, required TOML files, registry shape, and
managed-file checksums. Local edits to managed files are reported as warnings so
you can decide whether to keep them or accept a generated update later.

## Work inside the instance

Most commands discover the nearest Kansei instance from the current directory:

```powershell
Set-Location .tmp/kansei-demo
uv run --directory ..\.. kansei project list
uv run --directory ..\.. kansei status
uv run --directory ..\.. kansei dashboard today
```

The examples below use `uv run --directory ..\..` when they assume your current
directory is `.tmp/kansei-demo`. If `kansei` is installed in your environment,
you can omit that prefix and run `kansei ...` directly.

When running from somewhere else, use command-specific root flags where
available, for example `kansei doctor --root PATH`, `kansei update-harness
--root PATH`, `kansei mcp config --root PATH`, or `kansei backup --root PATH`.

## Register a local code project

Use the CLI for registry edits instead of hand-rewriting TOML:

```powershell
uv run --directory ..\.. kansei project add `
  --id demo-code `
  --name "Demo Code" `
  --kind code `
  --provider generic-code `
  --location local `
  --path C:\path\to\project `
  --priority B
```

Then inspect it:

```powershell
uv run --directory ..\.. kansei project show demo-code
uv run --directory ..\.. kansei project status demo-code
uv run --directory ..\.. kansei project open demo-code
```

`project open` prints the resolved path by default. Add `--exec` only when you
want Kansei to ask the operating system to open that path.

## Preview before writing

Kansei keeps read, plan, and apply flows separate:

```powershell
uv run --directory ..\.. kansei dashboard today
uv run --directory ..\.. kansei dashboard today --write
uv run --directory ..\.. kansei update-harness
uv run --directory ..\.. kansei update-harness --apply
```

Dashboard commands preview Markdown unless `--write` is passed.
`update-harness` is a dry run unless `--apply` is passed. The HarnessOps chained
call follows the same mode: dry runs call `hops update-harness --dry-run`, while
apply calls `hops update-harness`.

## Optional MCP setup

Preview the Codex MCP config generated from `providers.toml`:

```powershell
uv run --directory ..\.. kansei mcp config
uv run --directory ..\.. kansei mcp inspect
```

Write `.codex/config.toml` after review:

```powershell
uv run --directory ..\.. kansei mcp config --write --force
```

Use `--force` only after reviewing the preview. It is needed when an existing
generated config differs from the provider-derived output.
