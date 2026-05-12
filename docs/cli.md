# CLI Reference

This page describes the implemented v0.1 command surface. Use `kansei --help`
or any subcommand's `--help` for the exact current Typer output.

## Top-Level Commands

```powershell
kansei init PATH [--git] [--with-codex] [--with-mcp] [--force]
  [--harnessops/--no-harnessops] [--harnessops-profile PROFILE]
  [--with-harnessops-agent-bridge] [--require-harnessops]
kansei doctor [--root PATH] [--json] [--check-mcp] [--check-codex]
kansei status [--project ID] [--priority A|B|C|hold] [--json]
kansei search QUERY [--limit N]
kansei delegate PROJECT_ID TASK [--json] [--exec]
kansei update-harness [--root PATH] [--apply]
  [--harnessops/--no-harnessops] [--harnessops-profile PROFILE]
  [--with-harnessops-agent-bridge] [--require-harnessops]
kansei backup [--root PATH] [--output PATH]
kansei migrate [--root PATH] [--json]
kansei version
```

## HarnessOps Chaining

`kansei init` chains to `hops init --profile generic-code` by default when the
`hops` command is available. `kansei update-harness` chains to
`hops update-harness`; dry runs use `hops update-harness --dry-run`, and older
instances without `.harnessops/project.toml` first receive a `hops init` dry run
or apply, matching the Kansei command mode.

Use `--no-harnessops` to skip the chained call. Use `--require-harnessops` when
automation should fail instead of warning if `hops` cannot be found. If `hops`
is not on `PATH`, set `KANSEI_HOPS_COMMAND` or set `KANSEI_HARNESSOPS_SOURCE` to
a local HarnessOps checkout so Kansei can run `uvx --isolated --from <source>
hops ...`.

## Project Commands

```powershell
kansei project list [--active/--no-active] [--kind KIND] [--priority PRIORITY]
kansei project show PROJECT_ID
kansei project add --id ID --name NAME --kind KIND --provider PROVIDER --location LOCATION --path PATH
kansei project open PROJECT_ID [--exec]
kansei project status PROJECT_ID
kansei project doctor PROJECT_ID
```

`project add` writes `projects.toml` because the user explicitly requested a
registry edit. Duplicate project IDs are rejected.

## Provider Commands

```powershell
kansei provider list
kansei provider doctor [--provider-id PROVIDER_ID]
kansei provider connect PROVIDER_ID [--tunnel] [--exec]
kansei provider disconnect PROVIDER_ID
```

`provider connect --tunnel` prints an SSH tunnel command by default. It starts a
foreground tunnel only with `--exec`.

## Dashboard Commands

```powershell
kansei dashboard today [--write]
kansei dashboard weekly [--write]
```

Preview is the default. Writing requires `--write`.

## MCP Commands

```powershell
kansei mcp serve --transport stdio
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
kansei mcp config [--root PATH] [--write] [--force]
kansei mcp inspect [--root PATH]
```

`mcp config` renders `.codex/config.toml` from `providers.toml`. Existing
differing config requires `--force` to overwrite.

## Exit Behavior

Commands raise non-zero exits for validation errors, missing projects/providers,
or unsafe writes. v0.1 keeps destructive and remote-write actions outside the
default command surface.
