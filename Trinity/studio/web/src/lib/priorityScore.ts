/** CR-SCORE-01 — keep in sync with Trinity/shared/priority_score.py */

export const TIER_PRIORITY: Record<string, string> = {
  P0: "Highest",
  P1: "High",
  P2: "Medium",
  P3: "Low",
};

export const DEFAULT_FACTORS: Record<
  string,
  {
    customer_harm: number;
    likelihood: number;
    coverage_criticality: number;
    automation_value: number;
  }
> = {
  P0: { customer_harm: 5, likelihood: 4, coverage_criticality: 5, automation_value: 3 },
  P1: { customer_harm: 4, likelihood: 3, coverage_criticality: 4, automation_value: 3 },
  P2: { customer_harm: 3, likelihood: 3, coverage_criticality: 2, automation_value: 2 },
  P3: { customer_harm: 2, likelihood: 2, coverage_criticality: 1, automation_value: 1 },
};

export type PriorityScore = {
  customer_harm: number;
  likelihood: number;
  coverage_criticality: number;
  automation_value: number;
  total: number;
  derived_tier: string;
  rationale: string;
};

function clamp(n: number): number {
  return Math.max(1, Math.min(5, Math.round(Number.isFinite(n) ? n : 3)));
}

export function tierFromTotal(total: number): string {
  if (total >= 13) return "P0";
  if (total >= 10) return "P1";
  if (total >= 7) return "P2";
  return "P3";
}

export function buildPriorityScore(partial: Partial<PriorityScore>, fallbackTier = "P1"): PriorityScore {
  const defaults = DEFAULT_FACTORS[fallbackTier] ?? DEFAULT_FACTORS.P1;
  const customer_harm = clamp(Number(partial.customer_harm ?? defaults.customer_harm));
  const likelihood = clamp(Number(partial.likelihood ?? defaults.likelihood));
  const coverage_criticality = clamp(
    Number(partial.coverage_criticality ?? defaults.coverage_criticality)
  );
  const automation_value = clamp(Number(partial.automation_value ?? defaults.automation_value));
  const total = customer_harm + likelihood + coverage_criticality;
  return {
    customer_harm,
    likelihood,
    coverage_criticality,
    automation_value,
    total,
    derived_tier: tierFromTotal(total),
    rationale: String(partial.rationale ?? "").trim(),
  };
}

export function scoreFromTier(tier: string, rationale = ""): PriorityScore {
  const defaults = DEFAULT_FACTORS[tier] ?? DEFAULT_FACTORS.P1;
  return buildPriorityScore({ ...defaults, rationale }, tier);
}
