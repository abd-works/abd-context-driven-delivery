import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';

const here = path.dirname(fileURLToPath(import.meta.url));
const python = process.env.PYTHON || 'python';
const PYTHON_TIMEOUT_MS = Number(process.env.CODEQL_PYTHON_TIMEOUT_MS || 605_000);
const child = spawn(python, ['-u', path.join(here, 'host.py')], { stdio: ['pipe', 'pipe', 'inherit'] });
const lines = createInterface({ input: child.stdout });
const pending: Array<(line: string) => void> = [];

type PythonResponse = {
  ok: boolean;
  result?: unknown;
  error?: string;
  error_type?: string;
  traceback?: string;
};

lines.on('line', (line) => {
  const resolve = pending.shift();
  if (resolve) {
    resolve(line);
  }
});

child.on('error', (error) => {
  rejectAll(error);
});

child.on('exit', (code, signal) => {
  if (code === 0 && !signal) {
    return;
  }
  rejectAll(new Error(`Python host exited (code=${code ?? 'null'}, signal=${signal ?? 'null'})`));
});

function rejectAll(error: Error) {
  while (pending.length > 0) {
    const resolve = pending.shift();
    if (resolve) {
      resolve(JSON.stringify({ ok: false, error: error.message, error_type: error.name, traceback: error.stack }));
    }
  }
}

function operationName(body: unknown): string {
  if (typeof body === 'object' && body !== null && 'operation' in body) {
    return String((body as { operation: unknown }).operation);
  }
  return 'unknown';
}

function ask(body: unknown): Promise<unknown> {
  const operation = operationName(body);
  return new Promise((resolve, reject) => {
    let settled = false;
    const timer = setTimeout(() => {
      if (settled) {
        return;
      }
      settled = true;
      const index = pending.indexOf(onLine);
      if (index >= 0) {
        pending.splice(index, 1);
      }
      reject(new Error(`Python host timed out after ${PYTHON_TIMEOUT_MS}ms during ${operation}`));
    }, PYTHON_TIMEOUT_MS);

    function onLine(line: string) {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(timer);
      try {
        const payload = JSON.parse(line) as PythonResponse;
        if (!payload.ok) {
          const message =
            payload.traceback ||
            `${payload.error_type ?? 'Error'}: ${payload.error ?? `operation ${operation} failed`}`;
          reject(new Error(message));
          return;
        }
        resolve(payload.result);
      } catch (error) {
        reject(error);
      }
    }

    pending.push(onLine);
    child.stdin.write(JSON.stringify(body) + '\n');
  });
}

const app = express();
app.use(express.json());

for (const operation of [
  'load_working_copy',
  'inventory',
  'return_nodes',
  'filter_choices',
  'source',
  'create_database',
  'reload_working_copy',
  'update_working_copy',
  'choose_folder',
]) {
  app.post(`/api/${operation}`, async (request, response) => {
    try {
      const result = await ask({ operation, ...request.body });
      response.json({ ok: true, result });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const traceback = error instanceof Error ? error.stack : undefined;
      response.status(500).json({
        ok: false,
        error: message,
        error_type: error instanceof Error ? error.name : 'Error',
        traceback,
      });
    }
  });
}

const port = Number(process.env.PORT || 3000);
app.listen(port);
