import { useState, type FormEvent, type KeyboardEvent } from 'react';
import { Search, Zap } from 'lucide-react';

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

const EXAMPLES = [
  'Top 5 customers by total revenue',
  'Monthly revenue trend for 2018',
  'Best performing ad campaigns by ROI',
  'Top 10 product categories by sales',
  'Average order value by state',
];

export default function QueryInput({ onSubmit, loading }: Props) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const q = value.trim();
    if (q && !loading) onSubmit(q);
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const q = value.trim();
      if (q && !loading) onSubmit(q);
    }
  };

  return (
    <div className="query-form">
      <form onSubmit={handleSubmit}>
        <div className="query-input-wrapper">
          <Search size={20} className="query-input-icon" />
          <textarea
            id="query-input"
            className="query-input"
            rows={1}
            placeholder="Ask anything… e.g. &quot;Top 5 customers by revenue&quot;"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
            style={{ resize: 'none', height: '28px', overflowY: 'hidden' }}
            onInput={(e) => {
              const t = e.currentTarget;
              t.style.height = 'auto';
              t.style.height = `${Math.min(t.scrollHeight, 120)}px`;
            }}
          />
          <button
            id="query-submit-btn"
            className="query-submit-btn"
            type="submit"
            disabled={loading || !value.trim()}
          >
            {loading ? (
              <><span className="spinner" /> Thinking…</>
            ) : (
              <><Zap size={15} /> Run Query</>
            )}
          </button>
        </div>
      </form>

      {/* Example chips */}
      <div>
        <p className="examples-label">Try an example</p>
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              className="example-chip"
              onClick={() => {
                setValue(ex);
                if (!loading) onSubmit(ex);
              }}
              disabled={loading}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
