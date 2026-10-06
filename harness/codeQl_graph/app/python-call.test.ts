import { afterEach, expect, it, vi } from 'vitest';
import { PythonCall } from './python-call';

afterEach(() => {
  vi.unstubAllGlobals();
});

it('should surface the python traceback when the api reports a failure', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => ({
      ok: true,
      json: async () => ({
        ok: false,
        error: 'load_working_copy\nNo working copy for stories.',
        error_type: 'QueryFailure',
        traceback: 'Traceback (most recent call last):\n  File "host.py", line 1, in handle\nQueryFailure: load_working_copy',
      }),
    })),
  );

  const client = new PythonCall();
  await expect(client.run('load_working_copy', { folder: 'C:\\repo' })).rejects.toThrow(
    'Traceback (most recent call last):',
  );
});

it('should surface a timeout when the api never answers', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => {
      throw new DOMException('The operation timed out.', 'TimeoutError');
    }),
  );

  const client = new PythonCall(50);
  await expect(client.run('load_working_copy', { folder: 'C:\\repo' })).rejects.toThrow('timed out');
});
