import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';

const here = path.dirname(fileURLToPath(import.meta.url));
const python = process.env.PYTHON || 'python';
const child = spawn(python, ['-u', path.join(here, 'host.py')], { stdio: ['pipe', 'pipe', 'inherit'] });
const lines = createInterface({ input: child.stdout });
const pending: Array<(line: string) => void> = [];

lines.on('line', (line) => {
  const resolve = pending.shift();
  if (resolve) {
    resolve(line);
  }
});

function ask(body: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    pending.push((line) => {
      try {
        resolve(JSON.parse(line));
      } catch (error) {
        reject(error);
      }
    });
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
    const payload = await ask({ operation, ...request.body });
    response.json(payload);
  });
}

const port = Number(process.env.PORT || 3000);
app.listen(port);
