# MCP

Kansei は `kansei.` prefix の read-only / plan-oriented MCP tool を公開します。
状態変更の正本は引き続き CLI です。

## 起動

ローカルの Codex client では通常 stdio を使います。

```powershell
kansei mcp serve --transport stdio
```

HTTP mode は local use または SSH tunnel 経由の利用に使えます。

```powershell
kansei mcp serve --transport streamable-http --host 127.0.0.1 --port 18764
```

既定の host は loopback です。別途 access-control plan が無い限り、HTTP MCP を
public interface に公開しないでください。

## Codex config

生成される config を preview します。

```powershell
kansei mcp config
```

`providers.toml` から `.codex/config.toml` を書きます。

```powershell
kansei mcp config --write --force
```

生成される MCP surface を確認します。

```powershell
kansei mcp inspect
```

## MCP tool

- `kansei.health`: workspace root、version、基本 warning。
- `kansei.project.list`: 任意の `active`, `kind`, `priority` filter 付き project summary。
- `kansei.project.inspect`: 1 つの project の registry entry と safety policy。
- `kansei.workspace.status`: project/provider status の集約。
- `kansei.knowledge.search`: local knowledge をスコープ指定で検索。
- `kansei.dashboard.plan_today`: file を書かずに dashboard Markdown plan を返す。

## MCP resource

- `kansei://workspace/projects`
- `kansei://workspace/providers`

## 安全性

現在の MCP tool は job submit、file delete、manuscript rewrite、remote state write を
行いません。dashboard planning は Markdown を返し、`writes_files: false` です。
