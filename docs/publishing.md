# Publishing

Kansei is published to PyPI as `kansei`.

## Release Flow

1. Update `version` in `pyproject.toml`.
2. Run local checks:

   ```powershell
   uv run --extra dev pytest -q
   uv run --extra dev ruff check .
   uv run --extra dev mypy src\kansei
   uv build
   ```

3. Push the release commit.
4. Create a GitHub Release such as `v0.1.0`.
5. `.github/workflows/publish-pypi.yml` builds distributions and publishes them
   to PyPI through Trusted Publishing.

## Trusted Publisher Settings

PyPI Trusted Publisher Management should use:

- Publisher: GitHub Actions
- PyPI project name: `kansei`
- Repository owner: `Nkzono99`
- Repository name: `kansei`
- Workflow filename: `publish-pypi.yml`
- Environment name: `pypi`

No PyPI API token is required for this workflow.
