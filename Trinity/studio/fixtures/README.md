# Studio fixtures (committed)

Sanitized demo data for **offline** onboarding — no live Jira.

| Path | Use |
|------|-----|
| `demo-reviewer-run/` | Import into Studio as a fake portfolio run. Unit folder **`DEMO-4500`** matches the epic in `review-payload.json` (`scope.value`). Do **not** use real `ONE-*` keys for demo folders (e.g. `ONE-90001` is a Task in Appfire Jira, not an epic). |

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Same payload as `Trinity/reviewer/samples/demo-epic.payload.json`.
