# update-harness

`kansei update-harness` は安全な template 更新フローであり、directory sync ではありません。

Kansei が管理対象として知っている file だけを更新し、`.kansei/lock.toml` の checksum を
使って local edit の上書きを防ぎます。

Kansei は HarnessOps overlay の maintenance も `hops` に委譲します。command が利用できる場合、
dry run では `hops update-harness --dry-run`、`--apply` では `hops update-harness` を呼びます。
`.harnessops/project.toml` が無い古い instance では、先に `hops init --profile generic-code` を
preview または apply します。

## Managed file の扱い

`kansei init` が作成し、現在 lock で追跡している file には次が含まれます。

- `AGENTS.md`
- `KANSEI.md`
- `.gitignore`
- `.agents/skills/kansei-control-plane/**`
- `.agents/skills/feedback-kansei/**`
- `--with-codex` 使用時の `.codex/config.toml`
- `runbooks/_templates/project-runbook.md`
- `prompts/_templates/delegation.md`

これらの file は `.kansei/lock.toml` に template path、version、owner、class、checksum と
ともに記録されます。

## User-owned file の扱い

Kansei は次のものを user-owned な運用状態として扱います。

- `projects.toml`
- `providers.toml`
- `knowledge/`
- `dashboards/today.md`, `dashboards/weekly.md`
- `_templates` の外にある project runbook と prompt
- `.env`, `.secrets/`, local note

`update-harness` はこれらを上書きしません。

## 挙動

既定は dry-run preview です。

```powershell
uvx --from kansei kansei update-harness
```

`--no-harnessops` が無い限り、HarnessOps chained call も preview します。

plan を確認したあとで適用します。

```powershell
uvx --from kansei kansei update-harness --apply
```

managed file が lock checksum と一致していれば、Kansei はその場で更新できます。managed file に
local edit がある場合、Kansei は新しい template を `<path>.new` として横に書き、元の file は
そのまま残します。

HarnessOps file は Kansei が直接書き換えません。apply path は `hops init` または
`hops update-harness` を呼ぶため、`.harnessops/`, `harness-feedback/`, `harness-lab/` の所有は
HarnessOps に残ります。

## Versioned upgrade chain

Kansei は `uvx` 経由で exact package version を呼べるため、長期的な後方互換性は
「最新 Kansei が過去すべての layout を理解する」方式ではなく、「checkpoint ごとの
Kansei に更新を委譲する」方式を標準にします。

```powershell
uvx --from kansei kansei update-harness --plan
uvx --from kansei kansei update-harness --apply-chain
uvx --from kansei kansei update-harness --target 0.3
uvx --from kansei kansei update-harness --target latest --allow-major --apply-chain
```

`--plan` は `.kansei/manifest.toml` の `harness.kansei_version` と PyPI release list から、
minor ごとの latest patch を checkpoint とする chain を表示します。例:

```text
planned upgrade chain:
1. 0.1.7 -> 0.2.5
2. 0.2.5 -> 0.3.4
3. 0.3.4 -> 0.4.2
```

`--apply-chain` は各 step を exact version で呼びます。

```powershell
uvx --from kansei==0.2.5 kansei update-harness --upgrade-step --no-harnessops
uvx --from kansei==0.3.4 kansei update-harness --upgrade-step --no-harnessops
uvx --from kansei==0.4.2 kansei update-harness --upgrade-step --no-harnessops
```

これにより、最新 release に古い migration を無限に保持するのではなく、各 checkpoint
release が近い範囲の migration だけを担当できます。chain 導入前の version からの最初の
一段だけは最新側の bootstrap 互換で扱います。major boundary を跨ぐ実行は
`--allow-major` が必要です。

## 利用可否

Kansei は次の順序で `hops` を解決します。

1. `KANSEI_HOPS_COMMAND`
2. `PATH` 上の `hops`
3. `uvx --isolated --from <KANSEI_HARNESSOPS_SOURCE> hops`

どれも利用できない場合、Kansei は warning を表示して続行します。command failure にしたい場合は
`--require-harnessops` を使います。

## 生成 config

`.codex/config.toml` は `providers.toml` から再生成できます。

```powershell
uvx --from kansei kansei mcp config --write --force
```

この command は `.codex/config.toml` の lock entry も更新します。
