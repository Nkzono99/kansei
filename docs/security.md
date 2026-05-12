# Security

Kansei is private by default even though the package repository is public.

## Do Not Commit

- `.env`
- `.secrets/`
- API keys or bearer tokens
- SSH private keys
- HPC credentials
- private project paths from a real local instance
- unpublished paper notes or collaborator-specific constraints

## Apply Gates

The default implementation favors read and plan operations. Actions requiring
explicit user intent include:

- writing user-owned files
- creating or updating the instance-local `.venv`
- overwriting generated `.codex/config.toml`
- remote writes
- Slurm submit/cancel/delete
- archive/delete
- manuscript rewrite
- harness update apply
- HarnessOps chained updates through `hops`

## MCP

HTTP MCP should bind to `127.0.0.1` unless the operator has a deliberate access
control plan. SSH tunnels are preferred for remote provider access.

## Feedback Boundary

If local friction is exported upstream, sanitize it first. Keep reproducible
generic failure details, not private project data.

HarnessOps overlay writes remain `hops`-owned. Kansei may invoke `hops init` or
`hops update-harness`, but it must not directly restructure `.harnessops/`,
`harness-feedback/`, or `harness-lab/`.
