# Update Harness

`kansei update-harness` is a safe template update flow, not a directory sync.

It updates only files that Kansei knows how to manage, using `.kansei/lock.toml`
checksums to avoid overwriting local edits.

## Managed Files

Current lock-tracked files created by `kansei init` include:

- `AGENTS.md`
- `KANSEI.md`
- `.gitignore`
- `.codex/config.toml` when `--with-codex` is used
- `runbooks/_templates/project-runbook.md`
- `prompts/_templates/delegation.md`

These files appear in `.kansei/lock.toml` with template path, version, owner,
class, and checksum.

## User-Owned Files

Kansei treats the following as user-owned operational state:

- `projects.toml`
- `providers.toml`
- `knowledge/`
- `dashboards/today.md`, `dashboards/weekly.md`
- project runbooks and prompts outside `_templates`
- `.env`, `.secrets/`, local notes

`update-harness` does not overwrite these files.

## Behavior

Dry-run preview is the default:

```powershell
kansei update-harness
```

Apply only after reviewing the plan:

```powershell
kansei update-harness --apply
```

If a managed file still matches its lock checksum, Kansei can update it in
place. If a managed file has local edits, Kansei writes the new template beside
it as `<path>.new` and leaves the local file untouched.

## Generated Config

`.codex/config.toml` can also be regenerated from `providers.toml`:

```powershell
kansei mcp config --write --force
```

This command updates the lock entry for `.codex/config.toml`.
