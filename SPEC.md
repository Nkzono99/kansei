# Kansei 仕様書 v0.1

作成日: 2026-05-12  
対象: `kansei` Python package / `kansei` CLI / private local Kansei instance / Kansei MCP server  
想定公開形態: public repository + public PyPI package / private local instance  
関連プロジェクト: `harnessops`, `runops`, `paperops`

---

## 0. 要約

`Kansei` は、複数の AI 支援プロジェクトを管理するための **private local control plane** を生成・診断・更新・MCP公開する CLI パッケージである。

`Kansei` の目的は、研究、論文執筆、HPC 実験、コード開発、ハーネス改善をひとつの private root project から **安全に管制**することにある。`Kansei` は個々のプロジェクトの中身を直接抱え込まない。個別領域の正本は `runops`、`paperops`、将来の `codeops`、各 project リポジトリに残し、`Kansei` は project registry、provider registry、MCP 接続、dashboard、local knowledge、delegation policy を扱う。

`Kansei` は次の二面性を持つ。

```text
公開 package / 公開 repo:
  kansei
    - init / doctor / status / update-harness / mcp serve
    - template
    - schema
    - safe update engine
    - provider orchestration
    - private project data を含まない

private local instance:
  ~/work/kansei
    - 実際の projects.toml
    - providers.toml
    - local knowledge
    - dashboards
    - HPC endpoint metadata
    - unpublished paper notes
    - private Codex/MCP config
```

`Kansei` は「プロジェクトを管理するプロジェクト」だが、実装上は「公開CLIで保守される private instance」として扱う。

---

## 1. 名前とプロダクトID

### 1.1 名称

- project 名: `Kansei`
- GitHub repository: `Nkzono99/kansei`
- PyPI distribution: `kansei`
- Python import 名: `kansei`
- CLI command 名: `kansei`
- local instance の既定 path: `~/work/kansei`

### 1.2 名前の意味

`Kansei` は複数の意味を持つ。

- 管制: 複数プロジェクト、MCP provider、Codex session、SSH/HPC 接続を管制する。
- 完成: プロジェクトを完了・投稿・実験完遂へ進める。
- 感性: AI に委譲しても、最終判断、優先順位、研究者としての直観を残す。
- 関西: local/private な識別性を持つ。

`Kansei` は AI agent にすべてを任せる自動化システムではない。人間の判断を中心に置き、AI agent が安全に状態を読み、計画し、限定された操作を実行するための管制ハーネスである。

---

## 2. 背景

ユーザーは次のようなプロジェクトを並列運用している。

- ローカルのコード開発プロジェクト
- Codex を使うハーネス開発プロジェクト
- HPC / Slurm 上の simulation project
- 論文執筆プロジェクト
- 実験、解析、読書メモ、研究判断
- private local knowledge

VS Code recent や個別 repository の AGENTS.md だけでは、横断的な優先順位、状態確認、HPC 接続、論文進捗、Codex 委譲、MCP provider 管理が破綻しやすい。

`Kansei` はこの問題に対し、root project を単なる workspace ではなく、**AI agent が扱える project operations layer** として定義する。

---

## 3. コア思想

### 3.1 Kansei は control plane であり、mega workspace ではない

`Kansei` は全 project のソースコードを内部に取り込まない。各 project は独立した repository / directory / remote environment に残す。

`Kansei` が持つもの:

```text
- project registry
- provider registry
- MCP connection config
- dashboard
- local knowledge
- runbook
- delegation policy
- safe update metadata
```

`Kansei` が持たないもの:

```text
- runops project の simulation output 正本
- paperops project の manuscript 正本
- code project の source tree 正本
- HPC job の実体
- 未サニタイズの外部共有フィードバック束
```

### 3.2 CLI が状態変更の正本である

Agent、MCP tools、Codex prompts、VS Code integration は UX layer である。状態変更の正本は `kansei` CLI、domain operation の正本は `runo` / `pops` / `hops` CLI である。

原則:

```text
Agent / MCP / prompt
  -> kansei CLI
    -> provider CLI or provider MCP
      -> project state
```

Agent は `.kansei/`、`.harnessops/`、`runs/`、`manuscript/`、`notes/` などを直接再編しない。必要な操作は CLI または MCP tool に委譲する。

### 3.3 Domain state は domain provider が持つ

- HPC run、Slurm、manifest、campaign、survey は `runops` が持つ。
- 論文、claim/evidence、manuscript、refs、submission は `paperops` が持つ。
- ハーネス改善、failure、feedback、evaluation、decision は `harnessops` が持つ。
- 将来の code project health、test、PR、release は `codeops` または generic provider が持つ。

`Kansei` は domain logic を再実装しない。`Kansei` は routing / aggregation / delegation を行う。

### 3.4 まず読み、次に計画し、最後に適用する

すべての操作は次の順で設計する。

```text
read-only status / inspect
  -> plan
    -> explicit approval
      -> apply
```

`Kansei` は `plan_*` と `apply_*` を分離する。

```text
良い:
  kansei.dashboard.plan_today
  kansei.dashboard.write_today
  runops.job.plan_submit
  runops.job.submit
  paperops.manuscript.plan_revision
  paperops.manuscript.apply_revision

悪い:
  kansei.do_everything
  runops.job.run
  paperops.rewrite
```

### 3.5 既定で private

`Kansei` local instance は private である。公開 package に含めるのはテンプレート、schema、CLI、MCP server 実装だけにする。

private local instance に置いてよいもの:

```text
- actual project list
- private repo paths
- HPC host aliases
- local knowledge
- unpublished paper notes
- collaborators and constraints
- dashboard
```

public package / repo に置いてよいもの:

```text
- CLI implementation
- template
- schema
- generic MCP interface
- dummy examples
- docs
```

### 3.6 Local knowledge は prompt ではなく state である

`knowledge/` は Agent の長文 prompt 置き場ではない。検索・参照・昇格・判断更新が可能な durable memory layer である。

`AGENTS.md` にすべてを書くのではなく、`knowledge/`、`runbooks/`、`dashboards/`、`prompts/` に分離する。

### 3.7 Kansei は自己改善ループを持つ

`Kansei` は private instance で観測した摩擦を、必要に応じて `harnessops` の feedback/eval/decision ループへ渡す。

ただし、未サニタイズの private context は上流へ送らない。

```text
local friction
  -> kansei feedback draft
    -> sanitize
      -> harnessops feedback export/import
        -> eval case
          -> hypothesis
            -> decision
```

### 3.8 Update-harness は安全更新であり、同期ではない

`kansei update-harness` は public package のテンプレートや managed files を private local instance へ取り込む操作である。

これは `rsync` ではない。ユーザー所有ファイルを勝手に上書きしない。

---

## 4. 既存プロジェクトとの関係

### 4.1 HarnessOps

`harnessops` は AI Agent が出す改善候補を failure / feedback / eval case / hypothesis / scorecard / decision へ接続する運用基盤である。`hops` CLI が状態変更の正本であり、project-specific な事情をサニタイズ前に上流へ混ぜない設計を持つ。

`Kansei` は `harnessops` を次の目的で利用する。

- `Kansei` 自身の改善 feedback を整理する。
- downstream project の摩擦を upstream candidate / meta candidate に分離する。
- provider 共通の feedback loop を使う。
- safe update / managed file / migration の思想を共有する。

### 4.2 runops

`runops` は HPC / Slurm simulation project の実行基盤であり、run directory、manifest、survey、Slurm job、analysis、notes を Agent が扱える project state にする。

`Kansei` は `runops` の domain logic を再実装しない。`Kansei` は `runops` project を registry に登録し、`runops` MCP server または `runo` CLI に委譲する。

### 4.3 paperops

`paperops` は AI Agent と論文を書くための project harness であり、`pops` CLI が template 展開、診断、更新の execution kernel である。`pops update-harness` はハーネス管理ファイルだけを扱い、下流固有の `manuscript/`、`notes/`、`refs/`、`submission/` を自動上書きしない。

`Kansei` の `update-harness` も同じ原則を採用する。

### 4.4 codeops / generic-code

コード開発用の専用 provider は初期実装では作らない。最初は `generic-code` provider で扱う。

```text
generic-code:
  - git status
  - recent activity
  - test command
  - lint command
  - codex delegate
  - VS Code open
```

将来、コード系 project が増えたら `codeops` を作る。

---

## 5. 非目標

`Kansei` は次をしない。

- すべての project を mono-repo 化する。
- 各 project の domain-specific state を直接所有する。
- HPC の login node で長時間計算を直接走らせる。
- Slurm job submit / cancel / delete を既定で自動実行する。
- 論文 manuscript を確認なしに大規模 rewrite する。
- private knowledge を上流の public repo に自動送信する。
- AI の判断だけで priority / scientific decision / submission decision を確定する。
- `projects.toml`、`providers.toml`、`knowledge/`、`dashboards/` を update-harness で無断上書きする。

---

## 6. ユースケース

### 6.1 初期化

```bash
uv tool install kansei
kansei init ~/work/kansei --git --with-codex --with-mcp
cd ~/work/kansei
kansei doctor
```

### 6.2 プロジェクト登録

```bash
kansei project add \
  --id sim-cavity-hpc \
  --kind experiment \
  --provider runops \
  --location ssh \
  --host hpc-login \
  --path /work/USER/cavity
```

### 6.3 横断状態確認

```bash
kansei status
kansei dashboard today
```

### 6.4 paperops への委譲

```bash
kansei delegate paper-lunar-cavity \
  "claim-evidence mapを確認し、abstractの弱点を3点に整理して"
```

### 6.5 runops / HPC への委譲

```bash
kansei provider connect runops-hpc --tunnel
kansei delegate sim-cavity-hpc \
  "直近のfailed runを確認し、次のsbatch案だけ作って。submitはしない"
```

### 6.6 private local instance の更新

```bash
uv tool upgrade kansei
cd ~/work/kansei
kansei update-harness
kansei update-harness --apply --create-branch
```

---

## 7. パッケージ仕様

### 7.1 Python package

```toml
[project]
name = "kansei"
version = "0.1.0"
description = "AI 支援の研究運用向け private local control plane"
requires-python = ">=3.11"
dependencies = [
  "typer>=0.12",
  "rich>=13.0",
  "pydantic>=2.0",
  "tomli-w>=1.0",
  "tomlkit>=0.13",
  "jinja2>=3.1",
  "jsonschema>=4.0",
  "mcp[cli]>=1.0",
]

[project.scripts]
kansei = "kansei.cli.main:app"

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "ruff>=0.6",
  "mypy>=1.8",
]
```

### 7.2 Python version

初期実装は Python 3.11+ を標準とする。理由は以下である。

- 標準ライブラリ `tomllib` を使える。
- `paperops` と合わせやすい。
- private local tool として環境制約が比較的緩い。

必要になれば Python 3.10 互換へ広げる。

### 7.3 Build backend

`hatchling` を採用する。`harnessops`、`runops`、`paperops` と同じ方向性に合わせる。

---

## 8. リポジトリ構成

公開 `kansei` repo:

```text
kansei/
  README.md
  SPEC.md
  AGENTS.md
  pyproject.toml
  LICENSE

  src/kansei/
    __init__.py
    cli/
      __init__.py
      main.py
      commands/
        init.py
        doctor.py
        status.py
        dashboard.py
        project.py
        provider.py
        mcp.py
        update.py
        migrate.py
        backup.py
        search.py
        delegate.py
    core/
      paths.py
      config.py
      instance.py
      manifest.py
      lockfile.py
      safety.py
      git.py
      time.py
      errors.py
    registry/
      projects.py
      providers.py
      schema.py
      discovery.py
    providers/
      base.py
      generic_code.py
      harnessops.py
      runops.py
      paperops.py
      codex.py
      ssh.py
    dashboard/
      generator.py
      status_model.py
      renderer.py
    knowledge/
      search.py
      index.py
    update/
      planner.py
      applier.py
      merge.py
      managed_files.py
      migrations.py
    mcp/
      server.py
      tools.py
      resources.py
      prompts.py
      schemas.py
    templates/
      root/
        AGENTS.md.j2
        KANSEI.md.j2
        kansei.toml.j2
        projects.toml.j2
        providers.toml.j2
        gitignore.j2
        codex-config.toml.j2
      runbooks/
      prompts/
      dashboards/
      schemas/

  schemas/
    kansei.schema.json
    projects.schema.json
    providers.schema.json
    manifest.schema.json
    lock.schema.json

  tests/
    test_init.py
    test_doctor.py
    test_update_harness.py
    test_registry.py
    test_mcp_smoke.py

  docs/
    architecture.md
    mcp.md
    hpc.md
    update-harness.md
    provider-contract.md
    security.md
```

---

## 9. Private local instance の構成

`kansei init ~/work/kansei` が生成する標準構成:

```text
~/work/kansei/
  README.md
  AGENTS.md
  KANSEI.md
  kansei.toml
  projects.toml
  providers.toml

  knowledge/
    README.md
    profile.md
    research-profile.md
    writing-style.md
    hpc.md
    collaborators.md
    decision-log.md
    project-notes/
    reading-notes/

  dashboards/
    today.md
    weekly.md
    project-status.md
    provider-status.md

  runbooks/
    daily-planning.md
    hpc-experiment.md
    paper-writing.md
    code-development.md
    feedback-routing.md

  prompts/
    daily-planning.md
    project-triage.md
    paper-review.md
    hpc-failure-triage.md
    codex-delegation.md

  .codex/
    config.toml

  .kansei/
    manifest.toml
    lock.toml
    state/
      dashboard-cache.json
      provider-cache.json
      threads.toml
    cache/
    logs/
    backups/
    migrations/

  .gitignore
```

### 9.1 ファイル所有区分

`Kansei` は instance 内のファイルを3種類に分類する。

#### managed file

`Kansei` が管理する。`update-harness` の対象。

```text
AGENTS.md
KANSEI.md
runbooks/_templates/
prompts/_templates/
schemas/
.codex/config.template.toml
```

#### user-owned file

ユーザーの正本。`update-harness` は原則として触らない。

```text
projects.toml
providers.toml
knowledge/
dashboards/today.md
dashboards/weekly.md
runbooks/*.md
prompts/*.md
.env
.secrets/
```

#### generated file

再生成可能。ただし上書き前に diff を出す。

```text
README.md
.gitignore
.codex/config.toml
dashboards/project-status.md
dashboards/provider-status.md
.kansei/state/*.json
```

---

## 10. 設定ファイル

### 10.1 `kansei.toml`

private local instance のトップ設定。

```toml
schema_version = "0.1"

[workspace]
name = "Kansei"
description = "AI 支援の研究運用向け private control plane。"
timezone = "Asia/Tokyo"
default_dashboard = "dashboards/today.md"

[harness]
package = "kansei"
engine = "harnessops"
update_channel = "stable"
template_version = "0.1.0"

[privacy]
default_visibility = "private"
allow_public_export = false
sanitize_before_feedback = true

[safety]
default_apply_requires_confirmation = true
protect_user_files = true
require_git_clean_for_apply = true
hpc_submit_requires_explicit_approval = true
remote_write_requires_explicit_approval = true

[codex]
enabled = true
default_profile = "kansei"
target_delegation = "codex-exec"

[mcp]
enabled = true
default_transport = "stdio"
http_bind_host = "127.0.0.1"
http_port = 18764
```

### 10.2 `projects.toml`

project registry の正本。

```toml
schema_version = "0.1"

[[projects]]
id = "kansei"
name = "Kansei"
kind = "management"
provider = "kansei"
location = "local"
path = "~/work/kansei"
priority = "A"
active = true

[[projects]]
id = "paper-lunar-cavity"
name = "Lunar Cavity Charging Paper"
kind = "paper"
provider = "paperops"
location = "local"
path = "~/work/papers/lunar-cavity"
priority = "A"
active = true

[[projects]]
id = "sim-cavity-hpc"
name = "Cavity Simulation Campaign"
kind = "experiment"
provider = "runops"
location = "ssh"
host = "hpc-login"
path = "/work/USER/cavity"
priority = "A"
active = true

[[projects]]
id = "harnessops"
name = "HarnessOps"
kind = "code"
provider = "generic-code"
location = "local"
path = "~/work/harnessops"
priority = "B"
active = true
```

#### project field

| field | 必須 | type | description |
|---|---:|---|---|
| `id` | yes | string | 安定した識別子。CLI / MCP / dashboard で使う |
| `name` | yes | string | 人が読む名前 |
| `kind` | yes | enum | `management`, `paper`, `experiment`, `code`, `reading`, `admin`, `other` |
| `provider` | yes | string | `kansei`, `runops`, `paperops`, `harnessops`, `generic-code` |
| `location` | yes | enum | `local`, `ssh`, `cloud`, `external` |
| `path` | yes | string | local path または remote path |
| `host` | location=ssh | string | SSH host alias |
| `priority` | no | enum | `A`, `B`, `C`, `hold` |
| `active` | no | bool | dashboard対象か |
| `codex_profile` | no | string | target Codex profile |
| `tags` | no | list[string] | filtering |
| `notes` | no | string | 短いメモ |

### 10.3 `providers.toml`

provider registry の正本。

```toml
schema_version = "0.1"

[providers.kansei]
type = "local"
mode = "cli"
command = "kansei"

[providers.harnessops]
type = "local"
mode = "cli"
command = "hops"

[providers.paperops]
type = "mcp"
mode = "stdio"
command = "pops"
args = ["mcp", "serve", "--transport", "stdio"]
required = false

[providers.runops_hpc]
type = "mcp"
mode = "streamable-http"
url = "http://127.0.0.1:18765/mcp"
ssh_tunnel = "hpc-login:18765:127.0.0.1:18765"
token_env = "RUNOPS_HPC_MCP_TOKEN"
required = false

[providers.generic_code]
type = "local"
mode = "cli"
command = "git"
```

### 10.4 `.kansei/manifest.toml`

instance metadata。

```toml
schema_version = "0.1"

[instance]
name = "kansei"
root = "."
created_at = "2026-05-12T00:00:00+09:00"
created_by = "kansei 0.1.0"

[harness]
kansei_version = "0.1.0"
harnessops_version = "0.1.2"
template_version = "0.1.0"
layout_version = "0.1"

[paths]
projects = "projects.toml"
providers = "providers.toml"
knowledge = "knowledge"
dashboards = "dashboards"
runbooks = "runbooks"

[policy]
protect_user_files = true
require_git_clean_for_apply = true
```

### 10.5 `.kansei/lock.toml`

managed/generated files の checksum を記録する。

```toml
schema_version = "0.1"

[[managed_files]]
path = "AGENTS.md"
template = "root/AGENTS.md.j2"
version = "0.1.0"
checksum = "sha256:..."
owner = "kansei"
class = "managed"

[[managed_files]]
path = "KANSEI.md"
template = "root/KANSEI.md.j2"
version = "0.1.0"
checksum = "sha256:..."
owner = "kansei"
class = "managed"
```

---

## 11. CLI 仕様

### 11.1 コマンド概要

```text
kansei init
kansei doctor
kansei status
kansei dashboard today
kansei dashboard weekly
kansei project list
kansei project add
kansei project show
kansei project open
kansei project status
kansei project doctor
kansei provider list
kansei provider doctor
kansei provider connect
kansei provider disconnect
kansei delegate
kansei search
kansei mcp serve
kansei mcp config
kansei mcp inspect
kansei update-harness
kansei migrate
kansei backup
kansei version
```

### 11.2 終了コード

| code | 意味 |
|---:|---|
| 0 | 成功 |
| 1 | validation failure または user error |
| 2 | unsafe overwrite / protected operation の拒否 |
| 3 | project/provider が見つからない |
| 4 | remote connection failure |
| 5 | provider health failure |
| 6 | MCP server/client failure |
| 10 | internal error |

### 11.3 `kansei init`

private local Kansei instance を作成する。

```bash
kansei init PATH [options]
```

オプション:

```text
--git / --no-git
--with-codex / --no-codex
--with-mcp / --no-mcp
--template research|minimal|full
--force
```

挙動:

1. path を解決する。
2. `--force` が無い場合、path が存在して空でなければ拒否する。
3. 標準 directory layout を作成する。
4. template を render する。
5. `.kansei/manifest.toml` を作成する。
6. `.kansei/lock.toml` を作成する。
7. 必要に応じて `git init` する。
8. `kansei doctor` を実行する。

受け入れ確認:

```bash
kansei init /tmp/kansei-test --git --with-codex --with-mcp
cd /tmp/kansei-test
kansei doctor
```

### 11.4 `kansei doctor`

local instance を検証する。

検証項目:

- 必須 file の存在
- `kansei.toml` の schema 妥当性
- `projects.toml` の schema 妥当性
- `providers.toml` の schema 妥当性
- 重複 project ID
- 無効な provider reference
- managed file checksum の drift
- protected user-owned file が managed として追跡されていないこと
- Codex config render の妥当性
- MCP config render の妥当性
- apply operation が要求されたときの git status

オプション:

```text
--check-projects
--check-providers
--check-mcp
--check-codex
--json
```

### 11.5 `kansei status`

project と provider の status を集約する。

```bash
kansei status
kansei status --project paper-lunar-cavity
kansei status --priority A
kansei status --json
```

read-only。project state を変更してはいけない。

出力カテゴリ:

```text
- project id
- provider
- location
- priority
- 利用できる場合は git state
- provider health
- warning count
- suggested next actions
```

### 11.6 `kansei dashboard today`

`dashboards/today.md` を生成または更新する。

既定の挙動は dry-run preview。書き込みには `--write` が必要。

```bash
kansei dashboard today
kansei dashboard today --write
```

生成される section:

```markdown
# Today — YYYY-MM-DD

## Focus

## A-priority projects

## Provider 状態

## HPC queue

## Papers

## Code projects

## Decisions needed

## Deferred
```

### 11.7 `kansei project list`

登録済み project を一覧表示する。

```bash
kansei project list
kansei project list --kind paper
kansei project list --provider runops
kansei project list --active
```

### 11.8 `kansei project add`

project を `projects.toml` に追加する。これは user-owned file への書き込みだが、明示的な command なので許可される。

```bash
kansei project add --id ID --name NAME --kind KIND --provider PROVIDER --location local --path PATH
kansei project add --id ID --name NAME --kind experiment --provider runops --location ssh --host HOST --path PATH
```

ルール:

- 重複 ID は拒否する。
- provider が存在することを検証する。
- `--allow-missing` が無い限り local path の存在を検証する。
- `--skip-remote-check` が無い限り、SSH project は `ssh host test -d path` で検証する。

### 11.9 `kansei project open`

project を VS Code で開くか、shell command を表示する。

```bash
kansei project open paper-lunar-cavity
kansei project open sim-cavity-hpc --remote-vscode
```

実装:

- local: `code PATH`
- ssh: `code --remote ssh-remote+HOST PATH`
- fallback: print `ssh HOST 'cd PATH && exec $SHELL -l'`

### 11.10 `kansei provider connect`

provider connection を確立する。特に remote MCP 用の SSH tunnel を扱う。

```bash
kansei provider connect runops_hpc --tunnel
```

期待される挙動:

```bash
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

この command は、`--exec` の有無に応じて foreground tunnel を開始するか command を表示する。

### 11.11 `kansei delegate`

task を target project に委譲する。

```bash
kansei delegate PROJECT_ID "TASK"
```

mode:

```text
codex-exec:
  local: codex exec --cd PATH --profile PROFILE TASK
  ssh: ssh HOST 'cd PATH && codex exec --profile PROFILE TASK'

provider-mcp:
  call provider-specific MCP tool

print-plan:
  推奨 delegation command だけを表示
```

既定の安全性:

- read-only または planning task は許可する。
- apply/destructive task は明示的な確認を要求する。
- remote write は明示的な確認を要求する。
- HPC submit/cancel/delete は policy が許可しない限り無効。

### 11.12 `kansei search`

local knowledge と、必要に応じて project note を検索する。

```bash
kansei search "LoRA failed run cause"
kansei search "claim evidence" --project paper-lunar-cavity
```

MVP 実装:

- `knowledge/`, `runbooks/`, `dashboards/`, `prompts/` に対して `rg` を使う。
- 既定ではすべての project source tree を検索しない。
- project search には明示的な `--project` または `--all-projects` が必要。

将来の実装:

- SQLite FTS
- local embeddings
- resource-based MCP search

### 11.13 `kansei update-harness`

インストール済み `kansei` package template から local instance への安全な更新を plan / apply する。

```bash
kansei update-harness
kansei update-harness --apply
kansei update-harness --apply --create-branch
kansei update-harness --apply --allow-dirty
```

詳細仕様は section 12 にある。

### 11.14 `kansei mcp serve`

Kansei MCP server を起動する。

```bash
kansei mcp serve --transport stdio
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
```

既定: local client では stdio。

HTTP mode:

- 既定では `127.0.0.1` に bind する
- loopback でない場合は bearer token を要求する
- `--allow-public-bind` が無い限り `0.0.0.0` に bind しない

---

## 12. update-harness 仕様

### 12.1 目的

`kansei update-harness` は、private local instance の harness-managed part を、インストール済み `kansei` package version に合わせて更新する。

インストール済み Python package 自体は upgrade しない。package upgrade は `uv tool upgrade kansei`、`pipx upgrade kansei`、または同種の package manager command で行う。

### 12.2 ライフサイクル

```text
1. instance root を検出する
2. .kansei/manifest.toml を読む
3. .kansei/lock.toml を読む
4. インストール済み template catalog を読み込む
5. file を managed / generated / user-owned に分類する
6. 現在の checksum を計算する
7. local edit を検出する
8. update plan を作る
9. dry-run diff を表示する
10. --apply の場合:
    a. override が無い限り safe git state を要求する
    b. 必要に応じて branch を作る
    c. clean update を適用する
    d. unsafe update は conflict file として書く
    e. lock を更新する
    f. update log に追記する
11. doctor を実行する
```

### 12.3 update plan の出力

例:

```text
Kansei harness update plan

現在の template: 0.1.0
対象の template:  0.2.0

更新予定:
  AGENTS.md
  KANSEI.md
  schemas/projects.schema.json

再生成予定:
  .codex/config.toml

触らない:
  projects.toml
  providers.toml
  knowledge/
  dashboards/today.md

conflict:
  AGENTS.md には lock 以降の local edit がある。新しい file は AGENTS.md.new として書かれる

Run:
  kansei update-harness --apply --create-branch
```

### 12.4 conflict handling

managed file が lock checksum 以降に変更されている場合:

- 上書きしない。
- candidate を `PATH.new` として書く。
- `.kansei/logs/update-YYYYMMDD-HHMMSS.md` に conflict を記録する。
- `--strict` の場合は exit code 2 にする。

将来の option:

- previous template、current file、target template を使う 3-way merge。

### 12.5 Protected file

次の path は `update-harness` で絶対に上書きしない。

```text
projects.toml
providers.toml
knowledge/**
dashboards/today.md
dashboards/weekly.md
.env
.env.*
.secrets/**
**/*token*
**/*secret*
```

### 12.6 Git branch strategy

`--create-branch` が指定された場合:

```text
kansei/update-harness-YYYYMMDD-HHMMSS
```

git working tree が dirty で `--allow-dirty` が無い場合、apply を拒否する。

---

## 13. MCP 仕様

### 13.1 MCP の役割

`Kansei` は private local control plane を MCP 経由で公開し、Codex や他の MCP client が次を行えるようにする。

- project を一覧表示する
- status を確認する
- dashboard resource を読む
- local knowledge resource を読む
- 安全な planning tool を呼ぶ
- domain provider に委譲する
- next-action plan を生成する

MCP は標準 interface である。状態変更の正本は CLI に残す。

### 13.2 Transport

対応 transport:

```text
stdio:
  local Codex / local MCP client の既定

streamable-http:
  long-running server または SSH-tunnel 経由の remote access に使う
```

HTTP mode の既定:

```text
host: 127.0.0.1
port: 18764
path: /mcp
```

### 13.3 Namespace

すべての Kansei MCP tool は `kansei.` prefix を使う。

```text
kansei.health
kansei.workspace.status
kansei.project.list
kansei.project.inspect
kansei.project.status
kansei.provider.list
kansei.provider.status
kansei.dashboard.today
kansei.dashboard.plan_today
kansei.knowledge.search
kansei.delegate.plan
kansei.delegate.codex
```

### 13.4 Tool safety class

| class | 例 | side effect | 既定 |
|---|---|---:|---|
| read | `kansei.project.list`, `kansei.provider.status` | なし | 有効 |
| plan | `kansei.dashboard.plan_today`, `kansei.delegate.plan` | persistent write なし | 有効 |
| write | `kansei.dashboard.write_today` | local file に書く | confirmation |
| remote-read | SSH の `kansei.provider.status` | remote read | provider 接続済みなら有効 |
| remote-write | 将来の apply tool | remote write | 無効 |
| destructive | delete/archive/cancel | irreversible | 無効 |

### 13.5 MCP tools

#### `kansei.health`

入力:

```json
{}
```

出力:

```json
{
  "provider": "kansei",
  "status": "ok",
  "version": "0.1.0",
  "workspace_root": "/Users/you/work/kansei",
  "warnings": []
}
```

#### `kansei.project.list`

Input:

```json
{
  "active": true,
  "kind": "paper",
  "priority": "A"
}
```

Output:

```json
{
  "projects": [
    {
      "id": "paper-lunar-cavity",
      "name": "Lunar Cavity Charging Paper",
      "kind": "paper",
      "provider": "paperops",
      "location": "local",
      "priority": "A"
    }
  ]
}
```

#### `kansei.project.inspect`

Input:

```json
{"project_id": "sim-cavity-hpc"}
```

Output:

```json
{
  "project": {
    "id": "sim-cavity-hpc",
    "kind": "experiment",
    "provider": "runops",
    "location": "ssh",
    "host": "hpc-login",
    "path": "/work/USER/cavity"
  },
  "policy": {
    "remote_write_requires_explicit_approval": true,
    "hpc_submit_requires_explicit_approval": true
  }
}
```

#### `kansei.workspace.status`

active project 全体の status を集約する。read-only。

#### `kansei.dashboard.plan_today`

file を書かずに dashboard plan を作る。

#### `kansei.dashboard.write_today`

`dashboards/today.md` を書く。明示的に許可しない限り Codex config では既定で無効。

#### `kansei.knowledge.search`

local knowledge を検索する。明示設定が無い限り Kansei root の外は読まない。

#### `kansei.delegate.plan`

project/task に対する最も安全な delegation method を返す。

#### `kansei.delegate.codex`

`codex exec --cd` delegation を実行または提案する。`allow_execute=true` が無い限り、既定では plan tool とする。

### 13.6 MCP resource

```text
kansei://workspace/manifest
kansei://workspace/projects
kansei://workspace/providers
kansei://dashboard/today
kansei://dashboard/weekly
kansei://knowledge/profile
kansei://knowledge/hpc
kansei://knowledge/writing-style
kansei://project/{project_id}
kansei://project/{project_id}/status
kansei://provider/{provider_id}/status
```

### 13.7 MCP prompt

```text
kansei.prompt.daily_planning
kansei.prompt.project_triage
kansei.prompt.hpc_failure_triage
kansei.prompt.paper_review
kansei.prompt.codex_delegation
kansei.prompt.feedback_routing
```

prompt 例:

```text
kansei.prompt.daily_planning(project_filter?, horizon?)
```

agent に次を求める structured prompt を返す。

1. A-priority project を確認する
2. blocker を要約する
3. focus task を最大 3 つ提案する
4. apply/destructive action を避ける
5. 明示的に依頼された場合だけ dashboard を更新する

---

## 14. Provider contract

### 14.1 Provider class

```text
kansei provider:
  self/status/dashboard/update

harnessops provider:
  feedback/eval/decision loop

runops provider:
  HPC run/project/slurm の status と planning

paperops provider:
  paper/manuscript/claim/evidence/submission の status と planning

generic-code provider:
  git/test/lint/open/delegate
```

### 14.2 Python interface

```python
from typing import Protocol
from pydantic import BaseModel

class ProjectRef(BaseModel):
    id: str
    name: str
    kind: str
    provider: str
    location: str
    path: str
    host: str | None = None

class ProviderHealth(BaseModel):
    provider_id: str
    status: str
    warnings: list[str] = []

class ProjectStatus(BaseModel):
    project_id: str
    status: str
    summary: str
    warnings: list[str] = []
    next_actions: list[dict] = []

class ProviderAdapter(Protocol):
    provider_id: str

    def health(self) -> ProviderHealth: ...
    def status(self, project: ProjectRef) -> ProjectStatus: ...
    def doctor(self, project: ProjectRef) -> ProjectStatus: ...
    def delegate_plan(self, project: ProjectRef, task: str) -> dict: ...
```

### 14.3 Provider discovery

provider resolution の順序:

```text
1. `providers.toml` の explicit provider
2. インストール済み entry point（将来）
3. built-in provider
4. `generic-code` fallback
```

候補となる entry point group:

```toml
[project.entry-points."kansei.providers"]
runops = "runops.kansei_provider:provider"
paperops = "paperops.kansei_provider:provider"
```

初期実装では entry point を避け、built-in adapter を使ってよい。

---

## 15. Codex 連携

### 15.1 AGENTS.md の役割

Kansei root の `AGENTS.md` は Codex に次を指示する。

- Kansei を control plane として扱う
- target project file の直接編集を避ける
- `kansei` CLI または MCP tool を使う
- target-specific work は適切な cwd で target project に委譲する
- private knowledge を private に保つ
- apply 前に plan する

### 15.2 target project delegation

local project の場合:

```bash
codex exec --cd ~/work/papers/lunar-cavity --profile paper \
  "AGENTS.mdに従ってclaim-evidence mapを点検して"
```

SSH project の場合:

```bash
ssh hpc-login 'cd /work/USER/cavity && codex exec --profile hpc-readonly "直近ログを確認して次の実験案を作って"'
```

### 15.3 optional provider としての Codex MCP server

高度な orchestration では、Codex 自身を MCP server として動かすことがある。

```bash
codex mcp-server
```

`Kansei` v0.1 では必須ではない。MVP は `codex exec --cd` と provider MCP tool を使う。

### 15.4 `.codex/config.toml` template

```toml
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[mcp_servers.kansei]
command = "kansei"
args = ["mcp", "serve", "--transport", "stdio"]
cwd = "."
startup_timeout_sec = 20
tool_timeout_sec = 120
enabled = true
required = true

[mcp_servers.paperops]
command = "pops"
args = ["mcp", "serve", "--transport", "stdio"]
startup_timeout_sec = 20
tool_timeout_sec = 120
enabled = true
required = false

[mcp_servers.runops_hpc]
url = "http://127.0.0.1:18765/mcp"
bearer_token_env_var = "RUNOPS_HPC_MCP_TOKEN"
startup_timeout_sec = 20
tool_timeout_sec = 180
enabled = true
required = false
enabled_tools = [
  "runops.health",
  "runops.project.status",
  "runops.run.list",
  "runops.run.inspect",
  "runops.run.logs",
  "runops.slurm.queue",
  "runops.job.plan_submit"
]
disabled_tools = [
  "runops.job.submit",
  "runops.job.cancel",
  "runops.run.delete",
  "runops.fs.delete"
]
```

---

## 16. HPC / SSH 仕様

### 16.1 推奨モデル

HPC compute node は Kansei を host しない。policy が許可する場合、login node が runops MCP server を host する。

```text
Local workstation:
  Kansei + Codex + project registry

HPC login node Ubuntu:
  runops MCP server bound to 127.0.0.1

SSH tunnel:
  local 18765 -> hpc-login 127.0.0.1:18765
```

### 16.2 Login node runops MCP

HPC login node 上:

```bash
runo mcp serve \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 18765
```

local:

```bash
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

### 16.3 Safety policy

既定で許可:

```text
- queue status
- run list
- run inspect
- log read
- artifact list
- submit plan
```

既定で無効:

```text
- sbatch submit
- scancel
- delete
- archive
- remote file write
- login node 上での長時間 computation
```

### 16.4 Provider connection command

```bash
kansei provider connect runops_hpc --tunnel
```

これは次のどちらかにする。

- foreground SSH tunnel を開始する
- `--exec` に応じて正確な SSH tunnel command を表示する

v0.1 では黙って daemonize しない。

---

## 17. Dashboard 仕様

### 17.1 `dashboards/today.md`

目的: daily operation の意思決定 surface。

生成される構造:

```markdown
# Today — 2026-05-12

## 1. Focus

- [ ] ...

## 2. A-priority projects

| project | provider | status | next action |
|---|---|---|---|

## 3. HPC

## 4. Papers

## 5. Code

## 6. Decisions needed

## 7. Deferred / holding

## 8. Notes
```

`kansei dashboard today` は preview する。`--write` で書き込む。

### 17.2 Status cache

`kansei status` は provider result を `.kansei/state/provider-cache.json` に TTL 付きで cache してよい。

既定 TTL:

```text
local git: 30 sec
paperops: 60 sec
runops local: 60 sec
runops HPC queue: 30 sec
knowledge search: no cache
```

### 17.3 generated view としての dashboard

`dashboards/project-status.md` と `dashboards/provider-status.md` は generated view である。`dashboards/today.md` は human note を含みうるため user-owned とする。

---

## 18. Knowledge layer

### 18.1 考え方

`knowledge/` は durable memory であり、prompt stuffing ではない。

### 18.2 標準 file

```text
knowledge/profile.md
knowledge/research-profile.md
knowledge/writing-style.md
knowledge/hpc.md
knowledge/collaborators.md
knowledge/decision-log.md
knowledge/project-notes/
knowledge/reading-notes/
```

### 18.3 Search policy

既定の `kansei search` は次を検索する。

```text
knowledge/
runbooks/
prompts/
dashboards/
KANSEI.md
```

明示的に依頼されない限り、登録済み project root は検索しない。

### 18.4 Escalation policy

raw note -> project note -> durable knowledge -> dashboard/runbook。

```text
raw observation
  -> knowledge/project-notes/*.md
    -> knowledge/decision-log.md
      -> runbooks/*.md or providers/domain docs
```

---

## 19. セキュリティとプライバシー

### 19.1 Secret

絶対に commit しないもの:

```text
.env
.secrets/
*token*
*secret*
SSH private keys
API keys
HPC credentials
```

### 19.2 MCP HTTP

- 既定の bind host は `127.0.0.1`。
- non-loopback bind には `--allow-public-bind` が必要。
- HTTP mode は bearer token を support するべき。
- remote access には SSH tunnel を優先する。

### 19.3 Private data boundary

`Kansei` は次を区別しなければならない。

```text
private local:
  実際の project、未公開の science、collaborator、local path

sanitized feedback:
  generic failure、再現可能な最小 context、secret なし

public package:
  template、docs、schema、dummy example
```

### 19.4 適用ゲート

明示的な approval が必要な action:

```text
- writing user-owned files
- remote write
- sbatch submit
- scancel
- archive/delete
- manuscript rewrite
- provider migration apply
- harness update apply
```

---

## 20. 実装計画

### Phase 0: リポジトリ bootstrap

成果物:

```text
- pyproject.toml
- src/kansei/cli/main.py
- kansei version
- README.md
- SPEC.md
- smoke test
```

受け入れ確認:

```bash
uv run kansei version
uv run pytest -q
```

### Phase 1: init / doctor / update-harness MVP

成果物:

```text
- kansei init
- standard template
- manifest/lock
- kansei doctor
- kansei update-harness dry-run
- kansei update-harness --apply
```

受け入れ確認:

```bash
uv run kansei init /tmp/kansei-demo --git --with-codex --with-mcp
cd /tmp/kansei-demo
uv run --directory /path/to/kansei kansei doctor
uv run --directory /path/to/kansei kansei update-harness
```

### Phase 2: project/provider registry

成果物:

```text
- projects.toml parser
- providers.toml parser
- project list/add/show/open
- provider list/doctor/connect plan
```

受け入れ確認:

```bash
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
kansei project list
kansei provider list
kansei doctor --check-projects --check-providers
```

### Phase 3: status/dashboard/search

成果物:

```text
- generic-code provider status
- project status
- workspace status
- dashboard today preview/write
- `rg` による knowledge search
```

受け入れ確認:

```bash
kansei status
kansei dashboard today
kansei dashboard today --write
kansei search "HPC"
```

### Phase 4: MCP server

成果物:

```text
- kansei mcp serve --transport stdio
- kansei.health
- kansei.project.list
- kansei.project.inspect
- kansei.workspace.status
- kansei.knowledge.search
- kansei.dashboard.plan_today
```

受け入れ確認:

```bash
npx -y @modelcontextprotocol/inspector kansei mcp serve --transport stdio
```

### Phase 5: provider 連携

成果物:

```text
- paperops provider adapter
- runops provider adapter
- harnessops provider adapter
- Codex delegation helper
- SSH tunnel helper
```

受け入れ確認:

```bash
kansei delegate paper-demo "statusを確認して次の執筆タスクを出して"
kansei provider connect runops_hpc --tunnel
```

### Phase 6: hardening

成果物:

```text
- JSON schema validation
- conflict handling
- backup
- migration framework
- CI
- PyPI trusted publishing
```

---

## 21. 最小実装 skeleton

### 21.1 `src/kansei/cli/main.py`

```python
from __future__ import annotations

import typer

from kansei.cli.commands import init, doctor, status, dashboard, project, provider, mcp, update

app = typer.Typer(help="Kansei private control plane CLI")

app.add_typer(init.app, name="init")
app.add_typer(project.app, name="project")
app.add_typer(provider.app, name="provider")
app.add_typer(dashboard.app, name="dashboard")
app.add_typer(mcp.app, name="mcp")

app.command()(doctor.doctor)
app.command()(status.status)
app.command("update-harness")(update.update_harness)

@app.command()
def version() -> None:
    from kansei import __version__
    typer.echo(__version__)
```

### 21.2 `core/paths.py`

```python
from __future__ import annotations

from pathlib import Path

ROOT_MARKERS = ["kansei.toml", ".kansei/manifest.toml"]


def find_instance_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if all((path / marker).exists() for marker in ROOT_MARKERS):
            return path
    raise RuntimeError("not inside a Kansei instance")
```

### 21.3 `core/lockfile.py`

```python
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()
```

### 21.4 `mcp/server.py`

```python
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from kansei.core.paths import find_instance_root
from kansei.registry.projects import load_projects


def build_server() -> FastMCP:
    mcp = FastMCP("Kansei")

    @mcp.tool(name="kansei.health")
    def health() -> dict:
        root = find_instance_root()
        return {"provider": "kansei", "status": "ok", "workspace_root": str(root)}

    @mcp.tool(name="kansei.project.list")
    def project_list(active: bool | None = None, kind: str | None = None) -> dict:
        root = find_instance_root()
        projects = load_projects(root)
        items = [p.model_dump() for p in projects.filter(active=active, kind=kind)]
        return {"projects": items}

    @mcp.resource("kansei://workspace/projects")
    def projects_resource() -> str:
        root = find_instance_root()
        return (root / "projects.toml").read_text()

    return mcp


def run(transport: str = "stdio", host: str = "127.0.0.1", port: int = 18764) -> None:
    mcp = build_server()
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"unsupported transport: {transport}")
```

---

## 22. Test 仕様

### 22.1 Unit test

```text
- config parse
- project registry parse
- provider registry parse
- init が layout を作成する
- init 後に doctor が通る
- fresh instance で update-harness dry-run が no-op になる
- update-harness が user-owned overwrite を拒否する
- duplicate project id が失敗する
- invalid provider が失敗する
```

### 22.2 Smoke test

```bash
uv run kansei --help
uv run kansei version
uv run kansei init .tmp/kansei --git --with-codex --with-mcp
cd .tmp/kansei
kansei doctor
kansei project list
kansei dashboard today
```

### 22.3 MCP smoke test

```text
- stdio mode で MCP server を起動する
- tools/list に kansei.health が含まれる
- kansei.health を呼ぶ
- kansei://workspace/projects を読む
```

### 22.4 Safety test

```text
- update-harness が projects.toml を上書きしない
- update-harness が編集済み managed file に対して .new を書く
- provider connect が --exec なしに background tunnel を開始しない
- dashboard preview が --write なしに today.md を書かない
```

---

## 23. ドキュメント成果物

```text
README.md
SPEC.md
docs/get-started.md
docs/architecture.md
docs/update-harness.md
docs/mcp.md
docs/hpc.md
docs/security.md
docs/provider-contract.md
docs/codex.md
```

README は次に集中する:

```text
1. Kansei とは何か
2. public package と private instance の違い
3. quick start
4. safety model
5. harnessops/runops/paperops との連携
```

---

## 24. v0.1 の受け入れ条件

Kansei v0.1 は次を満たすとき受け入れ可能:

```text
- `kansei init` が利用可能な private local instance を作成する。
- `kansei doctor` が init 直後に通る。
- `kansei update-harness` が既定では書き込まずに変更を preview する。
- `kansei update-harness --apply` が managed file を更新し、user-owned file は絶対に上書きしない。
- `projects.toml` と `providers.toml` が検証される。
- `kansei project list/add/show/open` が local project で動く。
- `kansei status` が generic-code provider で動く。
- `kansei dashboard today` が有用な planning view を作る。
- `kansei search` が local knowledge を検索する。
- `kansei mcp serve --transport stdio` が少なくとも health、project list、project inspect、workspace status、knowledge search を公開する。
- `.codex/config.toml` を `providers.toml` から生成できる。
- HPC provider を、既定で non-loopback port を公開せず SSH-tunnel された Streamable HTTP として設定できる。
```

---

## 25. ロードマップ

### v0.1

- private local instance bootstrap
- safe update-harness
- registry
- generic status/dashboard
- MCP read-only tools

### v0.2

- paperops MCP 連携
- runops MCP 連携
- Codex delegate helper
- SSH tunnel helper
- dashboard write flow

### v0.3

- HarnessOps feedback 連携
- local friction capture
- sanitized upstream feedback export
- provider entry point system

### v0.4

- local SQLite FTS knowledge index
- persistent thread registry
- richer project status cache
- MCP prompt と resource template

### v0.5

- codeops provider または generic-code expansion
- test/lint/release status aggregation
- PR/issue planning tool

---

## 26. 参考リンク

- MCP Specification: https://modelcontextprotocol.io/specification/2025-11-25
- MCP Transports: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- MCP Tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- MCP Python SDK: https://modelcontextprotocol.github.io/python-sdk/
- Codex AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Codex config reference: https://developers.openai.com/codex/config-reference
- Codex MCP server / Agents SDK: https://developers.openai.com/codex/guides/agents-sdk
- HarnessOps: https://github.com/Nkzono99/harnessops
- runops: https://github.com/Nkzono99/runops
- paperops: https://github.com/Nkzono99/paperops
