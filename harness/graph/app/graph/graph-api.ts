import type { CddApi } from '@cdd/cdd-shared';

const API_ROOT = '/api';

type Failure = { error?: string; diagnosis?: string };

export class GraphCallFailure extends Error {
  constructor(diagnosis: string) {
    super(diagnosis);
    this.name = 'GraphCallFailure';
  }
}

// Every call the explorer makes to its server. The page shows a failure where the operation that met it was started, so
// a failed call throws its diagnosis instead of answering null.
export class GraphApi implements CddApi {
  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    const response = await fetch(`${API_ROOT}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const raw = await response.text();
    if (!raw.trim()) {
      throw new GraphCallFailure(
        `Empty response from ${path} (HTTP ${response.status}). The graph server may have restarted during a long load — try Reload working copy.`,
      );
    }
    const answer = this.parsed(path, response.status, raw);
    if (!response.ok) {
      const failure = (answer ?? {}) as Failure;
      throw new GraphCallFailure(failure.diagnosis || failure.error || `${path} failed (HTTP ${response.status})`);
    }
    return answer as Result | null;
  }

  private parsed(path: string, status: number, raw: string): unknown {
    try {
      return JSON.parse(raw);
    } catch (cause) {
      const detail = cause instanceof Error ? cause.message : String(cause);
      throw new GraphCallFailure(`Invalid JSON from ${path} (HTTP ${status}): ${detail}`);
    }
  }
}
