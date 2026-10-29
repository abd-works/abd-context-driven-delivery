// Bundles canvas fixtures for the browser. Run from the workspace root:
//   node build-canvas-fixtures.mjs <entry.ts> <out.js>
// The node tier (`*-node` modules, lowdb, node built-ins) stays out: each node module becomes a stand-in that
// exports the same names, so the domain repositories load and the node repositories are never reached.
// Vitest becomes a no-op: shared stories import `expect` for their Thens, which the canvas never runs.
import { build } from 'esbuild';
import { readFileSync } from 'node:fs';

const [entry, outfile] = process.argv.slice(2);
const NODE_TIER = /-node$|^lowdb(\/.*)?$|^node:|^(fs|path|url|os|crypto|express)$/;
const EXPORTED = /export\s+(?:declare\s+)?(?:abstract\s+)?(?:const|let|var|class|function\*?|async\s+function)\s+([A-Za-z_$][\w$]*)/g;

const VITEST = `
const chain = new Proxy(function () { return chain; }, { get: () => chain, apply: () => chain });
export const expect = chain;
export const vi = chain;
export const describe = () => {};
export const it = () => {};
export const test = () => {};
export const beforeEach = () => {};
export const afterEach = () => {};
export const beforeAll = () => {};
export const afterAll = () => {};
`;

const browserOnly = {
  name: 'canvas-browser-only',
  setup(builder) {
    builder.onResolve({ filter: /^vitest$/ }, () => ({ path: 'vitest', namespace: 'canvas-stub' }));
    builder.onResolve({ filter: NODE_TIER }, async (args) => {
      if (args.pluginData?.real) return undefined;
      const resolved = await builder.resolve(args.path, { resolveDir: args.resolveDir, kind: args.kind, pluginData: { real: true } });
      return { path: resolved.path || args.path, namespace: 'canvas-stub' };
    });
    builder.onLoad({ filter: /.*/, namespace: 'canvas-stub' }, (args) => {
      if (args.path === 'vitest') return { contents: VITEST, loader: 'js' };
      let source = '';
      try { source = readFileSync(args.path, 'utf8'); } catch { source = ''; }
      const names = [...new Set([...source.matchAll(EXPORTED)].map((match) => match[1]))];
      // A capitalised name is a class: an empty class keeps `instanceof` checks on node types false instead of throwing.
      const contents = names.map((name) => (/^[A-Z]/.test(name) ? `export class ${name} {}` : `export const ${name} = undefined;`)).join('\n') + '\nexport default undefined;';
      return { contents, loader: 'js' };
    });
  },
};

await build({
  entryPoints: [entry],
  bundle: true,
  format: 'iife',
  globalName: 'CanvasFixtures',
  platform: 'browser',
  target: 'es2020',
  tsconfig: 'tsconfig.json',
  outfile,
  jsx: 'automatic',
  loader: { '.css': 'empty', '.svg': 'dataurl', '.png': 'dataurl' },
  define: { 'process.env.NODE_ENV': '"production"' },
  plugins: [browserOnly],
  logLevel: 'warning',
});
