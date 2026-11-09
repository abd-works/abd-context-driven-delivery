// E2E helper: Story UI's Vite settings with the API proxy pointed at the in-memory dev server on 3021 and Vite on 5193.
import react from 'file:///C:/dev/story-ui/node_modules/@vitejs/plugin-react/dist/index.js';
export default {
  root: 'C:/dev/story-ui/packages/story-map-workspace',
  plugins: [react()],
  server: { host: '127.0.0.1', port: 5193, strictPort: true, proxy: { '/api': 'http://127.0.0.1:3021' } },
};
