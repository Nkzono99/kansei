# AGENTS.md

このリポジトリは `kansei` を開発します。`kansei` は、AI 支援の研究運用向けに
private local control plane を保守する公開 Python package / CLI です。

## 基本ルール

- このリポジトリは公開パッケージのコードとして扱います。private project data、HPC credential、
  未公開 note、API key、token、ローカル collaborator 固有の情報を追加しないでください。
- 他の agent が同時に編集している可能性があります。編集前に現在の diff を確認し、無関係な変更を
  revert しないでください。
- target project の状態は target project 側に残します。Kansei は registry、provider config、
  dashboard view、knowledge reference、prompt、runbook、MCP access を保存します。
- read / plan / apply を分けます。適用前に preview し、`projects.toml`, `providers.toml`,
  `knowledge/`, `dashboards/today.md` などの user-owned instance file を上書きしないでください。
- 状態変更の入り口として `kansei` CLI を優先します。MCP と Codex workflow は、別の
  source of truth を作らず、CLI の挙動を呼ぶか mirror してください。
- provider の挙動を追加するときは、まず安全な read/status/plan path を実装します。remote write、
  HPC submit/cancel、delete/archive、manuscript rewrite は明示的な承認を必須にしてください。
- このリポジトリは GitHub Flow を使います。`main` は protected branch として扱い、直接 push せず、
  topic branch から Pull Request を作成して required check 通過後に merge してください。

## 実装規約

- package source は `src/kansei` に置きます。
- CLI command は `src/kansei/cli/commands` に置きます。
- private instance 用 template は `src/kansei/templates` に置きます。
- このリポジトリの保守用 Codex skill は `.agents/skills/kansei-repository-maintainer` にあります。
- `kansei init` で生成する instance-local skill は `src/kansei/templates/agents/skills/` に置きます。
  `SKILL.md` は簡潔に保ち、手順の詳細は `references/`、繰り返し使う deterministic helper は
  `scripts/` に置きます。
- test は `tests` に置き、生成する Kansei instance には temporary directory を使います。
- TOML の読み書きには structured API を使います。registry や lock file を ad hoc な文字列処理で
  書き換えないでください。

## Agent ワークフロー

1. 計画や編集の前にリポジトリの状態と関連 file を確認します。
2. Kansei instance 作業では生成 instance 側の `kansei-control-plane` skill を procedural harness として使い、
   直接 file を編集するより CLI preview を優先します。
3. 生成/demo instance は `.tmp/` または別の disposable directory に置きます。
4. current task でユーザーが明示しない限り、remote provider への接続、HPC job の submit/cancel、
   remote file の delete/archive、manuscript rewrite は行いません。
5. `main` へ取り込む変更は `codex/...` などの topic branch に commit し、Pull Request を作成して
   required check を確認してから merge します。`main` への direct push は行いません。

## 検証

編集後は、意味のある最小限の check を実行します。

```powershell
uv run pytest -q
uv run kansei version
```

init/update 関連の作業では、さらに次を実行します。

```powershell
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp --no-bootstrap
uv run --directory . kansei doctor --root .tmp/kansei-demo
uv run --directory . kansei update-harness --root .tmp/kansei-demo
```

## Agent ハーネス

このリポジトリには `.agents/skills/kansei-repository-maintainer` に repo-local な Codex skill があります。
private Kansei instance に配る skill は `src/kansei/templates/agents/skills/` に version 管理し、
`kansei init` と `kansei update-harness` で instance 側へ展開します。
