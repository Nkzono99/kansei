# Provider contract

provider は、Kansei が domain state を所有せずに、登録済み project を確認したり、
作業計画を作ったりするための境界です。

## データモデル

`ProjectRef` には provider が必要とする registry data が入ります。

- `id`, `name`, `kind`, `provider`, `location`, `path`
- optional: `host`, `priority`, `active`, `tags`, `notes`

provider method は次を返します。

- `ProviderHealth`: provider ID、status、summary、warning。
- `ProjectStatus`: project ID、provider ID、status、summary、warning、次のアクション、details。
- `delegate_plan`: 実行前に確認できる安全な command plan。

## 組み込み provider

- `generic-code`: local worktree status の確認に `git` を使います。
- `kansei`: control-plane リポジトリに対して `generic-code` と同じ挙動を使います。
- `harnessops`, `paperops`, `runops`: v0.1 の domain adapter です。CLI availability を
  報告し、安全な delegation plan を作ります。domain write の完全実装はまだ行いません。

## Registry 解決順序

provider resolution の順序は次のとおりです。

1. `providers.toml` の explicit provider config
2. built-in provider adapter
3. `generic-code` fallback

将来のリリースでは、entry point ベースの provider plugin を追加する可能性があります。

## Registry フィールド

provider record は `providers.toml` の `[providers.<id>]` に置きます。対応する `type` は
`local`, `mcp`, `ssh`, `external` です。local provider と SSH provider には `command` が
必要です。MCP stdio provider にも `command` が必要です。stdio ではない MCP provider には
`url` が必要です。任意フィールドには `args`, `ssh_tunnel`, `token_env`, `required` があります。

## 安全性の分類

provider は read/status/doctor/delegation planning を先に実装します。remote write、
HPC submit/cancel/delete、archive/delete、manuscript rewrite は明示的な承認を必要とし、
status command の裏で隠れて実行されてはいけません。

## SSH tunnel

`providers.toml` では次のように宣言できます。

```toml
ssh_tunnel = "hpc-login:18765:127.0.0.1:18765"
```

`kansei provider connect runops_hpc --tunnel` は次を表示します。

```powershell
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

実際に foreground tunnel を開始したい場合だけ `--exec` を使います。
