import { ReactNode, useMemo, useState } from "react";

export type SortableColumn<T> = {
  id: string;
  header: string;
  getValue: (row: T) => string | number | null | undefined;
  align?: "left" | "right";
  render?: (row: T) => ReactNode;
  headerClassName?: string;
  cellClassName?: string;
  /** Used for default sort only; not shown in the table */
  hidden?: boolean;
};

type SortDir = "asc" | "desc";

type Props<T> = {
  rows: T[];
  columns: SortableColumn<T>[];
  rowKey: (row: T, index: number) => string;
  className?: string;
  defaultSort?: { columnId: string; dir: SortDir };
  rowClassName?: (row: T) => string | undefined;
};

function compareValues(a: string | number | null | undefined, b: string | number | null | undefined): number {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
}

export default function SortableDataTable<T>({
  rows,
  columns,
  rowKey,
  className,
  defaultSort,
  rowClassName,
}: Props<T>) {
  const [sort, setSort] = useState<{ columnId: string; dir: SortDir } | null>(
    defaultSort ?? null
  );

  const visibleColumns = useMemo(() => columns.filter((c) => !c.hidden), [columns]);

  const sorted = useMemo(() => {
    if (!sort) return rows;
    const col = columns.find((c) => c.id === sort.columnId);
    if (!col) return rows;
    const copy = [...rows];
    copy.sort((ra, rb) => {
      const cmp = compareValues(col.getValue(ra), col.getValue(rb));
      return sort.dir === "asc" ? cmp : -cmp;
    });
    return copy;
  }, [rows, columns, sort]);

  const onHeaderClick = (columnId: string) => {
    setSort((prev) => {
      if (prev?.columnId === columnId) {
        return { columnId, dir: prev.dir === "asc" ? "desc" : "asc" };
      }
      return { columnId, dir: "asc" };
    });
  };

  return (
    <table className={className ?? "data"}>
      <thead>
        <tr>
          {visibleColumns.map((col) => (
            <th
              key={col.id}
              className={col.headerClassName}
              style={{ textAlign: col.align ?? "left" }}
            >
              <button
                type="button"
                className="sortable-th"
                onClick={() => onHeaderClick(col.id)}
                aria-sort={
                  sort?.columnId === col.id
                    ? sort.dir === "asc"
                      ? "ascending"
                      : "descending"
                    : "none"
                }
              >
                {col.header}
                {sort?.columnId === col.id && (
                  <span className="sort-indicator">{sort.dir === "asc" ? " ▲" : " ▼"}</span>
                )}
              </button>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((row, index) => (
          <tr key={rowKey(row, index)} className={rowClassName?.(row)}>
            {visibleColumns.map((col) => (
              <td
                key={col.id}
                className={col.cellClassName}
                style={{ textAlign: col.align ?? "left" }}
              >
                {col.render ? col.render(row) : (col.getValue(row) ?? "—")}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
