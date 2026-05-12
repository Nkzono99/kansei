# Provider Contract

Providers let Kansei inspect or plan work for registered projects without
owning the domain state itself.

## Data Models

`ProjectRef` contains the registry data a provider needs:

- `id`, `name`, `kind`, `provider`, `location`, `path`
- optional `host`, `priority`, `active`, `tags`, `notes`

Provider methods return:

- `ProviderHealth`: provider ID, status, summary, warnings.
- `ProjectStatus`: project ID, provider ID, status, summary, warnings, next
  actions, details.
- `delegate_plan`: a command plan that is safe to inspect before execution.

## Built-In Providers

- `generic-code`: uses `git` for local worktree status.
- `kansei`: uses the generic-code behavior for the control-plane repository.
- `harnessops`, `paperops`, `runops`: v0.1 domain adapters that report CLI
  availability and produce safe delegation plans. They do not implement full
  domain writes.

## Registry Resolution

Provider resolution is:

1. explicit provider config in `providers.toml`
2. built-in provider adapter
3. `generic-code` fallback

Future releases may add entry-point based provider plugins.

## Registry Fields

Provider records live in `providers.toml` under `[providers.<id>]`. Supported
`type` values are `local`, `mcp`, `ssh`, and `external`. Local and SSH providers
require `command`; MCP stdio providers require `command`; non-stdio MCP
providers require `url`. Optional fields include `args`, `ssh_tunnel`,
`token_env`, and `required`.

## Safety Classes

Providers should implement read/status/doctor/delegation planning first. Remote
writes, HPC submit/cancel/delete, archive/delete, and manuscript rewrite flows
must require explicit approval and should not be hidden behind status commands.

## SSH Tunnels

`providers.toml` can declare:

```toml
ssh_tunnel = "hpc-login:18765:127.0.0.1:18765"
```

`kansei provider connect runops_hpc --tunnel` prints:

```powershell
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

Use `--exec` only when a foreground tunnel should actually be started.
