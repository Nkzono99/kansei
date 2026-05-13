# Kansei

Kansei は、AI 支援の研究運用を扱うための private local control plane です。
project registry、provider 設定、dashboard、knowledge、runbook、MCP access を
ひとつのローカル instance に集約しつつ、各 target project はそれぞれの
リポジトリや remote environment に残します。

Kansei は保守的に動きます。まず読む、次に計画する、最後に適用する、という
順序を基本にします。状態変更の正本は CLI です。MCP と Codex workflow は、
その状態に対する安全な参照・計画用インターフェースを提供します。

## インストール

```powershell
uv tool install kansei
kansei version
```

このリポジトリからローカル開発する場合:

```powershell
uv run kansei version
uv run --extra dev pytest -q
```

## クイックスタート

PyPI から 1 行で private instance を作成できます。

```powershell
uvx --from kansei kansei init ~/work/kansei --git --with-codex --with-mcp
```

すでに `kansei` をインストール済みの場合:

```powershell
kansei init ~/work/kansei --git --with-codex --with-mcp
cd ~/work/kansei
uvx --from kansei kansei doctor
```

ローカルの code project を登録します。

```powershell
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
kansei project list
kansei status
kansei dashboard today
```

`providers.toml` から Codex MCP 設定を生成します。

```powershell
kansei mcp config
kansei mcp config --write --force
kansei mcp inspect
```

harness update を preview します。

```powershell
uvx --from kansei kansei update-harness
```

plan が想定どおりのときだけ適用します。

```powershell
uvx --from kansei kansei update-harness --apply
```

離れた version の instance は、checkpoint ごとに exact package version を呼ぶ
upgrade chain で更新できます。

```powershell
uvx --from kansei kansei update-harness --plan
uvx --from kansei kansei update-harness --apply-chain
```

標準の CLI 実行は `uvx --from kansei kansei <command>` です。`kansei init` は
project-local な Kansei `.venv` を既定では作成しません。互換用に必要な場合だけ
`--bootstrap` で `.venv` と Kansei install を作れます。HarnessOps が `hops`
として利用できる場合、init は `hops init` も実行します。また、
`kansei update-harness` は `hops update-harness` に連鎖します。`hops` が
`PATH` に無い場合は、local HarnessOps checkout を `KANSEI_HARNESSOPS_SOURCE` に
設定してください。

## 主なコマンド

- `kansei init`: private local instance と instance-local agent skill を作成します。
- `kansei doctor`: instance 構造、TOML、registry、managed file の drift を検証します。
- `kansei project list/add/show/open/status/doctor`: project registry を管理します。
- `kansei provider list/doctor/connect/disconnect`: provider を確認し、SSH tunnel を計画します。
- `kansei status`: active project の状態を集約します。
- `kansei dashboard today|weekly`: 運用 planning view を表示します。
- `kansei search`: local knowledge、runbook、prompt、dashboard、`KANSEI.md` を検索します。
- `kansei delegate`: `--exec` が明示されない限り、安全な Codex delegation plan を出力します。
- `kansei mcp serve/config/inspect`: MCP tool を公開し、Codex MCP config を生成します。
- `kansei backup`: control-plane file を `.kansei/backups` に zip します。
- `kansei migrate`: 未適用の layout migration を確認します。

## Instance の構成

`kansei init` は次のような private instance を作成します。

- `kansei.toml`, `projects.toml`, `providers.toml`
- `knowledge/`, `dashboards/`, `runbooks/`, `prompts/`
- `.agents/skills/kansei-control-plane`, `.agents/skills/feedback-kansei`
- 必要に応じて `.codex/config.toml`
- `.kansei/manifest.toml`, `.kansei/lock.toml`, state/cache/log/backup folders

Kansei は source tree、simulation output、manuscript、remote job state を
control plane にコピーしません。

## 安全性の考え方

- `projects.toml`, `providers.toml`, `knowledge/`, daily dashboard などの
  user-owned file は `update-harness` で上書きされません。
- managed file は `.kansei/lock.toml` と照合されます。
- ローカル編集済みの managed file は上書きされず、harness update 時に
  `.new` sidecar file が作られます。
- remote write、HPC submit/cancel/delete、archive/delete、manuscript rewrite は
  v0.1 では自動実行されません。
- SSH tunnel command は既定では表示のみです。実際に foreground 実行するには
  `--exec` が必要です。
- Kansei CLI runtime は `uvx` の一時環境で再取得できます。private な運用状態は
  runtime environment ではなく instance file 側に残します。
- HarnessOps 連携は `hops` に委譲します。Kansei が `.harnessops/`,
  `harness-feedback/`, `harness-lab/` を直接組み替えることはありません。

## Agent 向けガイド

このリポジトリの保守用 Codex guidance は `.agents/skills/kansei-repository-maintainer` にあります。
`kansei init` で作成される instance 側には `.agents/skills/kansei-control-plane` と
`.agents/skills/feedback-kansei` が入ります。

## ドキュメント

- [アーキテクチャ](docs/architecture.md)
- [はじめに](docs/get-started.md)
- [CLI リファレンス](docs/cli.md)
- [Registry](docs/registries.md)
- [MCP 連携](docs/mcp.md)
- [Provider contract](docs/provider-contract.md)
- [update-harness](docs/update-harness.md)
- [セキュリティ](docs/security.md)
- [リリースノート](docs/release.md)
- [公開手順](docs/publishing.md)

v0.1 の完全な仕様は [SPEC.md](SPEC.md) にあります。
