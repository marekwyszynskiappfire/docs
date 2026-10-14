# Cursor + MCP setup for Trinity

**Wiki:** [Trinity — Cursor and MCP setup](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3753312561/Trinity+Cursor+and+MCP+setup)

**Audience:** Every operator on [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md).  
**Deep dive (Appfire dual Cloud):** [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md).

Trinity **Reviewer gather** uses Atlassian MCP (Jira + Confluence). **Creator** and **Importer** use repo files and optional Jira REST from Studio `.env`; they do not require extra MCP servers beyond what you already configured.

**Stuck?** See [FAQ — MCP](FAQ.md#mcp-atlassian).

---

## 1. Decision tree

```text
Will you read Confluence on appfireteam.atlassian.net AND Jira on appfire.atlassian.net in the SAME Reviewer runs?
  YES → §3 Dual-site MCP (required)
  NO  → §2 Single-site MCP

Are you only learning on sandbox?
  YES → §2 with sandbox resource URL
```

| Profile | MCP servers | Studio `JIRA_BASE_URL` |
|---------|-------------|-------------------------|
| Sandbox learning | One: `appfire-sandbox` | `https://appfire-sandbox-774.atlassian.net` |
| Prod Jira only (no appfireteam Confluence) | One: `atlassian_appfire` | `https://appfire.atlassian.net` |
| Prod Jira + appfireteam Confluence | Two: `atlassian_appfire` + `atlassian_appfireteam` | `https://appfire.atlassian.net` |

---

## 2. Single-site MCP

### 2.1 Prerequisites

```bash
node --version    # 18+
npm install -g mcp-remote
which mcp-remote   # use this path in mcp.json — not npx (corporate networks)
```

If install hangs on TLS:

```bash
npm_config_strict_ssl=false npm install -g mcp-remote
```

### 2.2 `~/.cursor/mcp.json` (sandbox example)

Merge into existing `mcpServers`. Replace `MCP_REMOTE_PATH` with `which mcp-remote`.

```json
{
  "mcpServers": {
    "atlassian_sandbox": {
      "command": "MCP_REMOTE_PATH",
      "args": [
        "https://mcp.atlassian.com/v2/mcp",
        "30801",
        "--resource",
        "https://appfire-sandbox-774.atlassian.net/"
      ]
    }
  }
}
```

**Production single-site** — same pattern with resource `https://appfire.atlassian.net/` and server key `atlassian_appfire`.

### 2.3 Authorise

1. Cursor → **Settings → MCP** → reload servers (or restart Cursor).
2. Complete **one** browser OAuth; pick the site that matches `--resource`.
3. In Agent chat: ask to call `getAccessibleAtlassianResources` on your server key → URL must match resource.

### 2.4 Built-in Atlassian plugin

If the agent picks the wrong site, disable Cursor’s built-in Atlassian MCP plugin so only your named `mcp.json` servers remain.

---

## 3. Dual-site MCP (Appfire default for prod Epics)

Use when Epics link Confluence on **appfireteam** while Jira is on **appfire**.

Full checklist, ports `30801`/`30802`, verification table, and **paste-ready setup prompt** for Agent:

→ [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md)

**Done when:**

- `atlassian_appfire` → `appfire.atlassian.net`
- `atlassian_appfireteam` → `appfireteam.atlassian.net`
- Reviewer HTML **Data sources** shows cross-site Confluence as analyzed (not “no connected site”).

---

## 4. Cursor workspace

| Setting | Value |
|---------|--------|
| Open folder | Repo root (`DOCS`) |
| Skills | `./Trinity/scripts/install-trinity-skills.sh` |
| Agent mode | Required for portfolio gather and Importer execute |
| Rules | Optional repo [`.cursor/rules/`](../.cursor/rules/) if present |

---

## 5. Verify MCP + Reviewer without Studio

```bash
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json --strict
```

Writes HTML under `/tmp` or cwd per script help — proves Python toolchain. MCP is validated only via live gather or Agent tool calls.

---

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| No MCP tools in chat | Settings → MCP → enable server; reload |
| Wrong Jira site | Re-auth; check `--resource` URL trailing slash |
| Second dual server silent | Port clash — change both ports in `args` |
| `mcp-remote` not found | Use absolute path from `which mcp-remote` |
| Agent uses plugin not `mcp.json` | Disable built-in Atlassian MCP |

---

## 7. Security

- Never commit `~/.cursor/mcp.json`, `studio/.env`, or API tokens.
- Do not paste tokens into Agent chat.
- OAuth tokens live in `mcp-remote` local storage on your machine.
