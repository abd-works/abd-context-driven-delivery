import type { IncomingMessage, ServerResponse } from 'node:http';
import { fileURLToPath } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vitest/config';
// The app's ports, written once for this config, the web server, and the Python that reports and starts the app.
import ports from './ports.json';

const resolved = (path: string): string => fileURLToPath(new URL(path, import.meta.url));

// The generated graph classes and views sit in the install, outside this package, so they take React and Monaco from here.
const aliases = {
  '@cdd': resolved('../../../.claude/language-adapters/typescript'),
  react: resolved('./node_modules/react'),
  '@monaco-editor/react': resolved('./node_modules/@monaco-editor/react'),
};

function ping(): Plugin {
  return {
    name: 'cdd-ping',
    configureServer(server) {
      server.middlewares.use('/ping', (req: IncomingMessage, res: ServerResponse, next: () => void) => {
        if (req.method !== 'GET' && req.method !== 'HEAD') {
          next();
          return;
        }
        const address = server.httpServer?.address();
        const heard = typeof address === 'object' && address ? address.port : ports.app[0];
        const host = typeof address === 'object' && address ? address.address : '127.0.0.1';
        const origin = host === '::1' || host === '::' ? `http://localhost:${heard}` : `http://127.0.0.1:${heard}`;
        const body = JSON.stringify({
          ok: true,
          ping: 'pong',
          service: 'graph_app',
          url: origin,
          port: heard,
        });
        res.statusCode = 200;
        res.setHeader('content-type', 'application/json');
        res.end(req.method === 'HEAD' ? undefined : body);
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), ping()],
  resolve: { alias: aliases },
  test: {
    environment: 'jsdom',
  },
  server: {
    host: '::',
    port: ports.app[0],
    proxy: {
      '/api': `http://localhost:${ports.web[0]}`,
    },
  },
});
