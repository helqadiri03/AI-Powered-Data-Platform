import { useState } from 'react';
import { askDocumentation, type RAGResponse } from '../services/api';
import { AlertTriangle, Send, Loader2, FileText, Bot, User } from 'lucide-react';

export default function RAGAssistant() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{ role: 'user' | 'assistant'; text: string; sources?: string[] }[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const currentQuestion = question.trim();
    setQuestion('');
    setError(null);
    setLoading(true);

    setHistory((prev) => [...prev, { role: 'user', text: currentQuestion }]);

    try {
      const data = await askDocumentation(currentQuestion);
      setHistory((prev) => [
        ...prev,
        { role: 'assistant', text: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-container">
      <div className="chat-window">
        {history.length === 0 ? (
          <div className="chat-empty">
            <Bot size={48} className="chat-empty-icon" />
            <h3>AI Documentation Assistant</h3>
            <p>Ask me anything about the e-commerce platform architecture, schemas, or pipelines.</p>
          </div>
        ) : (
          <div className="chat-messages">
            {history.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                </div>
                <div className="chat-bubble">
                  <div className="chat-text">{msg.text}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="chat-sources">
                      <strong>Sources:</strong>
                      <div className="sources-list">
                        {msg.sources.map((src, i) => (
                          <span key={i} className="source-chip">
                            <FileText size={12} /> {src}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant">
                <div className="chat-avatar"><Bot size={18} /></div>
                <div className="chat-bubble loading">
                  <Loader2 className="spinner" size={16} /> Thinking...
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-banner" style={{ margin: '1rem 0' }}>
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about the platform..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="chat-submit-btn" disabled={loading || !question.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
