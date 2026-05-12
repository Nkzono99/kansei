# Kansei

Kansei is a private local control plane for AI-assisted research operations. It
keeps project registries, provider configuration, dashboards, knowledge, and MCP
access in one local instance while leaving each target project in its own
repository or remote environment.

```powershell
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp
uv run kansei version
```

The CLI is the source of truth for local state changes. MCP tools and Codex
instructions are an interface over that state, with read and plan operations kept
separate from apply operations.
