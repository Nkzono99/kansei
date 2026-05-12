# Registries

Kansei uses TOML registries in each private instance. They are user-owned files:
`update-harness` does not overwrite them.

## `projects.toml`

Example:

```toml
schema_version = "0.1"

[[projects]]
id = "kansei"
name = "Kansei"
kind = "management"
provider = "kansei"
location = "local"
path = "~/work/kansei"
priority = "A"
active = true
tags = ["control-plane"]
```

Required fields:

- `id`: stable CLI/MCP identifier
- `name`: human-readable name
- `kind`: `management`, `paper`, `experiment`, `code`, `reading`, `admin`, or `other`
- `provider`: provider ID from `providers.toml` or a built-in provider
- `location`: `local`, `ssh`, `cloud`, or `external`
- `path`: local or remote project path

Optional fields:

- `host`: required for `location = "ssh"`
- `priority`: `A`, `B`, `C`, or `hold` (default `C`)
- `active`: included in dashboards/status when true (default true)
- `codex_profile`, `tags`, `notes`

Use `kansei project add` for simple additions:

```powershell
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
```

## `providers.toml`

Example:

```toml
schema_version = "0.1"

[providers.generic_code]
type = "local"
mode = "cli"
command = "git"

[providers.paperops]
type = "mcp"
mode = "stdio"
command = "pops"
args = ["mcp", "serve", "--transport", "stdio"]
required = false

[providers.runops_hpc]
type = "mcp"
mode = "streamable-http"
url = "http://127.0.0.1:18765/mcp"
ssh_tunnel = "hpc-login:18765:127.0.0.1:18765"
token_env = "RUNOPS_HPC_MCP_TOKEN"
required = false
```

Provider fields:

- `type`: `local`, `mcp`, `ssh`, or `external`
- `mode`: `cli`, `stdio`, or `streamable-http`
- `command`: required for local providers and stdio MCP providers
- `args`: optional command arguments
- `url`: required for non-stdio MCP providers
- `ssh_tunnel`: `host:local_port:remote_host:remote_port`
- `token_env`: environment variable for bearer token lookup
- `required`: whether missing/unhealthy provider should be treated as required

## Schemas

Public schemas live in `schemas/`:

- `kansei.schema.json`
- `projects.schema.json`
- `providers.schema.json`
- `manifest.schema.json`
- `lock.schema.json`
