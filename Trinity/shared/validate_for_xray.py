"""Shared Xray import validation (IQ-04). Used by Studio Importer plan and xray_graphql_import CLI."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from priority_score import validate_priority_policy

TRINITY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = TRINITY_ROOT / "creator" / "schemas" / "TestCaseDraft.schema.json"

REQUIRED_TEST_FIELDS = (
    "title",
    "linked_requirement_keys",
    "steps",
    "coverage_catalog_id",
    "execution_tier",
    "test_pattern",
    "role",
    "customer_impact",
    "test_data_required",
    "test_data_prerequisites",
)

_VALID_XRAY_TEST_TYPES = frozenset({"Manual", "Automated", "Generic", "Cucumber"})

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_SENSITIVE_URL_RE = re.compile(
    r"https?://[^\s\"']+",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _test_case_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_type_xray_coercion(raw: dict[str, Any]) -> str | None:
    """Human-readable note when import will change test_type for Xray (CQ-01)."""
    before = (raw.get("test_type") or "").strip()
    after = (enrich_test_for_xray_import(dict(raw)).get("test_type") or "Manual").strip()
    if not before:
        return None
    if before == after:
        return None
    return f"{before} → {after} (Xray import)"


def enrich_test_for_xray_import(test: dict[str, Any]) -> dict[str, Any]:
    out = dict(test)
    linked_ac = out.get("linked_ac_ids") or []
    if not out.get("coverage_catalog_id"):
        out["coverage_catalog_id"] = str(linked_ac[0]) if linked_ac else "TRINITY-IMPORT"
    test_type = (out.get("test_type") or "").strip()
    if test_type and test_type not in _VALID_XRAY_TEST_TYPES:
        out["test_type"] = "Manual"
    elif test_type == "Generic":
        out["test_type"] = "Manual"
    return out


def validate_test_legacy(test: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_TEST_FIELDS:
        if field not in test:
            errors.append(f"Missing required field: {field}")
    if not test.get("title", "").strip():
        errors.append("title is empty")
    if not test.get("linked_requirement_keys"):
        errors.append("linked_requirement_keys must be non-empty")
    steps = test.get("steps", [])
    if not steps:
        errors.append("steps must be non-empty")
    pattern = test.get("test_pattern")
    max_steps = 18 if pattern == "journey" else 13
    if len(steps) > max_steps:
        errors.append(f"step count {len(steps)} exceeds max {max_steps} for pattern {pattern}")
    for i, step in enumerate(steps, 1):
        if not step.get("step", "").strip():
            errors.append(f"step {i}: action is empty")
        if not step.get("expected_result", "").strip():
            errors.append(f"step {i}: expected_result is empty")
    errors.extend(validate_priority_policy(test))
    return errors


def validate_test_schema(test: dict[str, Any]) -> list[str]:
    if not SCHEMA_PATH.is_file():
        return []
    try:
        import jsonschema
    except ImportError:
        return []
    validator = jsonschema.Draft202012Validator(_test_case_schema())
    errors: list[str] = []
    for err in sorted(validator.iter_errors(test), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"schema: {path}: {err.message}")
    return errors[:15]


def validate_test(test: dict[str, Any]) -> list[str]:
    """Legacy Xray import rules + TestCaseDraft schema (IQ-04)."""
    enriched = enrich_test_for_xray_import(test)
    legacy = validate_test_legacy(enriched)
    if legacy:
        return legacy
    return validate_test_schema(enriched)


def deferrable_export_warnings(tests: list[dict[str, Any]]) -> list[str]:
    """IQ-08: warn when deferrable tests are in an export batch."""
    warnings: list[str] = []
    for test in tests:
        if not test.get("deferrable"):
            continue
        draft_id = test.get("draft_id", "?")
        rationale = test.get("deferrable_rationale") or "no rationale recorded"
        warnings.append(
            f"{draft_id} is marked deferrable ({rationale}) but is included in Xray export."
        )
    return warnings


def _scan_text_for_redaction(text: str, context: str, warnings: list[str]) -> None:
    for match in _EMAIL_RE.findall(text):
        warnings.append(f"{context}: possible email `{match}`")
    for url in _SENSITIVE_URL_RE.findall(text):
        lower = url.lower()
        if any(
            token in lower
            for token in ("localhost", "127.0.0.1", "internal", "staging", "sandbox")
        ):
            warnings.append(f"{context}: sensitive URL `{url[:80]}`")


def redaction_lint_payload(payload: dict[str, Any]) -> list[str]:
    """IQ-17: lint only — no auto-strip."""
    warnings: list[str] = []
    for test in payload.get("tests") or []:
        draft_id = test.get("draft_id", "?")
        blob = json.dumps(test, ensure_ascii=False)
        _scan_text_for_redaction(blob, f"test {draft_id}", warnings)
    return warnings[:25]


def export_preflight_warnings(payload: dict[str, Any]) -> list[str]:
    tests = payload.get("tests") or []
    out: list[str] = []
    out.extend(deferrable_export_warnings(tests))
    out.extend(redaction_lint_payload(payload))
    return out


_ISSUE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


def issue_key_or_none(value: Any) -> str | None:
    if isinstance(value, str) and _ISSUE_KEY_RE.match(value.strip()):
        return value.strip()
    return None


def declared_epic_keys(payload: dict[str, Any]) -> list[str]:
    """Epic keys this batch names. Child story keys in linked_requirement_keys are not epics."""
    found: list[str] = []

    def add(value: Any) -> None:
        key = issue_key_or_none(value)
        if key and key not in found:
            found.append(key)

    add(payload.get("epic_key"))
    scope = payload.get("scope")
    if isinstance(scope, dict):
        add(scope.get("jira_key"))
    add(payload.get("creator_run_id"))
    for test in payload.get("tests") or []:
        if isinstance(test, dict):
            add(test.get("epic_key"))
    return found


def one_epic_violation(payload: dict[str, Any]) -> str | None:
    """A write stays one Epic. Child stories under that Epic do not count as a second Epic."""
    keys = declared_epic_keys(payload)
    if len(keys) <= 1:
        return None
    return (
        "This batch names more than one Epic ("
        + ", ".join(keys)
        + "). Write one Epic at a time."
    )
