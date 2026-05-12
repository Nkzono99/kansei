# セキュリティ

package リポジトリは public ですが、Kansei は既定では private です。

## コミットしてはいけないもの

- `.env`
- `.secrets/`
- API key または bearer token
- SSH private key
- HPC credential
- 実在する local instance 由来の private project path
- 未公開の paper note や collaborator 固有の制約

## 適用ゲート

既定の実装は read と plan を優先します。次の操作には明示的なユーザー意図が必要です。

- user-owned file の書き込み
- instance-local な `.venv` の作成または更新
- generated `.codex/config.toml` の上書き
- `.agents/skills/feedback-kansei` による GitHub issue 作成
- remote write
- Slurm submit/cancel/delete
- archive/delete
- manuscript rewrite
- harness update apply
- `hops` 経由の HarnessOps chained update

## MCP

HTTP MCP は、明確な access-control plan が無い限り `127.0.0.1` に bind してください。
remote provider access には SSH tunnel を優先します。

## フィードバック境界

ローカルで起きた摩擦を upstream に export する場合は、先に sanitize します。
private project data ではなく、再現可能で汎用的な失敗内容を残してください。

HarnessOps overlay write は `hops` の責務です。Kansei は `hops init` や
`hops update-harness` を呼ぶことはありますが、`.harnessops/`, `harness-feedback/`,
`harness-lab/` を直接組み替えてはいけません。
