import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiPort = Number(process.env.PORT ?? 3001);
const uiPort = Number(process.env.VITE_PORT ?? 3000);

export default defineConfig({
  plugins: [react()],
  worker: { format: 'es' },
  server: {
    port: uiPort,
    strictPort: true,
    proxy: {
      '/api': {
        target: `http://localhost:${apiPort}`,
        timeout: 20 * 60 * 1000,
        proxyTimeout: 20 * 60 * 1000,
      },
    },
  },
});
