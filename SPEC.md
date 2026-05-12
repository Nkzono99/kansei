# Kansei 仕様書 v0.1

作成日: 2026-05-12  
対象: `kansei` Python package / `kansei` CLI / private local Kansei instance / Kansei MCP server  
想定公開形態: public repository + public PyPI package / private local instance  
関連プロジェクト: `harnessops`, `runops`, `paperops`

---

## 0. 要約

`Kansei` は、複数の AI 支援プロジェクトを管理するための **private local control plane** を生成・診断・更新・MCP公開する CLI パッケージである。

`Kansei` の目的は、研究、論文執筆、HPC 実験、コード開発、ハーネス改善をひとつの private root project から **安全に管制**することにある。`Kansei` は個々のプロジェクトの中身を直接抱え込まない。個別領域の正本は `runops`、`paperops`、将来の `codeops`、各 project repository に残し、`Kansei` は project registry、provider registry、MCP 接続、dashboard、local knowledge、delegation policy を扱う。

`Kansei` は次の二面性を持つ。

```text
public package / public repo:
  kansei
    - init / doctor / status / update-harness / mcp serve
    - templates
    - schema
    - safe update engine
    - provider orchestration
    - no private project data

private local instance:
  ~/work/kansei
    - actual projects.toml
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

- Project name: `Kansei`
- GitHub repository: `Nkzono99/kansei`
- PyPI distribution: `kansei`
- Python import: `kansei`
- CLI command: `kansei`
- Local instance default path: `~/work/kansei`

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

### 3.4 Read first, plan second, apply last

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

### 3.5 Private by default

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
- private knowledge を上流 public repo に自動送信する。
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
description = "Private local control plane for AI-assisted research operations"
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

## 8. Repository layout

public `kansei` repo:

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

## 9. Private local instance layout

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

### 9.1 File ownership classes

`Kansei` は instance 内のファイルを3種類に分類する。

#### managed files

`Kansei` が管理する。`update-harness` の対象。

```text
AGENTS.md
KANSEI.md
runbooks/_templates/
prompts/_templates/
schemas/
.codex/config.template.toml
```

#### user-owned files

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

#### generated files

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

## 10. Configuration files

### 10.1 `kansei.toml`

private local instance のトップ設定。

```toml
schema_version = "0.1"

[workspace]
name = "Kansei"
description = "Private control plane for AI-assisted research operations."
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

#### project fields

| field | required | type | description |
|---|---:|---|---|
| `id` | yes | string | stable identifier. CLI / MCP / dashboard で使う |
| `name` | yes | string | human-readable name |
| `kind` | yes | enum | `management`, `paper`, `experiment`, `code`, `reading`, `admin`, `other` |
| `provider` | yes | string | `kansei`, `runops`, `paperops`, `harnessops`, `generic-code` |
| `location` | yes | enum | `local`, `ssh`, `cloud`, `external` |
| `path` | yes | string | local path or remote path |
| `host` | location=ssh | string | SSH host alias |
| `priority` | no | enum | `A`, `B`, `C`, `hold` |
| `active` | no | bool | dashboard対象か |
| `codex_profile` | no | string | target Codex profile |
| `tags` | no | list[string] | filtering |
| `notes` | no | string | short memo |

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

## 11. CLI specification

### 11.1 Command overview

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

### 11.2 Exit codes

| code | meaning |
|---:|---|
| 0 | success |
| 1 | validation failure or user error |
| 2 | unsafe overwrite / protected operation rejected |
| 3 | project/provider not found |
| 4 | remote connection failure |
| 5 | provider health failure |
| 6 | MCP server/client failure |
| 10 | internal error |

### 11.3 `kansei init`

Creates a private local Kansei instance.

```bash
kansei init PATH [options]
```

Options:

```text
--git / --no-git
--with-codex / --no-codex
--with-mcp / --no-mcp
--template research|minimal|full
--force
```

Behavior:

1. Resolve path.
2. Refuse if path exists and is non-empty unless `--force`.
3. Create standard directory layout.
4. Render templates.
5. Create `.kansei/manifest.toml`.
6. Create `.kansei/lock.toml`.
7. Optionally `git init`.
8. Run `kansei doctor`.

Acceptance:

```bash
kansei init /tmp/kansei-test --git --with-codex --with-mcp
cd /tmp/kansei-test
kansei doctor
```

### 11.4 `kansei doctor`

Validates the local instance.

Checks:

- required files exist
- `kansei.toml` schema validity
- `projects.toml` schema validity
- `providers.toml` schema validity
- duplicate project IDs
- invalid provider references
- managed file checksum drift
- protected user-owned files not tracked as managed
- Codex config render validity
- MCP config render validity
- git status when apply operations are requested

Options:

```text
--check-projects
--check-providers
--check-mcp
--check-codex
--json
```

### 11.5 `kansei status`

Aggregates project and provider status.

```bash
kansei status
kansei status --project paper-lunar-cavity
kansei status --priority A
kansei status --json
```

Read-only. It must not modify project state.

Output categories:

```text
- project id
- provider
- location
- priority
- git state if available
- provider health
- warning count
- suggested next actions
```

### 11.6 `kansei dashboard today`

Generates or updates `dashboards/today.md`.

Default behavior is dry-run preview. Writing requires `--write`.

```bash
kansei dashboard today
kansei dashboard today --write
```

Generated sections:

```markdown
# Today — YYYY-MM-DD

## Focus

## A-priority projects

## Provider status

## HPC queue

## Papers

## Code projects

## Decisions needed

## Deferred
```

### 11.7 `kansei project list`

Lists registered projects.

```bash
kansei project list
kansei project list --kind paper
kansei project list --provider runops
kansei project list --active
```

### 11.8 `kansei project add`

Adds a project to `projects.toml`. This is a user-owned file write, but it is an explicit command and therefore allowed.

```bash
kansei project add --id ID --name NAME --kind KIND --provider PROVIDER --location local --path PATH
kansei project add --id ID --name NAME --kind experiment --provider runops --location ssh --host HOST --path PATH
```

Rules:

- Refuse duplicate IDs.
- Validate provider exists.
- Validate local path exists unless `--allow-missing`.
- Validate SSH project with `ssh host test -d path` unless `--skip-remote-check`.

### 11.9 `kansei project open`

Opens a project in VS Code or prints a shell command.

```bash
kansei project open paper-lunar-cavity
kansei project open sim-cavity-hpc --remote-vscode
```

Implementation:

- local: `code PATH`
- ssh: `code --remote ssh-remote+HOST PATH`
- fallback: print `ssh HOST 'cd PATH && exec $SHELL -l'`

### 11.10 `kansei provider connect`

Establishes provider connection, especially SSH tunnel for remote MCP.

```bash
kansei provider connect runops_hpc --tunnel
```

Expected behavior:

```bash
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

This command may either start a foreground tunnel or print the command unless `--exec`.

### 11.11 `kansei delegate`

Delegates a task to a target project.

```bash
kansei delegate PROJECT_ID "TASK"
```

Modes:

```text
codex-exec:
  local: codex exec --cd PATH --profile PROFILE TASK
  ssh: ssh HOST 'cd PATH && codex exec --profile PROFILE TASK'

provider-mcp:
  call provider-specific MCP tool

print-plan:
  print recommended delegation command only
```

Default safety:

- Read-only or planning tasks are allowed.
- Apply/destructive tasks require explicit confirmation.
- Remote write requires explicit confirmation.
- HPC submit/cancel/delete is disabled unless policy allows.

### 11.12 `kansei search`

Searches local knowledge and optionally project notes.

```bash
kansei search "LoRA failed run cause"
kansei search "claim evidence" --project paper-lunar-cavity
```

MVP implementation:

- Use `rg` over `knowledge/`, `runbooks/`, `dashboards/`, `prompts/`.
- Do not search all project source trees by default.
- Project search requires explicit `--project` or `--all-projects`.

Future implementation:

- SQLite FTS
- local embeddings
- resource-based MCP search

### 11.13 `kansei update-harness`

Plans and applies safe updates from installed `kansei` package templates to the local instance.

```bash
kansei update-harness
kansei update-harness --apply
kansei update-harness --apply --create-branch
kansei update-harness --apply --allow-dirty
```

Detailed spec is in section 12.

### 11.14 `kansei mcp serve`

Runs Kansei MCP server.

```bash
kansei mcp serve --transport stdio
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
```

Default: stdio for local clients.

HTTP mode:

- bind to `127.0.0.1` by default
- require bearer token if not loopback
- never bind to `0.0.0.0` unless `--allow-public-bind`

---

## 12. update-harness specification

### 12.1 Purpose

`kansei update-harness` updates the harness-managed parts of a private local instance to match the installed `kansei` package version.

It does not upgrade the installed Python package itself. Package upgrade is done by `uv tool upgrade kansei`, `pipx upgrade kansei`, or similar package manager commands.

### 12.2 Lifecycle

```text
1. detect instance root
2. read .kansei/manifest.toml
3. read .kansei/lock.toml
4. load installed template catalog
5. classify files as managed / generated / user-owned
6. calculate current checksums
7. detect local edits
8. create update plan
9. display dry-run diff
10. if --apply:
    a. require safe git state unless overridden
    b. optionally create branch
    c. apply clean updates
    d. write conflict files for unsafe updates
    e. update lock
    f. append update log
11. run doctor
```

### 12.3 Update plan output

Example:

```text
Kansei harness update plan

Current template: 0.1.0
Target template:  0.2.0

Will update:
  AGENTS.md
  KANSEI.md
  schemas/projects.schema.json

Will regenerate:
  .codex/config.toml

Will not touch:
  projects.toml
  providers.toml
  knowledge/
  dashboards/today.md

Conflicts:
  AGENTS.md has local edits since lock. New file will be written as AGENTS.md.new

Run:
  kansei update-harness --apply --create-branch
```

### 12.4 Conflict handling

If a managed file has changed since the lock checksum:

- Do not overwrite.
- Write candidate as `PATH.new`.
- Record conflict in `.kansei/logs/update-YYYYMMDD-HHMMSS.md`.
- Exit code 2 if `--strict`.

Future option:

- 3-way merge using previous template, current file, target template.

### 12.5 Protected files

The following paths are never overwritten by `update-harness`:

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

If `--create-branch` is set:

```text
kansei/update-harness-YYYYMMDD-HHMMSS
```

If git working tree is dirty and `--allow-dirty` is not set, refuse apply.

---

## 13. MCP specification

### 13.1 MCP role

`Kansei` exposes the private local control plane via MCP so that Codex or other MCP clients can:

- list projects
- inspect status
- read dashboard resources
- read local knowledge resources
- call safe planning tools
- delegate to domain providers
- generate next-action plans

MCP is the standard interface. CLI remains the source of truth for state changes.

### 13.2 Transports

Supported transports:

```text
stdio:
  default for local Codex / local MCP clients

streamable-http:
  used for long-running server or SSH-tunneled remote access
```

HTTP mode default:

```text
host: 127.0.0.1
port: 18764
path: /mcp
```

### 13.3 Namespace

All Kansei MCP tools use `kansei.` prefix.

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

### 13.4 Tool safety classes

| class | examples | side effect | default |
|---|---|---:|---|
| read | `kansei.project.list`, `kansei.provider.status` | no | enabled |
| plan | `kansei.dashboard.plan_today`, `kansei.delegate.plan` | no persistent write | enabled |
| write | `kansei.dashboard.write_today` | writes local files | confirmation |
| remote-read | `kansei.provider.status` for SSH | remote read | enabled if provider connected |
| remote-write | future apply tools | remote write | disabled |
| destructive | delete/archive/cancel | irreversible | disabled |

### 13.5 MCP tools

#### `kansei.health`

Input:

```json
{}
```

Output:

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

Aggregates status across active projects. Read-only.

#### `kansei.dashboard.plan_today`

Creates a dashboard plan without writing file.

#### `kansei.dashboard.write_today`

Writes `dashboards/today.md`. Disabled by default in Codex config unless explicitly allowed.

#### `kansei.knowledge.search`

Searches local knowledge. Never reads outside Kansei root unless explicitly configured.

#### `kansei.delegate.plan`

Returns the safest delegation method for a project/task.

#### `kansei.delegate.codex`

Runs or proposes `codex exec --cd` delegation. By default this should be a plan tool unless `allow_execute=true`.

### 13.6 MCP Resources

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

### 13.7 MCP Prompts

```text
kansei.prompt.daily_planning
kansei.prompt.project_triage
kansei.prompt.hpc_failure_triage
kansei.prompt.paper_review
kansei.prompt.codex_delegation
kansei.prompt.feedback_routing
```

Prompt example:

```text
kansei.prompt.daily_planning(project_filter?, horizon?)
```

Returns a structured prompt that asks the agent to:

1. inspect A-priority projects
2. summarize blockers
3. propose at most 3 focus tasks
4. avoid apply/destructive actions
5. update dashboard only if explicitly requested

---

## 14. Provider contract

### 14.1 Provider classes

```text
kansei provider:
  self/status/dashboard/update

harnessops provider:
  feedback/eval/decision loop

runops provider:
  HPC run/project/slurm status and planning

paperops provider:
  paper/manuscript/claim/evidence/submission status and planning

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

Provider resolution order:

```text
1. providers.toml explicit provider
2. installed entry point, future
3. built-in provider
4. generic-code fallback
```

Potential entry point group:

```toml
[project.entry-points."kansei.providers"]
runops = "runops.kansei_provider:provider"
paperops = "paperops.kansei_provider:provider"
```

Initial implementation can avoid entry points and use built-in adapters.

---

## 15. Codex integration

### 15.1 AGENTS.md role

Kansei root `AGENTS.md` should instruct Codex to:

- treat Kansei as control plane
- avoid direct editing of target project files
- use `kansei` CLI or MCP tools
- delegate target-specific work to target project with proper cwd
- keep private knowledge private
- plan before apply

### 15.2 Target project delegation

For local project:

```bash
codex exec --cd ~/work/papers/lunar-cavity --profile paper \
  "AGENTS.mdに従ってclaim-evidence mapを点検して"
```

For SSH project:

```bash
ssh hpc-login 'cd /work/USER/cavity && codex exec --profile hpc-readonly "直近ログを確認して次の実験案を作って"'
```

### 15.3 Codex MCP server as optional provider

Advanced orchestration may run Codex itself as an MCP server:

```bash
codex mcp-server
```

`Kansei` v0.1 does not require this. MVP uses `codex exec --cd` and provider MCP tools.

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

## 16. HPC / SSH specification

### 16.1 Recommended model

HPC compute nodes do not host Kansei. The login node hosts runops MCP server if allowed by policy.

```text
Local workstation:
  Kansei + Codex + project registry

HPC login node Ubuntu:
  runops MCP server bound to 127.0.0.1

SSH tunnel:
  local 18765 -> hpc-login 127.0.0.1:18765
```

### 16.2 Login node runops MCP

On HPC login node:

```bash
runo mcp serve \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 18765
```

Local:

```bash
ssh -N -L 18765:127.0.0.1:18765 hpc-login
```

### 16.3 Safety policy

Default allowed:

```text
- queue status
- run list
- run inspect
- log read
- artifact list
- submit plan
```

Default disabled:

```text
- sbatch submit
- scancel
- delete
- archive
- remote file write
- login node long computation
```

### 16.4 Provider connection command

```bash
kansei provider connect runops_hpc --tunnel
```

This should either:

- start a foreground SSH tunnel, or
- print exact SSH tunnel command, depending on `--exec`.

Do not daemonize silently in v0.1.

---

## 17. Dashboard specification

### 17.1 `dashboards/today.md`

Purpose: daily operational decision surface.

Generated structure:

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

`kansei dashboard today` previews. `--write` writes.

### 17.2 Status cache

`kansei status` may cache provider results under `.kansei/state/provider-cache.json` with TTL.

Default TTL:

```text
local git: 30 sec
paperops: 60 sec
runops local: 60 sec
runops HPC queue: 30 sec
knowledge search: no cache
```

### 17.3 Dashboard as generated view

`dashboards/project-status.md` and `dashboards/provider-status.md` are generated views. `dashboards/today.md` is user-owned because it may contain human notes.

---

## 18. Knowledge layer

### 18.1 Philosophy

`knowledge/` is durable memory, not prompt stuffing.

### 18.2 Standard files

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

Default `kansei search` searches:

```text
knowledge/
runbooks/
prompts/
dashboards/
KANSEI.md
```

It does not search registered project roots unless explicitly requested.

### 18.4 Escalation policy

Raw note -> project note -> durable knowledge -> dashboard/runbook.

```text
raw observation
  -> knowledge/project-notes/*.md
    -> knowledge/decision-log.md
      -> runbooks/*.md or providers/domain docs
```

---

## 19. Security and privacy

### 19.1 Secrets

Never commit:

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

- Default bind host is `127.0.0.1`.
- Non-loopback bind requires `--allow-public-bind`.
- HTTP mode should support bearer token.
- SSH tunnel is preferred for remote access.

### 19.3 Private data boundaries

`Kansei` must distinguish:

```text
private local:
  actual projects, unpublished science, collaborators, local paths

sanitized feedback:
  generic failure, reproducible minimal context, no secrets

public package:
  templates, docs, schemas, dummy examples
```

### 19.4 Apply gates

Actions requiring explicit approval:

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

## 20. Implementation plan

### Phase 0: repository bootstrap

Deliverables:

```text
- pyproject.toml
- src/kansei/cli/main.py
- kansei version
- README.md
- SPEC.md
- tests smoke
```

Acceptance:

```bash
uv run kansei version
uv run pytest -q
```

### Phase 1: init / doctor / update-harness MVP

Deliverables:

```text
- kansei init
- standard template
- manifest/lock
- kansei doctor
- kansei update-harness dry-run
- kansei update-harness --apply
```

Acceptance:

```bash
uv run kansei init /tmp/kansei-demo --git --with-codex --with-mcp
cd /tmp/kansei-demo
uv run --directory /path/to/kansei kansei doctor
uv run --directory /path/to/kansei kansei update-harness
```

### Phase 2: project/provider registry

Deliverables:

```text
- projects.toml parser
- providers.toml parser
- project list/add/show/open
- provider list/doctor/connect plan
```

Acceptance:

```bash
kansei project add --id demo --name Demo --kind code --provider generic-code --location local --path .
kansei project list
kansei provider list
kansei doctor --check-projects --check-providers
```

### Phase 3: status/dashboard/search

Deliverables:

```text
- generic-code provider status
- project status
- workspace status
- dashboard today preview/write
- knowledge search via rg
```

Acceptance:

```bash
kansei status
kansei dashboard today
kansei dashboard today --write
kansei search "HPC"
```

### Phase 4: MCP server

Deliverables:

```text
- kansei mcp serve --transport stdio
- kansei.health
- kansei.project.list
- kansei.project.inspect
- kansei.workspace.status
- kansei.knowledge.search
- kansei.dashboard.plan_today
```

Acceptance:

```bash
npx -y @modelcontextprotocol/inspector kansei mcp serve --transport stdio
```

### Phase 5: provider integrations

Deliverables:

```text
- paperops provider adapter
- runops provider adapter
- harnessops provider adapter
- Codex delegation helper
- SSH tunnel helper
```

Acceptance:

```bash
kansei delegate paper-demo "statusを確認して次の執筆タスクを出して"
kansei provider connect runops_hpc --tunnel
```

### Phase 6: hardening

Deliverables:

```text
- JSON schema validation
- conflict handling
- backup
- migration framework
- CI
- PyPI trusted publishing
```

---

## 21. Minimal implementation skeleton

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

## 22. Testing specification

### 22.1 Unit tests

```text
- config parse
- project registry parse
- provider registry parse
- init creates layout
- doctor passes after init
- update-harness dry-run no-op on fresh instance
- update-harness refuses user-owned overwrite
- duplicate project id fails
- invalid provider fails
```

### 22.2 Smoke tests

```bash
uv run kansei --help
uv run kansei version
uv run kansei init .tmp/kansei --git --with-codex --with-mcp
cd .tmp/kansei
kansei doctor
kansei project list
kansei dashboard today
```

### 22.3 MCP smoke tests

```text
- start MCP server in stdio mode
- tools/list contains kansei.health
- call kansei.health
- read kansei://workspace/projects
```

### 22.4 Safety tests

```text
- update-harness does not overwrite projects.toml
- update-harness writes .new for edited managed file
- provider connect does not start background tunnel unless --exec
- dashboard preview does not write today.md without --write
```

---

## 23. Documentation deliverables

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

README should focus on:

```text
1. What Kansei is
2. Public package vs private instance
3. Quick start
4. Safety model
5. Integration with harnessops/runops/paperops
```

---

## 24. Acceptance criteria for v0.1

Kansei v0.1 is acceptable when:

```text
- `kansei init` creates a usable private local instance.
- `kansei doctor` passes immediately after init.
- `kansei update-harness` previews changes without writing by default.
- `kansei update-harness --apply` updates managed files but never overwrites user-owned files.
- `projects.toml` and `providers.toml` are validated.
- `kansei project list/add/show/open` works for local projects.
- `kansei status` works with generic-code provider.
- `kansei dashboard today` creates a useful planning view.
- `kansei search` searches local knowledge.
- `kansei mcp serve --transport stdio` exposes at least health, project list, project inspect, workspace status, knowledge search.
- `.codex/config.toml` can be generated from providers.toml.
- HPC provider can be configured as SSH-tunneled Streamable HTTP without exposing non-loopback ports by default.
```

---

## 25. Roadmap

### v0.1

- private local instance bootstrap
- safe update-harness
- registry
- generic status/dashboard
- MCP read-only tools

### v0.2

- paperops MCP integration
- runops MCP integration
- Codex delegate helpers
- SSH tunnel helper
- dashboard write flow

### v0.3

- HarnessOps feedback integration
- local friction capture
- sanitized upstream feedback export
- provider entry point system

### v0.4

- local SQLite FTS knowledge index
- persistent thread registry
- richer project status cache
- MCP prompts and resource templates

### v0.5

- codeops provider or generic-code expansion
- test/lint/release status aggregation
- PR/issue planning tools

---

## 26. References

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

