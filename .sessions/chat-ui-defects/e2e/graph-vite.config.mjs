// E2E helper: the graph app's Vite settings, with the API proxy pointed at the e2e server on 3010 and Vite on 5183.
import react from 'file:///C:/dev/abd-context-driven-delivery/harness/graph/app/node_modules/@vitejs/plugin-react/dist/index.js';
const APP = 'C:/dev/abd-context-driven-delivery/harness/graph/app';
export default {
  root: APP,
  plugins: [react()],
  resolve: {
    alias: {
      '@cdd': 'C:/dev/abd-context-driven-delivery/.claude/language-adapters/typescript',
      react: `${APP}/node_modules/react`,
      '@monaco-editor/react': `${APP}/node_modules/@monaco-editor/react`,
    },
  },
  server: { host: '127.0.0.1', port: 5183, strictPort: true, proxy: { '/api': 'http://127.0.0.1:3010' } },
};
