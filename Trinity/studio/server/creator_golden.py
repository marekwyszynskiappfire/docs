"""Golden corpus registry + product config resolution (IQ-12)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = REPO_ROOT / "Trinity" / "creator" / "config"
REGISTRY_PATH = REPO_ROOT / "Trinity" / "creator" / "golden" / "registry.json"


def _read_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        return {"schema_version": "1.0", "corpora": []}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _corpus_test_count(corpus_path: Path) -> int | None:
    manifest = corpus_path / "manifest.json"
    if manifest.is_file():
        try:
            return int(json.loads(manifest.read_text(encoding="utf-8")).get("test_count") or 0)
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    extraction = corpus_path / "extraction.json"
    if extraction.is_file():
        try:
            data = json.loads(extraction.read_text(encoding="utf-8"))
            return int(data.get("test_count") or len(data.get("tests") or []))
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
    return None


def _resolve_repo_path(rel: str) -> Path:
    return (REPO_ROOT / rel).resolve()


def list_golden_corpora() -> list[dict[str, Any]]:
    reg = _read_registry()
    out: list[dict[str, Any]] = []
    for item in reg.get("corpora") or []:
        rel = str(item.get("path") or "")
        path = _resolve_repo_path(rel)
        row = dict(item)
        row["path_exists"] = path.is_dir() or path.is_file()
        row["resolved_path"] = rel
        if row.get("test_count") is None:
            count = _corpus_test_count(path) if path.is_dir() else None
            if count is not None:
                row["test_count"] = count
        out.append(row)
    return out


def corpus_by_id(corpus_id: str) -> dict[str, Any] | None:
    for c in list_golden_corpora():
        if c.get("id") == corpus_id:
            return c
    return None


def list_creator_products() -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    for path in sorted(CONFIG_DIR.glob("*.json")):
        if path.name == "README.md":
            continue
        cfg = json.loads(path.read_text(encoding="utf-8"))
        product = cfg.get("product") or {}
        pid = product.get("id") or path.stem
        golden_root = cfg.get("golden_root") or ""
        corpus_id = cfg.get("golden_corpus_id")
        corpus = corpus_by_id(corpus_id) if corpus_id else None
        imp = cfg.get("importer") or {}
        products.append(
            {
                "product_id": pid,
                "name": product.get("name") or pid,
                "config_file": f"Trinity/creator/config/{path.name}",
                "golden_root": golden_root,
                "golden_corpus_id": corpus_id,
                "golden_title": (corpus or {}).get("title"),
                "golden_test_count": (corpus or {}).get("test_count"),
                "reference_jira_project": (corpus or {}).get("reference_jira_project"),
                "importer_default_project_key": imp.get("default_jira_project_key"),
                "importer_default_folder_template": imp.get("default_folder_template"),
            }
        )
    return products


def golden_info_for_product(product_id: str | None) -> dict[str, Any]:
    from creator_importer_config import load_creator_product_config

    cfg = load_creator_product_config(product_id)
    pid = cfg.get("product", {}).get("id") or product_id or "default"
    golden_root = cfg.get("golden_root") or ""
    corpus_id = cfg.get("golden_corpus_id")
    corpus = corpus_by_id(corpus_id) if corpus_id else None
    path = _resolve_repo_path(golden_root) if golden_root else None
    return {
        "product_id": pid,
        "golden_root": golden_root,
        "golden_corpus_id": corpus_id,
        "corpus": corpus,
        "golden_root_exists": bool(path and path.exists()),
        "sampler_ready": bool(path and (path / "extraction.md").is_file()),
    }
