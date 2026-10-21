"""Deterministic coverage depth for Creator prompts.

The slider picks one of these profiles. It changes the requested journey
budget and scenario rules. It does not change model temperature.
"""

from __future__ import annotations

from typing import Any

DEFAULT_ID = "balanced"
STALE_PREFIX = "Coverage depth changed"

PROFILES: tuple[dict[str, Any], ...] = (
    {
        "id": "smoke",
        "label": "Smoke",
        "position": 0,
        "test_count_min": 1,
        "test_count_max": 2,
        "tiers": ("P0", "P1"),
        "summary": "One or two release-blocking happy paths. Confirms the main value can be delivered.",
        "include": (
            "The single most important happy-path journey.",
            "A second happy path only when the Epic has two distinct release-blocking outcomes.",
        ),
        "exclude": (
            "Permission and role variants.",
            "Validation failures, recovery, boundaries, and corner cases.",
        ),
    },
    {
        "id": "core",
        "label": "Core",
        "position": 1,
        "test_count_min": 3,
        "test_count_max": 5,
        "tiers": ("P0", "P1"),
        "summary": "Main journeys, the most important role or permission difference, and one material failure.",
        "include": (
            "Each primary user journey.",
            "The highest-risk role or permission difference.",
            "One material failure that the requirement already describes.",
        ),
        "exclude": (
            "Boundary matrices, rare combinations, and corner cases.",
        ),
    },
    {
        "id": "balanced",
        "label": "Balanced",
        "position": 2,
        "test_count_min": 5,
        "test_count_max": 8,
        "tiers": ("P0", "P1", "P2"),
        "summary": (
            "Main and alternate journeys, key roles and states, important validation, "
            "recovery, and integration behaviour."
        ),
        "include": (
            "Primary and important alternate journeys.",
            "Key roles, permissions, and state changes.",
            "Important validation, recovery, and integration behaviour stated by the requirement.",
        ),
        "exclude": (
            "Rare combinations and corner cases that are not in the requirement.",
        ),
    },
    {
        "id": "thorough",
        "label": "Thorough",
        "position": 3,
        "test_count_min": 8,
        "test_count_max": 12,
        "tiers": ("P0", "P1", "P2", "P3"),
        "summary": (
            "Balanced coverage plus meaningful boundaries, permission combinations, "
            "data variants, and integration failures."
        ),
        "include": (
            "Everything in Balanced.",
            "Boundary values and meaningful data variants.",
            "Permission combinations and state transitions.",
            "Integration failures and recovery paths described by the requirement.",
        ),
        "exclude": (
            "Speculative corner cases with no requirement evidence.",
        ),
    },
    {
        "id": "edge",
        "label": "Edge",
        "position": 4,
        "test_count_min": 12,
        "test_count_max": 20,
        "tiers": ("P0", "P1", "P2", "P3"),
        "summary": (
            "Thorough coverage plus evidence-backed corner cases: empty, maximum, and malformed data, "
            "rare combinations, concurrency, retries, outages, and rollback."
        ),
        "include": (
            "Everything in Thorough.",
            "Empty, maximum, and malformed data where the requirement implies a result.",
            "Rare role, state, or ordering combinations that the requirement allows.",
            "Concurrency, idempotency, retries, outages, and rollback when the requirement mentions them.",
        ),
        "exclude": (
            "Behaviour the requirement does not support. List those areas in coverage_profile.omitted.",
        ),
    },
)

_BY_ID = {profile["id"]: profile for profile in PROFILES}


def profile_by_id(profile_id: str) -> dict[str, Any]:
    found = _BY_ID.get(profile_id)
    if found is None:
        known = ", ".join(profile["id"] for profile in PROFILES)
        raise ValueError(f"Unknown coverage depth '{profile_id}'. Use one of: {known}.")
    return found


def coerce_profile_id(value: str | None) -> str:
    if value in _BY_ID:
        return str(value)
    return DEFAULT_ID


def resolve_profile_id(override: str | None, portfolio: str | None) -> str:
    if override:
        return profile_by_id(override)["id"]
    return coerce_profile_id(portfolio)


def resolve_for_unit(conn: Any, unit: Any) -> dict[str, Any]:
    override = unit["coverage_profile"]
    portfolio = None
    if not override:
        run = conn.execute(
            "SELECT coverage_profile FROM pipeline_run WHERE id = ?",
            (unit["pipeline_run_id"],),
        ).fetchone()
        portfolio = run["coverage_profile"] if run else None
    return profile_by_id(resolve_profile_id(override, portfolio))


def public_profile(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": profile["id"],
        "label": profile["label"],
        "position": profile["position"],
        "test_count_min": profile["test_count_min"],
        "test_count_max": profile["test_count_max"],
        "summary": profile["summary"],
    }


def public_profiles() -> list[dict[str, Any]]:
    return [public_profile(profile) for profile in PROFILES]


def is_coverage_stale(error: str | None) -> bool:
    return bool(error and error.startswith(STALE_PREFIX))


def stale_message(profile: dict[str, Any]) -> str:
    return (
        f"{STALE_PREFIX} to {profile['label']} "
        f"({profile['test_count_min']}–{profile['test_count_max']} journeys). "
        "Copy the new Creator prompt and replace the suite."
    )


def prompt_section(profile: dict[str, Any]) -> str:
    include = "\n".join(f"- {line}" for line in profile["include"])
    exclude = "\n".join(f"- {line}" for line in profile["exclude"])
    tiers = ", ".join(profile["tiers"])
    low = profile["test_count_min"]
    high = profile["test_count_max"]
    profile_id = profile["id"]
    return f"""### Coverage depth

This profile is a coverage budget. It is not a sampling temperature.

| Field | Value |
|-------|-------|
| **coverage_profile** | `{profile_id}` ({profile["label"]}) |
| **Target journeys** | {low}–{high} |
| **Priority tiers to include** | {tiers} |

{profile["summary"]}

Include:

{include}

Leave out:

{exclude}

Rules:

- Write only journeys the requirement supports. List unsupported areas in `coverage_profile.omitted`.
- `actual_count` may be below {low}. It must not exceed {high}.
- Keep each journey within the usual step limit. This profile adds journeys, not longer steps.
- Score each test on its own. A corner case can stay P2 or P3.
- Expected results come from the requirement. Unspecified behaviour belongs in `omitted`.
- `suite_mode` stays `release_slice_e2e` and `test_pattern` stays `journey`.
- Write this object on `suite-payload.json` and set `actual_count` to the number of tests:

```json
"coverage_profile": {{
  "id": "{profile_id}",
  "test_count_min": {low},
  "test_count_max": {high},
  "actual_count": 0,
  "omitted": []
}}
```
"""
