// Bundles a project's production views for the design canvas. Run from the project's root, so esbuild and the
// project's own packages resolve from its node_modules:
//   node build-mounted-views.mjs <config.json>
// config: { entry, runtime, work, outdir, name, namespace, tsconfig }
//   entry    - the project's view entry: its screens by name, canvasRoutes and canvasNavigation
//   runtime  - this folder, holding canvas-runtime.js and the React shims
//   work     - a folder in the project for the generated bundle entry
//   outdir   - the canvas version's design system folder (project/ds/<folder>)
//   name     - the bundle's file name, <name>.js and <name>.css
//   namespace - the global the canvas reads components from (<namespace>.CanvasMount)
import { build } from 'esbuild';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const config = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const { scopeCss } = await import(pathToFileURL(path.join(config.runtime, 'scope-css.mjs')).href);
const forward = (file) => file.split(path.sep).join('/');

mkdirSync(config.work, { recursive: true });
const entry = path.join(config.work, 'mounted-views.js');
writeFileSync(entry, [
  `import { canvasMount } from '${forward(path.join(config.runtime, 'canvas-runtime.js'))}';`,
  `import * as project from '${forward(path.resolve(config.entry))}';`,
  'export const CanvasMount = canvasMount(project);',
  '',
].join('\n'));

// A stylesheet that names a file the project does not have (a font never added) is drawn without it, as a browser
// does, and the build says so instead of failing.
const missingFiles = {
  name: 'canvas-missing-files',
  setup(builder) {
    builder.onResolve({ filter: /.*/ }, (args) => {
      if (args.kind !== 'url-token' || /^(data:|https?:|\/\/)/.test(args.path)) return undefined;
      const file = path.resolve(args.resolveDir, args.path.split(/[?#]/)[0]);
      if (existsSync(file)) return undefined;
      console.warn(`mounted views: ${args.importer} names ${args.path}, which is not there; the canvas draws it without`);
      return { path: args.path, external: true };
    });
  },
};

const header = { format: 4, namespace: config.namespace, components: [{ name: 'CanvasMount' }] };
const outfile = path.join(config.outdir, `${config.name}.js`);
await build({
  entryPoints: [entry],
  bundle: true,
  format: 'iife',
  globalName: config.namespace,
  platform: 'browser',
  target: 'es2020',
  outfile,
  tsconfig: config.tsconfig,
  jsx: 'automatic',
  alias: {
    'react': path.join(config.runtime, 'react'),
    'react/jsx-runtime': path.join(config.runtime, 'react', 'jsx-runtime.js'),
    'react/jsx-dev-runtime': path.join(config.runtime, 'react', 'jsx-dev-runtime.js'),
    'react-dom': path.join(config.runtime, 'react-dom'),
    'react-dom/client': path.join(config.runtime, 'react-dom', 'client.js'),
  },
  define: {
    'fetch': 'globalThis.__canvasFetch',
    'window.fetch': 'globalThis.__canvasFetch',
    'window.location': 'globalThis.__canvasLocation',
    'process.env.NODE_ENV': '"production"',
  },
  loader: { '.svg': 'dataurl', '.png': 'dataurl', '.jpg': 'dataurl', '.gif': 'dataurl', '.woff2': 'file', '.woff': 'file', '.ttf': 'file' },
  assetNames: 'assets/[name]-[hash]',
  banner: { js: `/* @ds-bundle: ${JSON.stringify(header)} */` },
  footer: { js: `window.${config.namespace} = ${config.namespace};` },
  plugins: [missingFiles],
  logLevel: 'warning',
});

const stylesheet = path.join(config.outdir, `${config.name}.css`);
if (existsSync(stylesheet)) writeFileSync(stylesheet, scopeCss(readFileSync(stylesheet, 'utf8')));
console.log(JSON.stringify({ script: outfile, stylesheet: existsSync(stylesheet) ? stylesheet : null }));
