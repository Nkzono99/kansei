# Registry

Kansei は各 private instance の中で TOML registry を使います。これらは user-owned file です。
`update-harness` は上書きしません。

## `projects.toml`

例:

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

必須フィールド:

- `id`: CLI/MCP で使う安定した識別子
- `name`: 人が読むための名前
- `kind`: `management`, `paper`, `experiment`, `code`, `reading`, `admin`, `other`
- `provider`: `providers.toml` の provider ID または built-in provider
- `location`: `local`, `ssh`, `cloud`, `external`
- `path`: local または remote の project path

任意フィールド:

- `host`: `location = "ssh"` の場合に必要
- `priority`: `A`, `B`, `C`, `hold`。既定は `C`
- `active`: true の場合、dashboard/status に含めます。既定は true
- `codex_profile`, `tags`, `notes`

単純な追加には `kansei project add` を使います。

```powershell
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
```

## `providers.toml`

例:

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

provider フィールド:

- `type`: `local`, `mcp`, `ssh`, `external`
- `mode`: `cli`, `stdio`, `streamable-http`
- `command`: local provider と stdio MCP provider で必要
- `args`: 任意の command argument
- `url`: stdio ではない MCP provider で必要
- `ssh_tunnel`: `host:local_port:remote_host:remote_port`
- `token_env`: bearer token を読む環境変数
- `required`: missing/unhealthy provider を必須扱いにするかどうか

## Schema

公開 schema は `schemas/` にあります。

- `kansei.schema.json`
- `projects.schema.json`
- `providers.schema.json`
- `manifest.schema.json`
- `lock.schema.json`
