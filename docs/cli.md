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
  [--harnessops/--no-harnessops] [--harnessops-profile PROFILE]
  [--with-harnessops-agent-bridge] [--require-harnessops]
kansei backup [--root PATH] [--output PATH]
kansei migrate [--root PATH] [--json]
kansei version
```

## Bootstrap

`kansei init` は生成した instance 内に `.venv` を作り、既定で
`kansei==<current-version>` をインストールします。一般的な初回実行は次の形です。

```powershell
uvx --from kansei kansei init ~/work/kansei
cd ~/work/kansei
.venv\Scripts\activate
kansei doctor
```

`uvx --from kansei` がインストールするのは一時的な execution environment だけです。
project-local な `.venv` に Kansei をインストールするのは init bootstrap の役割です。
bootstrap を省くには `--no-bootstrap`、bootstrap 問題を command failure にするには
`--require-bootstrap` を使います。local development checkout からインストールする場合は
`--kansei-install-spec PATH_OR_PACKAGE_SPEC` を指定します。

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
