"""Release-gate scoring for Creator test drafts (CR-SCORE-01).

``priority_score.total`` = customer_harm + likelihood + coverage_criticality (3–15).
``automation_value`` ranks automation backlog only; it does not change the gate tier.

Golden similarity scores are unrelated — they only pick writing references.
"""

from __future__ import annotations

from typing import Any

TIER_PRIORITY: dict[str, str] = {
    "P0": "Highest",
    "P1": "High",
    "P2": "Medium",
    "P3": "Low",
}

# Mid-band defaults when an author sets a tier before scoring factors.
DEFAULT_FACTORS: dict[str, dict[str, int]] = {
    "P0": {"customer_harm": 5, "likelihood": 4, "coverage_criticality": 5, "automation_value": 3},
    "P1": {"customer_harm": 4, "likelihood": 3, "coverage_criticality": 4, "automation_value": 3},
    "P2": {"customer_harm": 3, "likelihood": 3, "coverage_criticality": 2, "automation_value": 2},
    "P3": {"customer_harm": 2, "likelihood": 2, "coverage_criticality": 1, "automation_value": 1},
}

FACTOR_KEYS = (
    "customer_harm",
    "likelihood",
    "coverage_criticality",
    "automation_value",
)

GATE_FACTOR_KEYS = ("customer_harm", "likelihood", "coverage_criticality")


def clamp_factor(value: Any, default: int = 3) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(5, n))


def compute_total(harm: int, likelihood: int, coverage: int) -> int:
    return clamp_factor(harm) + clamp_factor(likelihood) + clamp_factor(coverage)


def tier_from_total(total: int) -> str:
    if total >= 13:
        return "P0"
    if total >= 10:
        return "P1"
    if total >= 7:
        return "P2"
    return "P3"


def priority_for_tier(tier: str) -> str:
    return TIER_PRIORITY.get(tier, "Medium")


def build_priority_score(
    *,
    customer_harm: int,
    likelihood: int,
    coverage_criticality: int,
    automation_value: int = 3,
    rationale: str = "",
) -> dict[str, Any]:
    harm = clamp_factor(customer_harm)
    like = clamp_factor(likelihood)
    cov = clamp_factor(coverage_criticality)
    auto = clamp_factor(automation_value)
    total = compute_total(harm, like, cov)
    out: dict[str, Any] = {
        "customer_harm": harm,
        "likelihood": like,
        "coverage_criticality": cov,
        "automation_value": auto,
        "total": total,
        "derived_tier": tier_from_total(total),
    }
    if rationale.strip():
        out["rationale"] = rationale.strip()
    return out


def apply_priority_fields(test: dict[str, Any]) -> dict[str, Any]:
    """Fill ``priority_score``, ``execution_tier``, ``priority``, and P3 deferrable flags."""
    out = dict(test)
    existing = out.get("priority_score") if isinstance(out.get("priority_score"), dict) else {}
    tier = str(out.get("execution_tier") or "").strip()
    defaults = DEFAULT_FACTORS.get(tier, DEFAULT_FACTORS["P1"])

    if any(existing.get(k) is not None for k in GATE_FACTOR_KEYS):
        score = build_priority_score(
            customer_harm=int(existing.get("customer_harm") or defaults["customer_harm"]),
            likelihood=int(existing.get("likelihood") or defaults["likelihood"]),
            coverage_criticality=int(
                existing.get("coverage_criticality") or defaults["coverage_criticality"]
            ),
            automation_value=int(existing.get("automation_value") or defaults["automation_value"]),
            rationale=str(existing.get("rationale") or ""),
        )
        out["execution_tier"] = score["derived_tier"]
    else:
        if tier not in TIER_PRIORITY:
            tier = "P1"
        defaults = DEFAULT_FACTORS[tier]
        score = build_priority_score(
            customer_harm=defaults["customer_harm"],
            likelihood=defaults["likelihood"],
            coverage_criticality=defaults["coverage_criticality"],
            automation_value=defaults["automation_value"],
            rationale=str(existing.get("rationale") or ""),
        )
        out["execution_tier"] = tier
    if not str(score.get("rationale") or "").strip():
        impact = str(out.get("customer_impact") or "").strip()
        score["rationale"] = (
            impact[:240]
            if impact
            else f"{out['execution_tier']} scored from default mid-band factors for this tier."
        )

    out["priority_score"] = score
    out["priority"] = priority_for_tier(out["execution_tier"])
    if out["execution_tier"] == "P3":
        out["deferrable"] = True
        if not str(out.get("deferrable_rationale") or "").strip():
            out["deferrable_rationale"] = (
                "P3 / score ≤ 6: skip under time pressure after P0–P2 journeys pass."
            )
    elif out["execution_tier"] in ("P0", "P1"):
        out["deferrable"] = False
        out.pop("deferrable_rationale", None)
    else:
        out["deferrable"] = bool(out.get("deferrable"))
        if not out["deferrable"]:
            out.pop("deferrable_rationale", None)
    return out


def validate_priority_policy(test: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    draft = test.get("draft_id") or test.get("title") or "?"
    prefix = f"{draft}: "

    tier = str(test.get("execution_tier") or "").strip()
    if tier not in TIER_PRIORITY:
        errors.append(f"{prefix}execution_tier must be one of {', '.join(TIER_PRIORITY)}")
        return errors

    expected_priority = priority_for_tier(tier)
    priority = test.get("priority")
    if not priority:
        errors.append(f"{prefix}priority is required (must be {expected_priority} for {tier})")
    elif priority != expected_priority:
        errors.append(
            f"{prefix}priority {priority!r} does not match {tier} "
            f"(canonical mapping is {expected_priority})"
        )

    score = test.get("priority_score")
    if not isinstance(score, dict):
        errors.append(f"{prefix}priority_score object is required")
        return errors

    for key in FACTOR_KEYS:
        raw = score.get(key)
        if raw is None:
            errors.append(f"{prefix}priority_score.{key} is required (1–5)")
            continue
        try:
            n = int(raw)
        except (TypeError, ValueError):
            errors.append(f"{prefix}priority_score.{key} must be an integer 1–5")
            continue
        if n < 1 or n > 5:
            errors.append(f"{prefix}priority_score.{key} must be 1–5, got {n}")

    try:
        harm = int(score.get("customer_harm"))
        like = int(score.get("likelihood"))
        cov = int(score.get("coverage_criticality"))
    except (TypeError, ValueError):
        return errors

    total = compute_total(harm, like, cov)
    recorded = score.get("total")
    if recorded is None:
        errors.append(f"{prefix}priority_score.total is required")
    else:
        try:
            if int(recorded) != total:
                errors.append(
                    f"{prefix}priority_score.total is {recorded}, expected {total} "
                    "(harm + likelihood + coverage_criticality)"
                )
        except (TypeError, ValueError):
            errors.append(f"{prefix}priority_score.total must be an integer")

    derived = tier_from_total(total)
    if derived != tier:
        errors.append(
            f"{prefix}execution_tier {tier} does not match score total {total} "
            f"(maps to {derived}: P0=13–15, P1=10–12, P2=7–9, P3=3–6)"
        )

    derived_on_score = score.get("derived_tier")
    if derived_on_score is not None and derived_on_score != derived:
        errors.append(
            f"{prefix}priority_score.derived_tier is {derived_on_score!r}, expected {derived}"
        )

    if not str(score.get("rationale") or "").strip():
        errors.append(f"{prefix}priority_score.rationale is required")

    deferrable = bool(test.get("deferrable"))
    if tier == "P3":
        if not deferrable:
            errors.append(f"{prefix}P3 tests must set deferrable=true")
        if not str(test.get("deferrable_rationale") or "").strip():
            errors.append(f"{prefix}P3 tests require deferrable_rationale")
    if tier in ("P0", "P1") and deferrable:
        errors.append(f"{prefix}{tier} tests must not be deferrable")

    return errors


def build_execution_plan(tests: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {
        "P0": "p0_critical",
        "P1": "p1_mandatory",
        "P2": "p2_medium",
        "P3": "p3_deferrable",
    }
    plan: dict[str, Any] = {}
    for tier, key in buckets.items():
        ids = [
            str(t.get("draft_id") or t.get("title") or "?")
            for t in tests
            if t.get("execution_tier") == tier
        ]
        plan[key] = {"count": len(ids), "tests": ids}
    p0 = plan["p0_critical"]["count"]
    p1 = plan["p1_mandatory"]["count"]
    plan["minimum_release_gate"] = (
        "Run all P0 and P1 journeys before release."
        if (p0 + p1)
        else "No P0/P1 journeys — confirm Epic coverage before gating."
    )
    plan["time_boxed_release"] = "Skip P3; run P2 only if time remains after P0–P1."
    return plan
