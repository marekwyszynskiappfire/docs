# Creator — Q4 backlog portfolio (filter 41907)

Reviewer run: `Trinity/reviewer/runs/q4-backlog`  
Config: `Trinity/reviewer/config/runs/q4-backlog.json`

## Where the payloads live (local)

After **trinity-creator** finishes, open:

```text
Trinity/creator/artifacts/q4-backlog/
```

Each epic has its own folder:

```text
Trinity/creator/artifacts/q4-backlog/ONE-{number}/suite-payload.json
```

**Studio:** **Creator → Import batch** — import **each** `suite-payload.json` separately (one Creator run per epic). There is **no** single combined payload. See [`../../artifacts/README.md`](../../artifacts/README.md).

**Skip or defer:** **ONE-381572** (`not_fit`, 0 tests in payload).

## Regenerate scripts

| Batch | Script |
|-------|--------|
| 1/3 | `Trinity/creator/scripts/_batch_q4_backlog_batch1_generate.py` |
| 2/3 | `Trinity/creator/scripts/generate_q4_backlog_batch2.py` |
| 3/3 | `Trinity/creator/scripts/build_q4_backlog_batch3.py` |

Legacy all-epic scaffold (superseded): `draft_q4_backlog_portfolio.py`.
