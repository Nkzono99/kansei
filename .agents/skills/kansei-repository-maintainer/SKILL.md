---
name: kansei-repository-maintainer
description: Kansei の公開 Python package / CLI リポジトリを保守するときに使う。Codex が src/kansei、templates、docs、GitHub workflow、PyPI publishing、repo-local HarnessOps 連携を変更し、private instance data や target project state を public package に漏らさない判断が必要なときに使う。
---

# Kansei Repository Maintainer

## 基本ルール

このリポジトリは public package の正本です。実在する private instance の
`projects.toml`、`providers.toml`、`knowledge/`、dashboard、HPC endpoint、
未公開 note、collaborator 固有情報を入れないでください。

## 作業の分け方

1. 公開 package の挙動は `src/kansei/` に実装します。
2. `kansei init` や `kansei update-harness` で instance に配る file は
   `src/kansei/templates/` に置きます。
3. このリポジトリだけで使う agent guidance は repo root の `.agents/skills/` に置きます。
4. 生成 instance 側で使う skill は `src/kansei/templates/agents/skills/` に置き、
   managed template として lock に載せます。
5. HarnessOps overlay は `hops` CLI に委譲し、`.harnessops/`、`harness-feedback/`、
   `harness-lab/` の構造を手で組み替えません。

## 検証

変更に応じて次を実行します。

```powershell
uv run --extra dev pytest -q
uv run --extra dev ruff check .
uv run --extra dev mypy src\kansei
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp --no-bootstrap --no-harnessops
uv run kansei doctor --root .tmp/kansei-demo
```

skill を作成・更新した場合は、UTF-8 mode で skill validator を実行してください。
