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

const DEFAULT_TIMEOUT_MS = Number(import.meta.env.VITE_CODEQL_CLIENT_TIMEOUT_MS || 10_800_000);

export class PythonCall {
  constructor(private readonly timeoutMs = DEFAULT_TIMEOUT_MS) {}

  async run<T>(operation: string, body: Record<string, unknown> = {}): Promise<T> {
    const response = await fetch(`/api/${operation}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    const payload = (await response.json()) as PythonSuccess<T> | PythonFailure;
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
