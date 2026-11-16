import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

import ports from './ports.json';
import { servePort } from './serve-port';

// `npm start`, and what the chat that opens the Graph app runs: the explorer's two servers in this one process. Vite
// serves the page on the app's ports and passes /api to the web server, so the app answers only while both run. Both
// live and die with this process: the chat stops the app by ending it, which on Windows ends no child process, so
// neither server is a child process of its own.
//
// A dev-lane chat starts it with `--port N`, the page's port on that lane; the web server moves by as much, so neither
// meets the stable lane's Graph. The web server reads its port when it is imported, so it is imported after.
const page = servePort(process.argv, ports.app[0]);
const web = ports.web[0] + page - ports.app[0];
if (page !== ports.app[0]) {
  process.env.PORT = String(web);
  process.env.EXPLORER_UI_URL = `http://localhost:${page}`;
}
await import('./server');

const here = path.dirname(fileURLToPath(import.meta.url));

const vite = await createServer({
  configFile: path.join(here, 'vite.config.ts'),
  root: here,
  server: { port: page, proxy: { '/api': `http://localhost:${web}` } },
});
await vite.listen();
