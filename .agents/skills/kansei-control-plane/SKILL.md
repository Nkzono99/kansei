---
name: kansei-control-plane
description: Kansei の private local control-plane instance を安全に扱う。Codex が Kansei instance root の中またはそれを対象に作業するとき、instance の inspect/init/doctor/update、project/provider registry の確認、dashboard planning、knowledge search、MCP exposure、delegation planning、または private target-project state を public kansei package に漏らさない判断が必要なときに使う。
---

# Kansei Control Plane

## 基本ルール

Kansei root は control plane として扱い、target project を直接再編する場所として扱わないでください。
まず読み、次に計画し、適用は `kansei` CLI または明示承認された safe write path だけで行います。

## ワークフロー

1. `kansei.toml` と `.kansei/manifest.toml` の両方を見つけて instance root を確認します。
2. write を提案する前に read-only check を実行します。例:
   `kansei doctor`, `kansei project list`, `kansei provider list`,
   `kansei status`, `kansei dashboard today`,
   `scripts/check_instance.py <instance-root>`。
3. 触ってよい file を分類します。`projects.toml`, `providers.toml`,
   `knowledge/`, `dashboards/today.md`, `.env`, `.secrets/` は user-owned として扱います。
4. harness update は `kansei update-harness` で preview します。ユーザーが update を依頼し、
   preview を理解できている場合だけ `--apply` を使います。
5. target-project 作業では cwd を target project に移すか、設定済み provider に委譲します。
   Kansei root から target-project file を直接編集しないでください。
6. MCP/provider 作業は既定で read-only または plan-only にします。remote write、HPC
   submit/cancel、delete/archive、manuscript rewrite は current task での明示承認が必要です。

## よく使うコマンド

```powershell
Push-Location <instance-root>
uv run kansei doctor --root <instance-root>
uv run kansei project list
uv run kansei provider list
uv run kansei status
uv run kansei dashboard today
uv run kansei search "query"
uv run kansei update-harness --root <instance-root>
uv run kansei mcp inspect --root <instance-root>
Pop-Location
```

## 同梱リソース

- ownership、preview/apply 境界、delegation、MCP safety が曖昧な場合は
  `references/control-plane-workflow.md` を読みます。
- 初見の instance を扱う前に、package import なしで構造を確認したい場合は
  `scripts/check_instance.py <instance-root>` を実行します。
