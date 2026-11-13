import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

// `npm start`, and what the chat that opens the Graph app runs: the explorer's two servers in this one process. Vite
// serves the page on the app's ports and passes /api to the web server, so the app answers only while both run. Both
// live and die with this process: the chat stops the app by ending it, which on Windows ends no child process, so
// neither server is a child process of its own.
import './server';

const here = path.dirname(fileURLToPath(import.meta.url));

const page = await createServer({ configFile: path.join(here, 'vite.config.ts'), root: here });
await page.listen();
