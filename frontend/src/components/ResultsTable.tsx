import { Table, Inbox } from 'lucide-react';

interface Props {
  columns: string[];
  rows: (string | number | null)[][];
  rowCount: number;
  loading?: boolean;
}

const NUMERIC_PATTERN = /^-?[\d,]+(\.\d+)?$/;

function isNumeric(val: string | number | null): boolean {
  if (val === null || val === '') return false;
  if (typeof val === 'number') return true;
  return NUMERIC_PATTERN.test(String(val));
}

function formatCell(val: string | number | null): string {
  if (val === null || val === undefined) return '—';
  if (typeof val === 'number') {
    return Number.isInteger(val)
      ? val.toLocaleString()
      : val.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(val);
}

export default function ResultsTable({ columns, rows, rowCount, loading }: Props) {
  if (loading) {
    return (
      <div className="results-section">
        <div className="results-table-wrapper">
          <div className="skeleton-rows">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="skeleton-row"
                style={{ opacity: 1 - i * 0.12, animationDelay: `${i * 80}ms` }}
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!columns.length) return null;

  return (
    <div className="results-section">
      <div className="results-header">
        <div className="results-title">
          <Table size={18} style={{ color: 'var(--cyan)' }} />
          Query Results
        </div>
        <span className="results-count-badge">{rowCount.toLocaleString()} rows</span>
      </div>

      <div className="results-table-wrapper">
        {rows.length === 0 ? (
          <div className="results-empty">
            <Inbox size={48} />
            <span>No rows returned for this query.</span>
          </div>
        ) : (
          <>
            <div className="results-table-scroll">
              <table className="results-table">
                <thead>
                  <tr>
                    {columns.map((col) => (
                      <th key={col}>{col.replace(/_/g, ' ')}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, ri) => (
                    <tr key={ri}>
                      {row.map((cell, ci) => (
                        <td
                          key={ci}
                          className={isNumeric(cell) ? 'num' : undefined}
                          title={String(cell ?? '')}
                        >
                          {formatCell(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="results-footer">
              <span>
                Showing <b>{rows.length.toLocaleString()}</b> of{' '}
                <b>{rowCount.toLocaleString()}</b> rows
              </span>
              <span>·</span>
              <span><b>{columns.length}</b> columns</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
