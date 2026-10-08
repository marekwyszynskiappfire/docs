#!/usr/bin/env python3
"""Select 5–10 golden TC keys for CR-GOLDEN-01: similarity-first, random fallback.

1. Rank all tests in `extraction.md` by thematic similarity to Epic keywords/theme text.
2. Take as many top matches as possible (cap 10, floor 5 when the corpus allows).
3. If fewer than 5 similar tests exist, fill the remainder with a random draw from the
   rest of the extract (seeded). If no keyword/theme signal at all, random sample 5–10.

Usage:
  python sample_golden_references.py \\
    --golden-root Trinity/creator/golden/v2/filter-17844-bigpicture-manual \\
    --keywords Security,Permission,Risk,Admin,UPS \\
    --seed ONE-228469-golden
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

ROW_RE = re.compile(r"\|\s*\d+\s*\|\s*(.+?)\s*\|\s*\w+\s*\|\s*\d+\s*\|\s*(TC-\d+)\s*\|")
MIN_SAMPLE = 5
MAX_SAMPLE = 10


def parse_extraction(extraction: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in extraction.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.search(line)
        if m:
            rows.append((m.group(1).strip(), m.group(2)))
    return rows


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def build_terms(keywords: list[str], theme_text: str) -> list[str]:
    terms: list[str] = []
    for kw in keywords:
        kw = kw.strip()
        if kw:
            terms.append(kw.lower())
    if theme_text:
        terms.extend(tokenize(theme_text))
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def score_title(title: str, terms: list[str]) -> tuple[int, list[str]]:
    t = title.lower()
    hits: list[str] = []
    score = 0
    for term in terms:
        if term in t:
            score += 2 if " " in term or len(term) > 8 else 1
            hits.append(term)
    return score, hits


def rank_rows(rows: list[tuple[str, str]], terms: list[str]) -> list[tuple[int, str, str, list[str]]]:
    ranked: list[tuple[int, str, str, list[str]]] = []
    for title, key in rows:
        score, hits = score_title(title, terms)
        ranked.append((score, key, title, hits))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked


def select_keys(
    ranked: list[tuple[int, str, str, list[str]]],
    seed: str,
    force_count: int,
    terms: list[str],
) -> tuple[list[str], str, int, int]:
    all_keys = [k for _, k, _, _ in ranked]
    similar = [x for x in ranked if x[0] > 0]

    if not terms:
        rng = random.Random(seed)
        n = force_count if MIN_SAMPLE <= force_count <= MAX_SAMPLE else rng.randint(MIN_SAMPLE, MAX_SAMPLE)
        n = min(n, len(all_keys))
        picked = sorted(rng.sample(all_keys, n))
        return picked, "random", 0, n

    if similar:
        # As many similar as possible, capped at MAX_SAMPLE, at least MIN_SAMPLE if corpus allows
        n_similar = len(similar)
        if n_similar >= MIN_SAMPLE:
            target = min(MAX_SAMPLE, n_similar)
        else:
            target = MIN_SAMPLE
        if force_count and MIN_SAMPLE <= force_count <= MAX_SAMPLE:
            target = min(force_count, MAX_SAMPLE)
            target = max(target, min(MIN_SAMPLE, len(all_keys)))

        chosen: list[str] = []
        for _score, key, _title, _hits in similar:
            if len(chosen) >= target:
                break
            chosen.append(key)
        similarity_count = len(chosen)

        random_fill = 0
        if len(chosen) < target:
            need = target - len(chosen)
            remainder = [k for k in all_keys if k not in chosen]
            rng = random.Random(seed or "golden-fill")
            if remainder:
                fill = rng.sample(remainder, min(need, len(remainder)))
                chosen.extend(fill)
                random_fill = len(fill)
        method = (
            "similarity"
            if random_fill == 0
            else "similarity_with_random_fill"
        )
        return sorted(chosen), method, similarity_count, random_fill

    # No title match — random fallback
    rng = random.Random(seed)
    n = force_count if MIN_SAMPLE <= force_count <= MAX_SAMPLE else rng.randint(MIN_SAMPLE, MAX_SAMPLE)
    n = min(n, len(all_keys))
    picked = sorted(rng.sample(all_keys, n))
    return picked, "random", 0, n


def main() -> None:
    p = argparse.ArgumentParser(description="Golden TC sample: similarity-first (CR-GOLDEN-01)")
    p.add_argument("--golden-root", required=True)
    p.add_argument("--keywords", default="", help="Comma-separated Epic theme keywords")
    p.add_argument("--theme-file", default="", help="Optional file with review excerpt for token overlap")
    p.add_argument("--seed", default="", help="Seed for random fill / random fallback")
    p.add_argument("--count", type=int, default=0, help="Force total sample size 5–10")
    args = p.parse_args()

    root = Path(args.golden_root)
    extraction = root / "extraction.md"
    if not extraction.is_file():
        raise SystemExit(f"Missing {extraction}")

    theme_text = ""
    if args.theme_file:
        theme_text = Path(args.theme_file).read_text(encoding="utf-8", errors="replace")

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    terms = build_terms(keywords, theme_text)
    rows = parse_extraction(extraction)
    if len(rows) < MIN_SAMPLE:
        raise SystemExit(f"Extract has only {len(rows)} tests; need at least {MIN_SAMPLE}.")

    ranked = rank_rows(rows, terms)
    chosen, method, sim_n, rand_n = select_keys(ranked, args.seed, args.count, terms)

    title_by_key = {k: t for t, k in rows}
    scores = {k: s for s, k, _, _ in ranked}

    out = {
        "method": method,
        "sample_count": len(chosen),
        "similarity_count": sim_n,
        "random_fill_count": rand_n,
        "candidate_pool_size": len(rows),
        "similarity_pool_size": sum(1 for s, _, _, _ in ranked if s > 0),
        "random_seed": args.seed or None,
        "keywords": keywords,
        "jira_keys": chosen,
        "similarity_scores": {k: scores.get(k, 0) for k in chosen},
        "titles": {k: title_by_key.get(k, "") for k in chosen},
        "rag_paths": [str(root / "rag" / "by-key" / f"{k}.json") for k in chosen],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
