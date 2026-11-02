# Golden library

Phase 1 copies `Input/Marek/_shared/golden/v1/` here (`style-rules.md`, examples). Product teams pick a **v2 corpus** via `config/*.json` → `golden_root` (see [`registry.json`](registry.json)).

**Not in git:** Xray extract trees under `v2/` (and `v1/examples/`). Only this README, [`registry.json`](registry.json), [`v1/style-rules.md`](v1/style-rules.md), and [`v2/README.md`](v2/README.md) are tracked. Restore corpora locally:

| Corpus | How to obtain |
|--------|----------------|
| `neutral-manual-journeys` | `python3 Trinity/creator/scripts/build_neutral_golden_corpus.py` from repo root |
| `filter-17844-bigpicture-manual` | QA lead export / internal artifact; paths in `registry.json` |

**IQ-12:** `v2/neutral-manual-journeys/` — product-agnostic journeys for non-TC Importer targets; rebuild with `scripts/build_neutral_golden_corpus.py`.
