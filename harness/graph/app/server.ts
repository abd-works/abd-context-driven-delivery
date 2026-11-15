import { execFile } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express, { type Request, type Response } from 'express';

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection';
import { CddRequestError, cddProgressRoutes, type CddRoute } from '@cdd/cdd-shared';
import { chatRoutes } from '@cdd/harness/chat/chat';
import { graphRoutes } from '@cdd/harness/graph/graph';
import ports from './ports.json';

const here = path.dirname(fileURLToPath(import.meta.url));
const python = process.env.PYTHON || 'python';
const API_ROOT = '/api';
const BAD_REQUEST = 400;
const FAILED = 500;
// The chat route the page needs: sending the chat that opened it (?chat=) each failure the page meets.
const CHAT_ROUTES = ['/chat/:chat/send'];

// One cdd server holds the graph. A route reaches it on the connection of the project the page names (?project=, sent
// as the project header), so the call works in the session open in that project, the one the board shows as active;
// a page naming none works on the project the explorer was started on (GRAPH_PROJECT, set by scripts/start.py).
const projects = new ProjectConnections(new CddConnection(process.env.GRAPH_PROJECT));

const textOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure));

// What a person pastes to an agent: the operation, the folder it ran on, and what cdd answered.
function diagnosis(route: CddRoute, request: Request, failure: unknown): string {
  const body = (request.body ?? {}) as Record<string, unknown>;
  const operation = route.path.split('/').pop()?.replace(/-/g, '_') ?? route.path;
  const database = String(body.database || body.folder || 'the loaded graph');
  return `I just encountered an error doing ${operation} on ${database}. Please diagnose and fix.\n\n${textOf(failure)}`;
}

async function answer(route: CddRoute, request: Request, response: Response): Promise<void> {
  try {
    response.json((await route.run(projects.of(request), request)) ?? null);
  } catch (failure) {
    const status = failure instanceof CddRequestError ? BAD_REQUEST : FAILED;
    response.status(status).json({ error: textOf(failure), diagnosis: diagnosis(route, request, failure) });
  }
}

// A folder dialog opens on this machine, which only the explorer's server can do; it is not a graph operation.
function chooseFolder(title: string): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile(python, [path.join(here, 'choose_folder.py'), title], (failure, stdout) => (failure ? reject(failure) : resolve(stdout.trim())));
  });
}

const app = express();
app.use(express.json());

// A failure answering a request the request can no longer be told of, as when the answer was half sent, is written
// to stderr whole, so it is seen where the server runs.
function unanswered(route: string, failure: unknown): void {
  console.error(`Error: the Graph web server could not answer ${route}:`, failure);
}

const routes = [...graphRoutes, ...cddProgressRoutes, ...chatRoutes.filter((route) => CHAT_ROUTES.includes(route.path))];
for (const route of routes) {
  app.post(`${API_ROOT}${route.path}`, (request, response) => {
    answer(route, request, response).catch((failure) => unanswered(route.path, failure));
  });
}

app.post(`${API_ROOT}/explorer/choose-folder`, async (request, response) => {
  try {
    response.json({ folder: await chooseFolder(String(request.body?.title ?? 'Select a folder')) });
  } catch (failure) {
    response.status(FAILED).json({ error: textOf(failure), diagnosis: textOf(failure) });
  }
});

const explorerUi = process.env.EXPLORER_UI_URL || `http://localhost:${ports.app[0]}`;
const port = Number(process.env.PORT || ports.web[0]);

app.get('/', (_request, response) => {
  response.redirect(302, explorerUi);
});

app.get('/ping', (_request, response) => {
  response.json({
    ok: true,
    ping: 'pong',
    service: 'graph_web',
    url: `http://127.0.0.1:${port}`,
    port,
  });
});

// A port another process holds is the usual reason the Graph does not start, often a Graph server another checkout
// started on its own (`npm run server`): say so in one line the chat bar shows, instead of a stack.
app.listen(port).on('error', (failure: NodeJS.ErrnoException) => {
  const held = failure.code === 'EADDRINUSE' ? `port ${port} is held by another process, often another Graph server; stop it, or set PORT` : failure.message;
  console.error(`Error: the Graph web server did not start: ${held}`);
  process.exit(1);
});
