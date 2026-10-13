export type PythonFailure = {
  ok: false;
  error?: string;
  error_type?: string;
  traceback?: string;
  diagnosis?: string;
};

export type PythonSuccess<T> = {
  ok: true;
  result: T;
};

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_GRAPH_CLIENT_TIMEOUT_MS || 10_800_000);

export class PythonCall {
  constructor(private readonly timeoutMs = DEFAULT_TIMEOUT_MS) {}

  async run<T>(operation: string, body: Record<string, unknown> = {}): Promise<T> {
    const response = await fetch(`/api/${operation}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    const raw = await response.text();
    if (!raw.trim()) {
      throw new Error(
        `Empty response from /api/${operation} (HTTP ${response.status}). The graph API may have restarted during a long load — try Reload working copy.`,
      );
    }
    let payload: PythonSuccess<T> | PythonFailure;
    try {
      payload = JSON.parse(raw) as PythonSuccess<T> | PythonFailure;
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      throw new Error(`Invalid JSON from /api/${operation} (HTTP ${response.status}): ${detail}`);
    }
    if (!response.ok || !payload.ok) {
      const failure = payload as PythonFailure;
      const detail = failure.error ?? response.statusText ?? 'request failed';
      throw new Error(
        failure.diagnosis || failure.traceback || `${failure.error_type ?? 'Error'}: ${detail}`,
      );
    }
    return payload.result;
  }
}
