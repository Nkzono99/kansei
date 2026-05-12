# Kansei Control Plane Workflow

## Ownership Classes

Managed files are maintained by Kansei templates and can be updated by
`kansei update-harness` with lock-file checks. Examples: `AGENTS.md`,
`KANSEI.md`, template runbooks, template prompts, and generated Codex config
templates.

User-owned files are the user's source of truth. Do not overwrite them during
harness updates. Examples: `projects.toml`, `providers.toml`, `knowledge/`,
`dashboards/today.md`, `.env`, and `.secrets/`.

Generated files can be regenerated but should still be previewed before writing.
Examples: `README.md`, `.gitignore`, `.codex/config.toml`,
`dashboards/project-status.md`, and provider status caches.

## Safe Operation Sequence

1. Read: inspect config, registries, provider health, dashboards, or knowledge.
2. Plan: produce a diff, command plan, delegation plan, or dashboard proposal.
3. Apply: write only after the user asked for it or the CLI has an explicit
   `--apply` style flag.

## Delegation

Local project work should run from the target project cwd. SSH/HPC work should
prefer read-only provider tools and explicit tunnel commands. Kansei should not
submit Slurm jobs, cancel jobs, delete remote files, or run long computations on
login nodes by default.
