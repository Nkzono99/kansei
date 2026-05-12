# MCP

Kansei exposes read-only and plan-oriented MCP tools with the `kansei.` prefix.

Initial tools:

- `kansei.health`
- `kansei.project.list`
- `kansei.project.inspect`
- `kansei.workspace.status`
- `kansei.knowledge.search`
- `kansei.dashboard.plan_today`

The default transport is stdio for local Codex clients. HTTP mode binds to
`127.0.0.1` by default.
