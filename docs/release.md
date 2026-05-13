# リリースノート

Kansei v0.1 は alpha 版の control-plane package です。実装済みの範囲は、
local instance 作成、検証、registry 操作、dashboard render、安全な harness update、
backup、read/plan-oriented な MCP surface です。

## v0.1.0

実装済み:

- package template から private local instance を作る `kansei init`。
- `uvx --from kansei kansei <command>` を標準にした init flow。
- layout、TOML、registry、managed-file を検証する `kansei doctor`。
- 登録済み project を list/show/add/open/check する `kansei project` command。
- provider を list し、built-in provider health を確認し、foreground SSH tunnel を
  計画または実行する `kansei provider` command。
- local operating view を表示する `kansei status`, `kansei dashboard today`,
  `kansei dashboard weekly`。
- Markdown knowledge、runbook、prompt、dashboard surface を検索する `kansei search`。
- package-managed file 向けの `kansei update-harness` dry-run/apply flow。
- `kansei mcp serve`, `kansei mcp config`, `kansei mcp inspect`。
- local control-plane file を zip archive する `kansei backup`。
- 現在の layout version に対する migration status を確認する `kansei migrate`。

## 安全性の考え方

- private instance data は private instance 内に残します。
- 可能な限り read command と preview command を既定にします。
- file write には `--write` や `--apply` のような明示 flag が必要です。
- remote connection helper は `--exec` が無い限り plan を表示します。
- `update-harness` は managed file だけを更新し、user-owned state を保護します。

## 現在の制限

- v0.1 では MCP write tool は実装していません。
- `provider disconnect` は background tunnel process を管理しません。
- runops、paperops、harnessops など domain-specific な挙動は provider 設定と
  delegation surface として表現します。それぞれの domain state は provider project 側に残ります。
- code project health は意図的に generic です。将来の dedicated codeops provider を
  置き換えるものではありません。
