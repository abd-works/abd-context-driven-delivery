export class PythonCall {
  async run<T>(operation: string, body: Record<string, unknown> = {}): Promise<T> {
    const response = await fetch(`/api/${operation}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const payload = (await response.json()) as { ok: boolean; result?: T; error?: string };
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || response.statusText);
    }
    return payload.result as T;
  }
}
