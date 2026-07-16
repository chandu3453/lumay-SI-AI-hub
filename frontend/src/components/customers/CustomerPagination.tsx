"use client";

type CustomerPaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
};

export function CustomerPagination({ page, pageSize, total, onPageChange }: CustomerPaginationProps) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-border bg-muted/20">
      <p className="text-sm text-muted-foreground">Showing {start}–{end} of {total}</p>
      <div className="flex items-center gap-2">
        <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
          className="px-3 py-1.5 text-sm rounded-lg border border-border bg-white dark:bg-card hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors">Previous</button>
        <div className="flex items-center gap-1">
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
            let pn: number;
            if (totalPages <= 5) pn = i + 1;
            else if (page <= 3) pn = i + 1;
            else if (page >= totalPages - 2) pn = totalPages - 4 + i;
            else pn = page - 2 + i;
            return (
              <button key={pn} onClick={() => onPageChange(pn)}
                className={`px-2.5 py-1.5 text-sm rounded-lg transition-colors ${page === pn ? "bg-primary text-primary-foreground" : "hover:bg-accent text-muted-foreground"}`}>{pn}</button>
            );
          })}
        </div>
        <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
          className="px-3 py-1.5 text-sm rounded-lg border border-border bg-white dark:bg-card hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors">Next</button>
      </div>
    </div>
  );
}