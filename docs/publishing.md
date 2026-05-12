# 公開手順

Kansei は `kansei` という package 名で PyPI に公開します。

## リリース手順

1. `pyproject.toml` の `version` を更新します。
2. ローカルで check を実行します。

   ```powershell
   uv run --extra dev pytest -q
   uv run --extra dev ruff check .
   uv run --extra dev mypy src\kansei
   uv build
   ```

3. release commit を push します。
4. `v0.1.0` のような GitHub Release を作成します。
5. `.github/workflows/publish-pypi.yml` が distribution をビルドし、Trusted Publishing
   経由で PyPI に公開します。

## Trusted Publisher 設定

PyPI Trusted Publisher Management には次を登録します。

- Publisher: GitHub Actions
- PyPI project name: `kansei`
- Repository owner: `Nkzono99`
- Repository name: `kansei`
- Workflow filename: `publish-pypi.yml`
- Environment name: `pypi`

この workflow では PyPI API token は不要です。
