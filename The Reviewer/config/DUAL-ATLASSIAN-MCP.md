# Dual Atlassian MCP setup (Cursor)

**Audience:** Platform / MCP administrator (P10) or a QA engineer (P1) doing one-time machine setup.  
**Not for:** PM/BA (P3), automation (P4), or day-to-day review operators who already have working MCP — skip this unless linked pages show as *Unavailable* with a cross-site reason in the report’s **Data sources** section.

**Why two connections:** The Reviewer routes Jira and Confluence reads by **host** (PRF-24). At Appfire, Jira often lives on `appfire.atlassian.net` while Confluence product docs live on `appfireteam.atlassian.net`. One login cannot cover both; the built-in Atlassian integration only holds one site at a time.

**What “done” looks like (checklist):**

- [ ] Two MCP server entries in `~/.cursor/mcp.json`, each using `mcp-remote` with a **different** local callback port.
- [ ] After reload, you completed **two separate** browser authorisations (one per entry).
- [ ] `getAccessibleAtlassianResources` on **each** entry returns the expected site URL (no swap).
- [ ] Optional: built-in Atlassian plugin disabled so the agent does not pick a third, single-site connection.
- [ ] A test scan shows cross-site Confluence links as **Analyzed**, not `linked page is on …; no connected Atlassian site covers it`.

---

## 1. Prerequisites

1. **Node.js** and npm (for `mcp-remote`).
2. Install the proxy once:

   ```bash
   npm install -g mcp-remote
   ```

   **Corporate network / silent hang:** if `npx mcp-remote` never starts, install with:

   ```bash
   npm_config_strict_ssl=false npm install -g mcp-remote
   ```

   Then use the full path from `which mcp-remote` in `mcp.json` (do not rely on `npx`).

3. **Security (P9):** OAuth tokens are stored locally by `mcp-remote`. Never commit `~/.cursor/mcp.json`, paste tokens into chat, or check secrets into this repo. This document contains **no** credentials.

---

## 2. Manual `mcp.json` template

Edit `~/.cursor/mcp.json`. **Merge** into existing `mcpServers` — do not remove unrelated servers (Figma, Xray, etc.).

Replace `MCP_REMOTE_PATH` with the output of `which mcp-remote` (examples: `/opt/homebrew/bin/mcp-remote`, `/usr/local/bin/mcp-remote`).

```json
{
  "mcpServers": {
    "atlassian_appfire": {
      "command": "MCP_REMOTE_PATH",
      "args": [
        "https://mcp.atlassian.com/v2/mcp",
        "30801",
        "--resource",
        "https://appfire.atlassian.net/"
      ]
    },
    "atlassian_appfireteam": {
      "command": "MCP_REMOTE_PATH",
      "args": [
        "https://mcp.atlassian.com/v2/mcp",
        "30802",
        "--resource",
        "https://appfireteam.atlassian.net/"
      ]
    }
  }
}
```

**Ports:** `30801` and `30802` must differ. If either port is in use, pick two free ports and use them consistently — changing ports later forces re-authorisation.

**Authorisation:**

1. Cursor → reload MCP servers (or restart Cursor).
2. Complete browser login for the **first** server; on the Atlassian consent screen, select the site that matches that entry (`appfire` vs `appfireteam`).
3. Repeat for the **second** server only after the first finished.

**If sites are swapped:** rename the top-level keys (`atlassian_appfire` ↔ `atlassian_appfireteam`) so names match reality. **Do not change `args`** unless you intend to re-login — logins are keyed on them.

**Verify:**

Ask the agent (or run yourself via MCP tools):

- On server `atlassian_appfire`: `getAccessibleAtlassianResources` → should list `appfire.atlassian.net`.
- On server `atlassian_appfireteam`: same → should list `appfireteam.atlassian.net`.

---

## 3. Product config (optional)

The Reviewer does **not** require extra fields in `config/<product>.json` for site routing — it discovers connected sites each run. Only add product-specific Jira field maps or policies there; see `config/default.json`.

---

## 4. Paste this prompt in Cursor (automated setup)

Copy everything inside the block below into a **new Cursor chat** (Agent mode). The agent should edit local MCP config and only interrupt you for auth and path confirmation.

```text
Set up dual Atlassian MCP for The Reviewer (two simultaneous Cloud sites).

Context:
- Skill doc: config/DUAL-ATLASSIAN-MCP.md in The Reviewer repo (read it first).
- Target sites: https://appfire.atlassian.net/ and https://appfireteam.atlassian.net/
- Use mcp-remote with separate local ports 30801 and 30802 unless those ports are taken (then pick two free ports and say which you used).
- Server keys: atlassian_appfire (appfire) and atlassian_appfireteam (appfireteam).

Do:
1. Check whether mcp-remote is installed (`which mcp-remote`). If missing, give me the exact install command (include npm_config_strict_ssl=false fallback for corporate TLS issues) and wait until I confirm install before continuing.
2. Read ~/.cursor/mcp.json and merge in the two servers without removing any existing mcpServers entries.
3. Use the full path to mcp-remote as "command", not npx.
4. Tell me to reload MCP in Cursor, then authorise each server in the browser one at a time, picking the matching site on each consent screen.
5. After I confirm both logins, call getAccessibleAtlassianResources on EACH server and show a small table: server key → site URL returned. If swapped, tell me to rename keys only (not args).
6. Suggest disabling Cursor’s built-in Atlassian plugin if it would duplicate one of these sites.
7. Do not modify The Reviewer config/*.json unless I ask. Do not commit or print secrets.

Ask me only:
- To confirm mcp-remote path if ambiguous.
- To confirm port changes if 30801/30802 are in use.
- To complete browser authentication when MCP reload prompts.
- Whether other Atlassian site URLs should be used instead of the two defaults.

Stop when the verification table shows both expected hosts.
```

---

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| Second server never prompts for login | Port collision | Use distinct ports in both `args` arrays. |
| Confluence still *Unavailable* with cross-site message | Only one site connected | Finish second auth; verify both resources. |
| Wrong site on a connection | Picked wrong org on consent | Re-auth that entry or swap key names only. |
| Agent uses wrong MCP | Built-in plugin + remotes | Disable plugin; call tools on named servers. |
| `mcp-remote` hangs on start | npm TLS / proxy | Global install with `npm_config_strict_ssl=false`; use binary path. |

---

## 6. Persona review (applied to this document)

| Persona | Need | Change made |
|--------|------|-------------|
| **P10** Platform / MCP admin | Clear verify step, port/auth rules | Checklist at top; verification table in prompt; troubleshooting table |
| **P1** QA engineer | Fast path, when to bother | “Done” checklist; link from MANUAL; optional product config clarified as unnecessary |
| **P3** PM / BA | Should not wade through MCP | Explicit “skip unless…” in audience line |
| **P9** Security | No secret leakage | Security subsection; prompt forbids printing/committing secrets |
| **P8** Release / delivery | Why Epics miss Confluence | Opening paragraph ties cross-site links to report quality |
| **P5** Skill maintainer | Single source of truth | MANUAL §10 points here instead of duplicating JSON |
| **P2** QA lead | No false promise of rollup | No dashboard wording; setup is per-machine only |

---

## 7. Related docs

- Operator manual: [`MANUAL.md`](../MANUAL.md) (§10 summary + link here).
- Site routing in runs: [`reference.md`](../reference.md) (`site_routing`), [`SKILL.md`](../SKILL.md) gather step 8.
- Decision: [`DECISIONS.md`](../DECISIONS.md) PRF-24.
