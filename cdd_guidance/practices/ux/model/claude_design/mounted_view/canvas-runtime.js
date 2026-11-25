// The design canvas's stand-ins for what a production view reaches outside itself, bundled with the project's views
// (build-mounted-views.mjs). A canvas has no server and must not leave its artboard, so:
//
// - fetch: each request a view makes is answered by the project's canvasRoutes, keyed `METHOD /path`, which run the
//   domain operation on the objects the scenario on show bound and the repositories its Givens filled;
// - window.location: a view that navigates moves the story explorer to the story its page belongs to, through
//   canvasNavigation and the explorer's go, and the artboard stays where it is.
//
// The build points every `fetch` and `window.location` the views name at these (esbuild define), so nothing else on the
// canvas page is touched. CanvasMount is the component a mounted screen draws: it takes the screen's scene and renders
// the project's view by name.
import React from 'react';

const ORIGIN = 'https://canvas.local';
const NOTHING = Object.freeze({});
const NOT_FOUND = 404;
const FAILED = 500;

// The scene of the screen drawn last: a story explorer shows one screen at a time.
let scene = { bound: NOTHING, repositories: NOTHING, go: null, routes: NOTHING, navigation: NOTHING };

function pathOf(address) {
  return new URL(String(address), `${ORIGIN}/`).pathname;
}

function requestAddress(input) {
  if (typeof input === 'string') return input;
  if (input && typeof input.url === 'string') return input.url;
  return String(input);
}

// A Response as far as a client reads one; the walk renders screens where no Response exists.
function answer(body, status) {
  const text = JSON.stringify(body === undefined ? null : body);
  return { ok: status >= 200 && status < 300, status, headers: { get: () => 'application/json' },
    json: () => Promise.resolve(JSON.parse(text)), text: () => Promise.resolve(text) };
}

function postedBody(init) {
  if (!init || init.body === undefined || init.body === null) return null;
  try {
    return JSON.parse(String(init.body));
  } catch (unreadable) {
    return init.body;
  }
}

export async function canvasFetch(input, init) {
  const method = String((init && init.method) || 'GET').toUpperCase();
  const path = pathOf(requestAddress(input));
  const route = scene.routes[`${method} ${path}`];
  if (!route) {
    console.warn(`Design canvas: no canvas route answers ${method} ${path}`);
    return answer({ message: `No canvas route answers ${method} ${path}` }, NOT_FOUND);
  }
  try {
    return answer(await route({ body: postedBody(init), bound: scene.bound, repositories: scene.repositories }), 200);
  } catch (refused) {
    const status = refused && typeof refused.status === 'number' ? refused.status : FAILED;
    if (status >= FAILED) console.error('Design canvas: a canvas route failed', refused);
    return answer({ message: String((refused && refused.message) || refused) }, status);
  }
}

// The story a page belongs to: its path as written, or with or without its last slash.
function storyAt(path) {
  const navigation = scene.navigation;
  const bare = path.length > 1 ? path.replace(/\/$/, '') : path;
  return navigation[path] || navigation[bare] || navigation[`${bare}/`] || null;
}

function navigate(address) {
  const path = pathOf(address);
  const story = storyAt(path);
  if (!story || !scene.go) {
    console.warn(`Design canvas: no story for ${path}; the screen stays where it is`);
    return;
  }
  scene.go(story);
}

export const canvasLocation = {
  origin: ORIGIN, host: 'canvas.local', hostname: 'canvas.local', protocol: 'https:', pathname: '/', search: '', hash: '',
  get href() { return `${ORIGIN}/`; },
  set href(address) { navigate(address); },
  assign: navigate,
  replace: navigate,
  reload() {},
  toString() { return `${ORIGIN}/`; },
};

globalThis.__canvasFetch = canvasFetch;
globalThis.__canvasLocation = canvasLocation;

// The component a mounted screen draws: `view` names one of the project's exports, which is handed the scene.
function hasAny(objects) {
  return Boolean(objects) && Object.keys(objects).length > 0;
}

// Each fixture load hands over a new bound object; its number tells one load's mount from the next.
const loads = new WeakMap();
let nextLoad = 0;
function loadNumber(bound) {
  if (!loads.has(bound)) loads.set(bound, ++nextLoad);
  return loads.get(bound);
}

export function canvasMount(project) {
  const routes = project.canvasRoutes || NOTHING;
  const navigation = project.canvasNavigation || NOTHING;
  return function CanvasMount({ view, bound, repositories, position, go }) {
    scene = { bound: bound || NOTHING, repositories: repositories || NOTHING, go: go || null, routes, navigation };
    const View = project[view];
    if (typeof View !== 'function') return React.createElement('p', { role: 'alert' }, `The canvas bundle has no view ${view}.`);
    // The screen hands the scenario's fixture over once it has loaded. A view mounted before then would ask the
    // canvas routes for data the repositories do not hold yet, so it waits.
    if (!hasAny(scene.bound) && !hasAny(scene.repositories)) return React.createElement('p', { role: 'status' }, 'Loading the scenario…');
    // Each load hands over new objects: mounting the view afresh makes it ask for the new scenario's data.
    return React.createElement(View, { key: loadNumber(scene.bound), bound: scene.bound, repositories: scene.repositories, position: position || NOTHING });
  };
}
