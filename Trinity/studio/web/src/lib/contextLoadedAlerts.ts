export type ContextLoadedAlert = {
  pipeline_run_id: string;
  run_label: string;
  unit_id: string;
  jira_key: string;
  source: string;
  status: string;
  detail?: string;
};

export type ContextLoadedRunGroup = {
  pipeline_run_id: string;
  run_label: string;
  alerts: ContextLoadedAlert[];
  epicKeys: string[];
};

export function groupContextLoadedAlertsByRun(
  alerts: ContextLoadedAlert[]
): ContextLoadedRunGroup[] {
  const map = new Map<string, ContextLoadedRunGroup>();
  for (const a of alerts) {
    let g = map.get(a.pipeline_run_id);
    if (!g) {
      g = {
        pipeline_run_id: a.pipeline_run_id,
        run_label: a.run_label,
        alerts: [],
        epicKeys: [],
      };
      map.set(a.pipeline_run_id, g);
    }
    g.alerts.push(a);
    if (!g.epicKeys.includes(a.jira_key)) g.epicKeys.push(a.jira_key);
  }
  return [...map.values()].sort((a, b) => {
    if (b.alerts.length !== a.alerts.length) return b.alerts.length - a.alerts.length;
    return a.run_label.localeCompare(b.run_label, undefined, { sensitivity: "base" });
  });
}
