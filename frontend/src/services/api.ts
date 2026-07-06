// API service — communicates with FastAPI Text-to-SQL backend

const API_BASE = import.meta.env.VITE_API_URL ?? '';

export interface QueryResponse {
  question: string;
  sql: string;
  model_used: string;
  columns: string[];
  rows: (string | number | null)[][];
  row_count: number;
}

export interface ApiError {
  detail: string;
}

export interface RAGResponse {
  answer: string;
  sources: string[];
}

export async function runQuery(question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const err: ApiError = await response.json().catch(() => ({
      detail: `HTTP ${response.status} — ${response.statusText}`,
    }));
    throw new Error(err.detail);
  }

  return response.json() as Promise<QueryResponse>;
}

export async function askDocumentation(question: string): Promise<RAGResponse> {
  const response = await fetch(`${API_BASE}/api/rag`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const err: ApiError = await response.json().catch(() => ({
      detail: `HTTP ${response.status} — ${response.statusText}`,
    }));
    throw new Error(err.detail);
  }

  return response.json() as Promise<RAGResponse>;
}
