import type { IncomingMessage, ServerResponse } from 'node:http';
import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vitest/config';

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
        const heard = typeof address === 'object' && address ? address.port : 5173;
        const host = typeof address === 'object' && address ? address.address : '127.0.0.1';
        const origin = host === '::1' || host === '::' ? `http://localhost:${heard}` : `http://127.0.0.1:${heard}`;
        const body = JSON.stringify({
          ok: true,
          ping: 'pong',
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
  test: {
    environment: 'jsdom',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:3000',
    },
  },
});
