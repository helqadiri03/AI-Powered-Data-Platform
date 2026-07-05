import { useState } from 'react';
import { Code2, ChevronDown, Copy, Check } from 'lucide-react';

interface Props {
  sql: string;
  modelUsed: string;
}

// Very lightweight SQL keyword highlighter
function highlightSQL(sql: string): string {
  const keywords = [
    'SELECT','FROM','WHERE','JOIN','LEFT','RIGHT','INNER','OUTER','ON','AND','OR',
    'GROUP BY','ORDER BY','HAVING','LIMIT','WITH','AS','DISTINCT','COUNT','SUM',
    'AVG','MAX','MIN','CASE','WHEN','THEN','ELSE','END','IN','NOT','NULL',
    'IS','BETWEEN','LIKE','DESC','ASC','BY',
  ];
  let out = sql
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // Table names (UPPER_CASE words)
  out = out.replace(/\b([A-Z][A-Z0-9_]+)\b/g, (m) =>
    keywords.includes(m) ? `<span class="kw">${m}</span>` : `<span class="tb">${m}</span>`
  );

  // Numbers
  out = out.replace(/\b(\d+(\.\d+)?)\b/g, '<span class="st">$1</span>');

  // Strings
  out = out.replace(/'([^']*)'/g, "<span class=\"st\">'$1'</span>");

  return out;
}

export default function SQLViewer({ sql, modelUsed }: Props) {
  const [open, setOpen] = useState(true);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="sql-viewer">
      <div
        className="sql-viewer-header"
        onClick={() => setOpen((o) => !o)}
        role="button"
        aria-expanded={open}
        id="sql-viewer-toggle"
      >
        <div className="sql-viewer-title">
          <Code2 size={15} className="sql-viewer-title-icon" />
          Generated SQL
        </div>
        <div className="sql-viewer-meta">
          <span className="sql-model-badge">{modelUsed}</span>
          <ChevronDown
            size={16}
            className={`sql-viewer-toggle${open ? ' open' : ''}`}
          />
        </div>
      </div>

      {open && (
        <div className="sql-viewer-body animate-slide-down">
          <div className="sql-code-block">
            <button
              className="sql-copy-btn"
              onClick={(e) => { e.stopPropagation(); copy(); }}
              title="Copy SQL"
              id="sql-copy-btn"
            >
              {copied ? <><Check size={11} /> Copied</> : <><Copy size={11} /> Copy</>}
            </button>
            <span dangerouslySetInnerHTML={{ __html: highlightSQL(sql) }} />
          </div>
        </div>
      )}
    </div>
  );
}
