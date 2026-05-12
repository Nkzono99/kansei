# Release Notes

Kansei v0.1 is an alpha control-plane package. The implemented scope focuses on
local instance creation, validation, registry operations, dashboard rendering,
safe harness updates, backups, and a read/plan-oriented MCP surface.

## v0.1.0

Implemented:

- `kansei init` for creating private local instances from package templates.
- `kansei doctor` for layout, TOML, registry, and managed-file checks.
- `kansei project` commands for listing, showing, adding, opening, and checking
  registered projects.
- `kansei provider` commands for listing providers, checking built-in provider
  health, and planning or running foreground SSH tunnels.
- `kansei status`, `kansei dashboard today`, and `kansei dashboard weekly` for
  local operating views.
- `kansei search` over Markdown knowledge, runbook, prompt, and dashboard
  surfaces.
- `kansei update-harness` dry-run/apply flow for package-managed files.
- `kansei mcp serve`, `kansei mcp config`, and `kansei mcp inspect`.
- `kansei backup` for local control-plane zip archives.
- `kansei migrate` status inspection for the current layout version.

## Safety Model

- Private instance data stays in the private instance.
- Read and preview commands are the default where practical.
- File writes require explicit flags such as `--write` or `--apply`.
- Remote connection helpers print plans unless `--exec` is provided.
- `update-harness` updates managed files only and protects user-owned state.

## Current Limitations

- MCP write tools are not implemented in v0.1.
- `provider disconnect` does not manage background tunnel processes.
- Domain-specific runops, paperops, and harnessops behavior is represented as
  provider configuration and delegation surfaces; their domain state remains in
  those provider projects.
- Code project health is intentionally generic and does not replace a future
  dedicated codeops provider.
