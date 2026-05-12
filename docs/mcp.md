# MCP

Kansei exposes read-only and plan-oriented MCP tools with the `kansei.` prefix.
The CLI remains the source of truth for state changes.

## Serving

Local Codex clients normally use stdio:

```powershell
kansei mcp serve --transport stdio
```

HTTP mode is available for local or SSH-tunneled use:

```powershell
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
```

The default host is loopback. Do not expose HTTP MCP on a public interface
without a separate access-control plan.

## Codex Config

Preview generated config:

```powershell
kansei mcp config
```

Write `.codex/config.toml` from `providers.toml`:

```powershell
kansei mcp config --write --force
```

Inspect generated MCP surfaces:

```powershell
kansei mcp inspect
```

## Tools

- `kansei.health`: workspace root, version, and basic warnings.
- `kansei.project.list`: project summaries with optional `active`, `kind`, and
  `priority` filters.
- `kansei.project.inspect`: full registry entry plus safety policy for one
  project.
- `kansei.workspace.status`: aggregate project/provider status.
- `kansei.knowledge.search`: scoped search over local knowledge surfaces.
- `kansei.dashboard.plan_today`: dashboard markdown plan without writing files.

## Resources

- `kansei://workspace/projects`
- `kansei://workspace/providers`

## Safety

Current MCP tools do not submit jobs, delete files, rewrite manuscripts, or write
remote state. Dashboard planning returns markdown and `writes_files: false`.
