# CLI リファレンス

このページは v0.1 で実装されているコマンド体系を説明します。正確な最新の
Typer 出力は `kansei --help` または各 subcommand の `--help` を確認してください。

## トップレベルコマンド

```powershell
kansei init PATH [--git] [--with-codex] [--with-mcp] [--force]
  [--bootstrap/--no-bootstrap] [--kansei-install-spec SPEC]
  [--require-bootstrap]
  [--harnessops/--no-harnessops] [--harnessops-profile PROFILE]
  [--with-harnessops-agent-bridge] [--require-harnessops]
kansei doctor [--root PATH] [--json] [--check-mcp] [--check-codex]
kansei status [--project ID] [--priority A|B|C|hold] [--json]
kansei search QUERY [--limit N]
kansei delegate PROJECT_ID TASK [--json] [--exec]
kansei update-harness [--root PATH] [--apply]
  [--plan] [--apply-chain] [--target latest|VERSION|MAJOR.MINOR] [--allow-major]
  [--harnessops/--no-harnessops] [--harnessops-profile PROFILE]
  [--with-harnessops-agent-bridge] [--require-harnessops]
kansei backup [--root PATH] [--output PATH]
kansei migrate [--root PATH] [--json]
kansei version
```

## Bootstrap

`kansei init` は生成した instance 内に project-local な Kansei `.venv` を既定では
作りません。一般的な初回実行は次の形です。

```powershell
uvx --from kansei kansei init ~/work/kansei
cd ~/work/kansei
uvx --from kansei kansei doctor
```

標準の CLI 実行は `uvx --from kansei kansei <command>` です。互換用に
project-local な `.venv` が必要な場合だけ `--bootstrap` を使います。bootstrap 問題を
command failure にするには `--require-bootstrap`、local development checkout から
インストールする場合は `--kansei-install-spec PATH_OR_PACKAGE_SPEC` を指定します。

`kansei init` は instance-local skill として `.agents/skills/kansei-control-plane` と
`.agents/skills/feedback-kansei` も生成します。前者は instance 操作用、後者は
Kansei upstream へのサニタイズ済み feedback / issue 下書き用です。

## HarnessOps 連鎖

`hops` command が利用できる場合、`kansei init` は既定で
`hops init --profile generic-code` に連鎖します。`kansei update-harness` は
`hops update-harness` に連鎖します。dry-run では `hops update-harness --dry-run` を使い、
`.harnessops/project.toml` が無い古い instance では、Kansei 側の command mode に
合わせて `hops init` の dry-run または apply を先に実行します。

連鎖を省くには `--no-harnessops` を使います。`hops` が見つからないときに warning では
なくコマンドを失敗扱いにしたい automation では `--require-harnessops` を指定します。
`hops` が `PATH` に無い場合は、`KANSEI_HOPS_COMMAND` または
`KANSEI_HARNESSOPS_SOURCE` に local HarnessOps checkout を設定してください。Kansei は
`uvx --isolated --from <source> hops ...` を実行できます。

## Versioned upgrade chain

`uvx` を標準動線にしているため、Kansei は古い instance を最新 runtime だけで直接
migration し続ける必要はありません。`.kansei/manifest.toml` に記録された最後の
`harness.kansei_version` を起点に、PyPI release の minor checkpoint を順番に踏む
upgrade chain を計画できます。

```powershell
uvx --from kansei kansei update-harness --plan
uvx --from kansei kansei update-harness --apply-chain
uvx --from kansei kansei update-harness --target 0.3
uvx --from kansei kansei update-harness --target latest --allow-major --apply-chain
```

`--plan` は書き込みません。`--apply-chain` は各 checkpoint を exact version で
`uvx --from kansei==<version> kansei update-harness --upgrade-step --no-harnessops`
として呼びます。major version を跨ぐ chain は `--allow-major` が無い限り実行しません。
通常の `update-harness` dry run / `--apply` は、現在実行中の Kansei runtime だけで扱える
近い更新に使います。

## Project 系コマンド

```powershell
kansei project list [--active/--no-active] [--kind KIND] [--priority PRIORITY]
kansei project show PROJECT_ID
kansei project add --id ID --name NAME --kind KIND --provider PROVIDER --location LOCATION --path PATH
kansei project open PROJECT_ID [--exec]
kansei project status PROJECT_ID
kansei project doctor PROJECT_ID
```

`project add` は、ユーザーが registry edit を明示しているため `projects.toml` を書きます。
重複した project ID は拒否されます。

## Provider 系コマンド

```powershell
kansei provider list
kansei provider doctor [--provider-id PROVIDER_ID]
kansei provider connect PROVIDER_ID [--tunnel] [--exec]
kansei provider disconnect PROVIDER_ID
```

`provider connect --tunnel` は既定では SSH tunnel command を表示します。実際に
foreground tunnel を開始するのは `--exec` が指定された場合だけです。

## Dashboard 系コマンド

```powershell
kansei dashboard today [--write]
kansei dashboard weekly [--write]
```

既定は preview です。書き込みには `--write` が必要です。

## MCP 系コマンド

```powershell
kansei mcp serve --transport stdio
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
kansei mcp config [--root PATH] [--write] [--force]
kansei mcp inspect [--root PATH]
```

`mcp config` は `providers.toml` から `.codex/config.toml` を render します。既存の
config と差分がある場合、上書きには `--force` が必要です。

## 終了時の挙動

validation error、存在しない project/provider、unsafe write は non-zero exit になります。
v0.1 では破壊的操作と remote write を既定のコマンド体系の外に
置いています。
