# Kansei

Kansei is a private local control plane for AI-assisted research operations. It
keeps project registries, provider configuration, dashboards, knowledge,
runbooks, and MCP access in one local instance while leaving each target project
in its own repository or remote environment.

Kansei is intentionally conservative: read first, plan second, apply last.
The CLI is the source of truth for state changes. MCP and Codex workflows expose
safe read and planning surfaces over that state.

## Install

```powershell
uv tool install kansei
kansei version
```

For local development from this repository:

```powershell
uv run kansei version
uv run --extra dev pytest -q
```

## Quickstart

Create a private instance in one line from PyPI:

```powershell
uvx --from kansei kansei init ~/work/kansei --git --with-codex --with-mcp
```

Or, if `kansei` is already installed:

```powershell
kansei init ~/work/kansei --git --with-codex --with-mcp
cd ~/work/kansei
.venv\Scripts\activate
kansei doctor
```

Register a local code project:

```powershell
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
kansei project list
kansei status
kansei dashboard today
```

Generate Codex MCP configuration from `providers.toml`:

```powershell
kansei mcp config
kansei mcp config --write --force
kansei mcp inspect
```

Preview a harness update:

```powershell
kansei update-harness
```

Apply only when the plan is expected:

```powershell
kansei update-harness --apply
```

`kansei init` creates `.venv` in the instance and installs Kansei into it.
`uvx` only installs Kansei into a temporary runner environment; the init
bootstrap is what makes the generated instance self-contained. When HarnessOps
is available as `hops`, init also runs `hops init`, and `kansei update-harness`
chains to `hops update-harness`. If `hops` is not on `PATH`, set
`KANSEI_HARNESSOPS_SOURCE` to a local HarnessOps checkout.

## Core Commands

- `kansei init`: create a private local instance.
- `kansei doctor`: validate instance structure, TOML, and managed-file drift.
- `kansei project list/add/show/open/status/doctor`: manage the project registry.
- `kansei provider list/doctor/connect/disconnect`: inspect providers and plan SSH tunnels.
- `kansei status`: aggregate active project status.
- `kansei dashboard today|weekly`: render operational planning views.
- `kansei search`: search local knowledge, runbooks, prompts, dashboards, and `KANSEI.md`.
- `kansei delegate`: print a safe Codex delegation plan unless `--exec` is explicit.
- `kansei mcp serve/config/inspect`: expose MCP tools and generate Codex MCP config.
- `kansei backup`: zip control-plane files into `.kansei/backups`.
- `kansei migrate`: inspect pending layout migrations.

## Instance Model

`kansei init` creates a private instance containing:

- `kansei.toml`, `projects.toml`, `providers.toml`
- `knowledge/`, `dashboards/`, `runbooks/`, `prompts/`
- `.codex/config.toml` when requested
- `.kansei/manifest.toml`, `.kansei/lock.toml`, state/cache/log/backup folders

Kansei does not copy source trees, simulation outputs, manuscripts, or remote
job state into the control plane.

## Safety Model

- User-owned files such as `projects.toml`, `providers.toml`, `knowledge/`, and
  daily dashboards are not overwritten by `update-harness`.
- Managed files are checked against `.kansei/lock.toml`.
- Locally edited managed files receive sidecar `.new` files during harness
  updates instead of being overwritten.
- Remote writes, HPC submit/cancel/delete, archive/delete, and manuscript
  rewrite workflows are not automatic in v0.1.
- SSH tunnel commands are printed by default; foreground execution requires
  `--exec`.
- `.venv` is ignored and may be recreated; private operational state remains in
  the instance files, not the bootstrap environment.
- HarnessOps integration is delegated to `hops`; Kansei does not directly
  reshape `.harnessops/`, `harness-feedback/`, or `harness-lab/`.

## Agent Guidance

Repository-local Codex guidance lives under `.agents/skills/kansei-control-plane`.
Use it when working on private Kansei instances or updating the instance
operational harness.

## Documentation

- [Architecture](docs/architecture.md)
- [Get started](docs/get-started.md)
- [CLI reference](docs/cli.md)
- [Registries](docs/registries.md)
- [MCP integration](docs/mcp.md)
- [Provider contract](docs/provider-contract.md)
- [Update harness](docs/update-harness.md)
- [Security](docs/security.md)
- [Release notes](docs/release.md)
- [Publishing](docs/publishing.md)

The full v0.1 specification is in [SPEC.md](SPEC.md).
