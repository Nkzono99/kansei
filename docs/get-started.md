# はじめに

このガイドでは、private project data を使わずに、使い捨ての Kansei instance を作り
v0.1 CLI surface を試します。

## 必要なもの

- Python 3.11 以降。
- このリポジトリで local development command を実行するための `uv`。
- 任意: private instance に git リポジトリを作りたい場合は `git`。

## Instance を作成する

公開 package リポジトリから実行する場合:

```powershell
$kanseiSource = (Get-Location).Path
uv run kansei init .tmp/kansei-demo --git --with-codex --with-mcp --kansei-install-spec $kanseiSource
```

PyPI から実行する場合、事前インストールは不要です。

```powershell
uvx --from kansei kansei init .tmp/kansei-demo --git --with-codex --with-mcp
```

これにより `.tmp/kansei-demo` 配下に private control-plane layout が作られます。

- `kansei.toml`: instance 設定と safety policy。
- `projects.toml`: project registry。
- `providers.toml`: provider registry。
- `knowledge/`, `runbooks/`, `prompts/`, `dashboards/`: private な運用領域。
- `.kansei/manifest.toml` と `.kansei/lock.toml`: safe update 用の package-managed metadata。
- `.agents/skills/kansei-control-plane`: instance 操作用の Codex skill。
- `.agents/skills/feedback-kansei`: Kansei upstream への feedback をサニタイズする skill。
- `.codex/config.toml`: `--with-codex` を渡した場合だけ生成されます。

生成された instance は private workspace state です。実在する local path、credential、
未公開 note、collaborator 固有の情報を公開 package リポジトリに戻さないでください。

`uvx --from kansei` は一時 environment で command を実行します。以後の command も
project-local な Kansei `.venv` ではなく、この uvx 経路を標準にします。互換用に
instance 内へ Kansei をインストールしたい場合だけ `--bootstrap` を使います。local
checkout から legacy bootstrap する場合は `--kansei-install-spec C:\path\to\kansei` を
指定します。

HarnessOps が `hops` として利用できる場合、init は instance 内で
`hops init --profile generic-code` も実行します。インストール済み command ではなく local
HarnessOps checkout を使う場合は次のように設定します。

```powershell
$env:KANSEI_HARNESSOPS_SOURCE = "C:\path\to\harnessops"
```

HarnessOps feedback overlay を持たない素の Kansei instance が欲しい場合は
`--no-harnessops` を使います。

## Instance を検証する

```powershell
uvx --from kansei kansei doctor --root .tmp/kansei-demo
uvx --from kansei kansei version
```

`doctor` は期待される layout、必須 TOML file、registry shape、managed-file checksum を
確認します。managed file への local edit は warning として報告されるので、保持するか
後で生成 update を取り込むかを判断できます。

## Instance 内で作業する

ほとんどの command は現在 directory から最も近い Kansei instance を探索します。

```powershell
Set-Location .tmp/kansei-demo
uvx --from kansei kansei project list
uvx --from kansei kansei status
uvx --from kansei kansei dashboard today
```

以下の例では、現在 directory が `.tmp/kansei-demo` である前提で
`uvx --from kansei kansei ...` を使っています。`kansei` を環境にインストール済みの場合は、
この prefix を省いて `kansei ...` を直接実行できます。

別の場所から実行するときは、利用できる command では root flag を指定します。例:
`kansei doctor --root PATH`, `kansei update-harness --root PATH`,
`kansei mcp config --root PATH`, `kansei backup --root PATH`。

## ローカル code project を登録する

TOML を手で書き換える代わりに CLI で registry を編集します。

```powershell
uvx --from kansei kansei project add `
  --id demo-code `
  --name "Demo Code" `
  --kind code `
  --provider generic-code `
  --location local `
  --path C:\path\to\project `
  --priority B
```

登録内容を確認します。

```powershell
uvx --from kansei kansei project show demo-code
uvx --from kansei kansei project status demo-code
uvx --from kansei kansei project open demo-code
```

`project open` は既定では解決された path を表示します。OS にその path を開かせたい場合
だけ `--exec` を追加します。

## 書く前に preview する

Kansei は read、plan、apply を分けます。

```powershell
uvx --from kansei kansei dashboard today
uvx --from kansei kansei dashboard today --write
uvx --from kansei kansei update-harness
uvx --from kansei kansei update-harness --apply
```

dashboard command は `--write` が無い限り Markdown を preview します。
`update-harness` は `--apply` が無い限り dry run です。HarnessOps への chained call も
同じ mode に従い、dry run では `hops update-harness --dry-run`、apply では
`hops update-harness` を呼びます。

## 任意の MCP setup

`providers.toml` から生成される Codex MCP config を preview します。

```powershell
uvx --from kansei kansei mcp config
uvx --from kansei kansei mcp inspect
```

内容を確認したあとで `.codex/config.toml` を書きます。

```powershell
uvx --from kansei kansei mcp config --write --force
```

既存の generated config と provider 由来の出力が異なる場合、上書きには `--force` が必要です。
必ず preview を確認してから使ってください。
