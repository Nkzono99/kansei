---
name: kansei-release
description: Release the public Kansei Python package. Use when Codex is asked to prepare Kansei release notes, choose or bump the package version, update release docs, validate the package, commit the release, tag or create a GitHub Release, and publish through the configured PyPI workflow.
---

# Kansei Release

Use this skill only for the public `kansei` package repository. Keep private instance data,
project registry contents, credentials, HPC endpoints, and unpublished notes out of release
artifacts.

## Workflow

1. Confirm the worktree and release target.
   - Run `git status --short`, `git status -sb`, `git tag --sort=-v:refname`, and inspect
     recent commits.
   - If unrelated user changes are present, do not stage them.
   - Use semantic versioning. Feature releases normally bump minor, patch-only fixes bump patch.

2. Update release files.
   - Bump `pyproject.toml` and `src/kansei/__init__.py`.
   - If managed templates or generated harness files changed, bump
     `src/kansei/core/instance.py` `TEMPLATE_VERSION` and the default manifest template version.
   - Update `docs/release.md` with a new top section.
   - Run `uv lock` after changing the package version.

3. Validate locally.
   - `uv run --extra dev pytest -q`
   - `uv run --extra dev ruff check .`
   - `uv run --extra dev mypy src\kansei`
   - `uv build`
   - `uv run kansei version`

4. Commit and publish.
   - Stage only release-related files.
   - Commit with `Release vX.Y.Z`.
   - Push `main` to `origin`.
   - Create a GitHub Release named `vX.Y.Z` with notes from `docs/release.md`.
   - The `publish-pypi.yml` workflow publishes to PyPI via Trusted Publishing.

5. Verify after release.
   - Check the GitHub Release exists.
   - Check the publish workflow status if `gh` is available.
   - Leave any follow-up notes in the final response.

## Guardrails

- Do not create a release from a dirty stage that includes unrelated files.
- Do not rewrite existing release tags. If a tag exists, stop and report it.
- Do not apply HarnessOps migrations or remote provider writes as part of a Kansei package release
  unless the user explicitly asks.
- Prefer `gh release create vX.Y.Z --target main --title "Kansei vX.Y.Z" --notes-file <file>`
  for the release step.
