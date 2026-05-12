# アーキテクチャ

Kansei は、公開 Python package と private local instance を分離します。

## 公開パッケージ

公開リポジトリには次のものを置きます。

- `src/kansei/cli` 配下の CLI 実装
- `src/kansei/registry` 配下の TOML registry model
- `src/kansei/providers` 配下の provider adapter
- dashboard / search / MCP / update helper
- `src/kansei/templates` 配下の private instance template
- `src/kansei/templates/agents/skills` 配下の instance-local agent skill template
- `.agents/skills` 配下の repo-local agent guidance
- `schemas` 配下の公開 JSON schema
- test と GitHub Actions workflow

private project list、未公開の研究メモ、HPC credential、API key、ローカルの
collaborator 情報、実在する remote path は含めません。

## Private instance の構成

`kansei init PATH` は private control plane を作成します。

```text
PATH/
  README.md
  AGENTS.md
  KANSEI.md
  kansei.toml
  projects.toml
  providers.toml
  knowledge/
  dashboards/
  runbooks/
  prompts/
  .agents/
    skills/
      kansei-control-plane/
      feedback-kansei/
  .codex/
  .kansei/
    manifest.toml
    lock.toml
    state/
    cache/
    logs/
    backups/
    migrations/
```

instance は運用 metadata と local knowledge を保存します。target project の
source tree、manuscript、Slurm output、provider 側の状態を取り込むものでは
ありません。`kansei init` は既定で git 管理外の `.venv` も作成し、bootstrap 後に
instance 自身の `kansei` command を実行できるようにします。
`.agents/skills/` には instance 操作用の `kansei-control-plane` と、upstream feedback 用の
`feedback-kansei` を managed file として配ります。

## 状態の境界

Kansei の状態変更の正本は CLI です。MCP tool や Codex prompt は CLI を呼ぶか、
CLI と同じ挙動を mirror し、別の状態 model を作らないようにします。

HarnessOps state は委譲境界です。Kansei は生成済み instance に対して
`hops init` や `hops update-harness` を subprocess として呼びますが、
`.harnessops/`, `harness-feedback/`, `harness-lab/` を直接書きません。

典型的な流れ:

```text
agent or user
  -> kansei CLI / MCP read tool
    -> provider adapter or provider CLI/MCP
      -> target project state
```

## ファイル所有区分

- managed: `AGENTS.md`, `KANSEI.md`, `.gitignore`, `.codex/config.toml`,
  `.agents/skills/` の Kansei-managed skill、`runbooks/_templates` と
  `prompts/_templates` 配下の template file など、
  lock で追跡される file。
- user-owned: registry、knowledge、dashboard、runbook、prompt、ユーザーが作成した
  local note。
- generated: 明示コマンドで再生成できる file。例:
  `kansei mcp config --write --force` から作る `.codex/config.toml`。

正確な update の挙動は [update-harness](update-harness.md) を参照してください。
