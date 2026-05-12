# Kansei Control Plane Workflow

## Instance Orientation

Confirm the root before making plans. A Kansei instance root has `kansei.toml`
and `.kansei/manifest.toml`; a target project root usually has its own project
files and may be registered from `projects.toml`. If both are present, prefer the
more specific user request and state which root you are operating on.

Use `scripts/check_instance.py <instance-root>` when you need a deterministic
structural check that does not import the package or mutate files.

## Ownership Classes

Managed files are maintained by Kansei templates and updated by
`kansei update-harness` with lock-file checks. Examples include root
`AGENTS.md`, `KANSEI.md`, template runbooks, template prompts, and Codex config
templates.

User-owned files are the user's source of truth. Do not overwrite them during
harness updates. Examples: `projects.toml`, `providers.toml`, `knowledge/`,
`dashboards/today.md`, `.env`, `.secrets/`, notebooks, local notes, and provider
credentials.

Generated files can be regenerated but should still be previewed before writing.
Examples: `.gitignore`, `.codex/config.toml`, `dashboards/project-status.md`,
and provider status caches. The instance `README.md` is initially templated but
is user-owned after creation.

## Safe Operation Sequence

1. Read: inspect config, registries, provider health, dashboards, or knowledge.
2. Plan: produce a diff, command plan, delegation plan, or dashboard proposal.
3. Apply: write only after the user asked for it or the CLI has an explicit
   `--apply` style flag.

Prefer these preview surfaces:

- Harness templates: `kansei update-harness --root <root>`
- Dashboard content: from the instance root, `kansei dashboard today`
- MCP config: `kansei mcp config --root <root>`
- Workspace/provider health: `kansei doctor --root <root>` and provider/project
  doctor commands from the instance root

When applying, repeat the exact root path used for preview. If the preview shows
`.new` sidecar files for edited managed files, preserve the user's original file
and explain the sidecar instead of merging automatically.

## Delegation

Local project work should run from the target project cwd. SSH/HPC work should
prefer read-only provider tools and explicit tunnel commands. Kansei should not
submit Slurm jobs, cancel jobs, delete remote files, or run long computations on
login nodes by default.

Before delegating, identify the project id, provider id, target location, and
requested action. If any of those are missing, inspect registries or ask a narrow
question instead of guessing.

## MCP Safety

Kansei MCP tools are intended to be read-only or plan-oriented. Treat tool names
that include `plan`, `status`, `inspect`, `list`, `health`, or `search` as safe
starting points. Treat tools that write files, call remote systems, submit jobs,
cancel jobs, delete data, archive data, or rewrite manuscripts as approval-gated
even when the underlying provider exposes them.

## Public Package Hygiene

Do not copy private instance content into the public package. When improving
templates, examples, tests, docs, or skills, use generic placeholders and
temporary demo instances. Keep real project names, collaborators, credentials,
cluster names, endpoints, unpublished notes, and paper text out of repo changes.
