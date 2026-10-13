# Trinity — versioning

How we version the **operator distribution** (skills + Studio + shared scripts) versus **JSON contracts** between stages.

---

## Distribution release (semver)

| Artifact | Location |
|----------|----------|
| **Canonical version** | [`VERSION`](VERSION) — one line, e.g. `0.2.0` |
| **Studio API** | `GET /api/health` → `trinity_version`, `studio_version` (same value) |
| **Telemetry** | `trinity_version` on each event envelope |
| **Override** | `TRINITY_VERSION` in env (CI, local experiments only) |
| **Git revision (optional)** | `TRINITY_GIT_REVISION` in env → health `git_revision` |

**Release tags (Git):** `trinity-v<VERSION>` on `main` when a pilot or internal release is cut, e.g. `trinity-v0.2.0`.

```bash
git tag -a "trinity-v$(cat Trinity/VERSION)" -m "Trinity $(cat Trinity/VERSION)"
git push docs "trinity-v$(cat Trinity/VERSION)"
```

**Not yet automated:** changelog file, GitHub Releases page, or npm publish (Studio web is `private`).

---

## What moves together on a release bump

1. Edit [`VERSION`](VERSION).
2. Align [`studio/web/package.json`](studio/web/package.json) `version` (Studio UI bundle; should match).
3. Run `cd Trinity/studio/web && npm install` if lockfile version metadata should match (optional).
4. Smoke: `pytest Trinity/studio/tests -q` and `GET /api/health`.
5. Tag `trinity-v*`.

Implementation reads version via [`studio/server/trinity_release.py`](studio/server/trinity_release.py).

---

## JSON / schema versions (independent)

These **do not** follow `Trinity/VERSION`. Bump only when the contract changes.

| Contract | Version field | Doc |
|----------|---------------|-----|
| Reviewer payload | `schema_version` / `payload_version` `1.1` | [`reviewer/scripts/render_report.py`](reviewer/scripts/render_report.py) |
| Test case draft | `schema_version` in JSON Schema | [`creator/schemas/TestCaseDraft.schema.json`](creator/schemas/TestCaseDraft.schema.json) |
| Importer operator config | `schema_version` `1.0` | [`importer/schemas/import-operator-config.schema.json`](importer/schemas/import-operator-config.schema.json) |
| Jira instances registry | `schema_version` `1.0` | [`importer/config/instances.json`](importer/config/instances.json) |
| Golden corpora index | `schema_version` `1.0` | Creator golden README |

Breaking schema changes require a migration note in [`CONTRACTS.md`](CONTRACTS.md) and coordinated skill/Studio updates.

---

## Mateusz / pilot evidence

Pilot scorecards and slides are **not** versioned with semver; track evidence per run (`telemetry/export`, Confluence). Criteria closure: [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md).
