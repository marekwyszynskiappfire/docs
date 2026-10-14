import { Link } from "react-router-dom";
import RunListRowActions from "./RunListRowActions";
import SortableDataTable from "./SortableDataTable";

export type ReviewerRunRow = {
  id: string;
  label: string;
  unit_count?: number;
};

type Props = {
  runs: ReviewerRunRow[];
  onChanged: () => void;
};

export default function ReviewerRunsTable({ runs, onChanged }: Props) {
  return (
    <SortableDataTable
      rows={runs}
      rowKey={(r) => r.id}
      defaultSort={{ columnId: "label", dir: "asc" }}
      columns={[
        {
          id: "label",
          header: "Label",
          getValue: (r) => r.label,
          render: (r) => <Link to={`/runs/${r.id}`}>{r.label}</Link>,
        },
        {
          id: "id",
          header: "Studio ID",
          getValue: (r) => r.id,
          render: (r) => <code className="run-id-cell">{r.id}</code>,
        },
        {
          id: "units",
          header: "Units",
          getValue: (r) => r.unit_count ?? null,
          align: "right",
        },
        {
          id: "actions",
          header: "Actions",
          getValue: () => "",
          render: (r) => (
            <RunListRowActions kind="pipeline" runId={r.id} label={r.label} onChanged={onChanged} />
          ),
        },
      ]}
    />
  );
}
