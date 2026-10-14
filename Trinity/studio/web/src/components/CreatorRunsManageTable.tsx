import { Link } from "react-router-dom";
import RunListRowActions from "./RunListRowActions";
import SortableDataTable from "./SortableDataTable";

export type CreatorRunManageRow = {
  id: string;
  label: string;
  test_count?: number;
};

type Props = {
  runs: CreatorRunManageRow[];
  onChanged: () => void;
  onRowAction?: (runId: string) => void;
};

export default function CreatorRunsManageTable({ runs, onChanged, onRowAction }: Props) {
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
          render: (r) => <Link to={`/creator/${encodeURIComponent(r.id)}`}>{r.label}</Link>,
        },
        {
          id: "id",
          header: "Studio ID",
          getValue: (r) => r.id,
          render: (r) => <code className="run-id-cell">{r.id}</code>,
        },
        {
          id: "tests",
          header: "Tests",
          getValue: (r) => r.test_count ?? null,
          align: "right",
        },
        {
          id: "actions",
          header: "Actions",
          getValue: () => "",
          render: (r) => (
            <RunListRowActions
              kind="creator"
              runId={r.id}
              label={r.label}
              onChanged={() => {
                onChanged();
                onRowAction?.(r.id);
              }}
            />
          ),
        },
      ]}
    />
  );
}
