import { useState } from 'react';
import './index.css';
import './App.css';

import { runQuery, type QueryResponse } from './services/api';
import QueryInput from './components/QueryInput';
import SQLViewer from './components/SQLViewer';
import ResultsTable from './components/ResultsTable';

import { AlertTriangle, Database, Cpu, ArrowRight, Sparkles } from 'lucide-react';

type PipelineStage =
  | 'idle'
  | 'generating'
  | 'validating'
  | 'executing'
  | 'done';

const PIPELINE_STEPS: { key: PipelineStage | string; label: string }[] = [
  { key: 'react',      label: 'React' },
  { key: 'generating',  label: 'Text-to-SQL Agent' },
  { key: 'validating',  label: 'SQL Validation' },
  { key: 'executing',   label: 'Snowflake MARTS' },
  { key: 'done',        label: 'Response' },
];

function App() {
  const [loading, setLoading] = useState(false);
  const [stage, setStage]   = useState<PipelineStage>('idle');
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError]   = useState<string | null>(null);

  const handleQuery = async (question: string) => {
    setError(null);
    setResult(null);
    setLoading(true);

    // Simulate visible pipeline stages for UX feedback
    setStage('generating');
    try {
      // Small artificial delay so users see the pipeline animate
      await new Promise((r) => setTimeout(r, 400));
      setStage('validating');
      await new Promise((r) => setTimeout(r, 300));
      setStage('executing');

      const data = await runQuery(question);

      setStage('done');
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred.');
      setStage('idle');
    } finally {
      setLoading(false);
    }
  };

  const activeStageIndex = PIPELINE_STEPS.findIndex((s) => s.key === stage);

  return (
    <div className="app">
      {/* ---- Header ---- */}
      <header className="header">
        <div className="header-logo">
          <div className="header-logo-icon">✦</div>
          <span className="header-logo-name gradient-text">QueryAI</span>
        </div>
        <span className="header-badge">Snowflake MARTS</span>
      </header>

      {/* ---- Main ---- */}
      <main className="main">

        {/* Hero */}
        <section className="hero">
          <h1>
            Ask your data<br />
            <span className="gradient-text">anything.</span>
          </h1>
          <p>
            Type a question in plain English. The AI agent translates it to SQL,
            validates it, runs it against your Snowflake MARTS, and returns
            instant results.
          </p>
        </section>

        {/* Pipeline visualiser */}
        <div className="pipeline">
          <div className={`pipeline-step${stage !== 'idle' ? ' active' : ''}`}>
            <span className="pipeline-dot" />
            <Sparkles size={12} />
            React
          </div>
          <span className="pipeline-arrow"><ArrowRight size={14} /></span>

          <div className={`pipeline-step${stage === 'generating' || activeStageIndex >= 1 ? ' active' : ''}`}>
            <span className="pipeline-dot" />
            <Cpu size={12} />
            Text-to-SQL Agent
          </div>
          <span className="pipeline-arrow"><ArrowRight size={14} /></span>

          <div className={`pipeline-step${stage === 'validating' || activeStageIndex >= 2 ? ' active' : ''}`}>
            <span className="pipeline-dot" />
            SQL Validation
          </div>
          <span className="pipeline-arrow"><ArrowRight size={14} /></span>

          <div className={`pipeline-step${stage === 'executing' || activeStageIndex >= 3 ? ' active' : ''}`}>
            <span className="pipeline-dot" />
            <Database size={12} />
            Snowflake MARTS
          </div>
          <span className="pipeline-arrow"><ArrowRight size={14} /></span>

          <div className={`pipeline-step${stage === 'done' ? ' active' : ''}`}>
            <span className="pipeline-dot" />
            Response
          </div>
        </div>

        {/* Query input + example chips */}
        <QueryInput onSubmit={handleQuery} loading={loading} />

        {/* Error */}
        {error && (
          <div className="error-banner" role="alert">
            <AlertTriangle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Results skeleton while executing */}
        {loading && <ResultsTable columns={[]} rows={[]} rowCount={0} loading />}

        {/* SQL viewer */}
        {result && !loading && (
          <SQLViewer sql={result.sql} modelUsed={result.model_used} />
        )}

        {/* Results table */}
        {result && !loading && (
          <ResultsTable
            columns={result.columns}
            rows={result.rows}
            rowCount={result.row_count}
          />
        )}
      </main>
    </div>
  );
}

export default App;
