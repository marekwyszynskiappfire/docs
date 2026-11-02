"""Trinity Usage Scorecard — baked spreadsheet target (interim evidence store)."""

from __future__ import annotations

SCORECARD_SPREADSHEET_ID = "123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo"

SCORECARD_SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    f"{SCORECARD_SPREADSHEET_ID}/edit"
)

# Product tab on the sheet ↔ run id prefix ↔ display product name
PRODUCT_SCORECARD_TABS: dict[str, dict[str, str]] = {
    "bigpicture": {
        "tab": "BigPicture",
        "run_prefix": "BP-",
        "product_label": "BigPicture",
    },
    "timetracker": {
        "tab": "TimeTracker",
        "run_prefix": "TT-",
        "product_label": "TimeTracker",
    },
    "jmwe": {
        "tab": "JMWE",
        "run_prefix": "JMWE-",
        "product_label": "JMWE",
    },
}

DEFAULT_PRODUCT_KEY = "bigpicture"

# BigPicture tab header (row 1) — append rows in this order
SCORECARD_ROW_HEADERS: tuple[str, ...] = (
    "Run ID",
    "QA User",
    "Product",
    "Use Case",
    "Epics Rev.",
    "Epics Appr.",
    "Epic Appr. %",
    "TC Gen.",
    "TC Appr.",
    "TC Rej.",
    "TC Appr. %",
    "Sent XRay",
    "TC Time (m)",
    "Total Time (m)",
    "Coverage Depth",
)


def product_tab_config(product_id: str | None) -> dict[str, str]:
    key = (product_id or "").strip().lower() or DEFAULT_PRODUCT_KEY
    if key in PRODUCT_SCORECARD_TABS:
        return PRODUCT_SCORECARD_TABS[key]
    # Unknown product configs still land on BigPicture tab with BP- ids
    return PRODUCT_SCORECARD_TABS[DEFAULT_PRODUCT_KEY]
