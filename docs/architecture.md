# Architecture

Kansei separates a public CLI package from a private local instance.

- Public package: CLI, schemas, templates, update engine, provider adapters, and
  MCP server.
- Private instance: project registry, provider registry, dashboards, local
  knowledge, runbooks, prompts, and private Codex/MCP config.

The CLI is the source of truth for local state changes. MCP exposes safe read
and plan surfaces for agents.
