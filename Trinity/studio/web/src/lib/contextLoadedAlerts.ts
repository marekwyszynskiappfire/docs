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

export type ContextLoadedSortColumn = "jira_key" | "source" | "status" | "detail";
export type ContextLoadedSortDir = "asc" | "desc";

function sortValue(a: ContextLoadedAlert, col: ContextLoadedSortColumn): string {
  switch (col) {
    case "jira_key":
      return a.jira_key;
    case "source":
      return a.source;
    case "status":
      return a.status;
    case "detail":
      return a.detail ?? "";
  }
}

export function sortContextLoadedAlerts(
  alerts: ContextLoadedAlert[],
  col: ContextLoadedSortColumn,
  dir: ContextLoadedSortDir
): ContextLoadedAlert[] {
  const mult = dir === "asc" ? 1 : -1;
  return [...alerts].sort(
    (a, b) =>
      sortValue(a, col).localeCompare(sortValue(b, col), undefined, {
        sensitivity: "base",
        numeric: true,
      }) * mult
  );
}

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
