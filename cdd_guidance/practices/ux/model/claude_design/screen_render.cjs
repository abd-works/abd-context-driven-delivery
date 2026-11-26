// Renders Claude Design screen artboards (.dc.html) to the text each one shows, for the story canvas walk
// (screen_walk.py). Reads {"jobs": [{"artboard": <absolute path>, "props": {...}}]} on stdin and writes one result per
// job on stdout: {"text": ...} or {"error": ...}.
//
// Each job runs in a fresh browser-like context: the scripts the artboard and the components it dc-imports load
// (resolved beside each file; the canvas's own support.js and a local React are left to the canvas), a small React
// that renders function and class components once, with hooks answering their first value, and the artboard's
// DCLogic built with the props given, mounted, and given time to settle on a fake clock before it is drawn. The x-dc
// template is drawn with sc-if, sc-for, x-import (a component from the global scope), and dc-import (another artboard
// beside it). What the screen shows is its text, the values of its fields, and its aria-labels.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ELEMENT = Symbol.for('screen-walk.element');
const FRAGMENT = Symbol.for('screen-walk.fragment');
const BLOCK = new Set(['address', 'article', 'aside', 'blockquote', 'br', 'dd', 'div', 'dl', 'dt', 'fieldset', 'figcaption',
  'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'label', 'legend', 'li', 'main', 'nav', 'ol',
  'option', 'p', 'pre', 'section', 'table', 'tbody', 'td', 'th', 'thead', 'tr', 'ul', 'button']);
const SILENT = new Set(['script', 'style', 'template', 'helmet', 'title', 'meta', 'link', 'head']);
const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);
// How long, on the fake clock, a screen may take to settle after it mounts.
const SETTLE_MS = 15000;

// ---- the fake clock: timers run in order of when they fall due, without waiting --------------------------------
class Clock {
  constructor() { this.now = 0; this.queue = []; this.id = 0; this.errors = []; }
  setTimeout(callback, ms, ...args) { const id = ++this.id; this.queue.push({ id, at: this.now + Math.max(0, Number(ms) || 0), callback, args }); return id; }
  setInterval(callback, ms, ...args) {
    const id = ++this.id, every = Math.max(1, Number(ms) || 1);
    const repeat = () => { callback(...args); this.queue.push({ id, at: this.now + every, callback: repeat, args: [] }); };
    this.queue.push({ id, at: this.now + every, callback: repeat, args: [] });
    return id;
  }
  clear(id) { this.queue = this.queue.filter((timer) => timer.id !== id); }
  async settle() {
    for (let round = 0; round < 20000; round += 1) {
      await new Promise((resolve) => setImmediate(resolve));
      if (!this.queue.length) return;
      this.queue.sort((a, b) => a.at - b.at || a.id - b.id);
      const next = this.queue.shift();
      if (next.at > SETTLE_MS) { this.queue = []; return; }
      this.now = Math.max(this.now, next.at);
      try { next.callback(...next.args); } catch (problem) { this.errors.push(problem); }
    }
  }
}

// ---- a small React: elements, hooks at their first value, context, portals drawn in place ---------------------
function flatten(children, into = []) {
  if (Array.isArray(children)) children.forEach((child) => flatten(child, into));
  else if (children !== undefined && children !== null && children !== false && children !== true) into.push(children);
  return into;
}

function makeReact() {
  let ids = 0;
  function createElement(type, config, ...children) {
    const props = Object.assign({}, config || {});
    const key = props.key === undefined ? null : props.key;
    delete props.key; delete props.ref;
    if (children.length === 1) props.children = children[0];
    else if (children.length > 1) props.children = children;
    if (type && type.defaultProps) for (const name of Object.keys(type.defaultProps)) if (props[name] === undefined) props[name] = type.defaultProps[name];
    return { $$typeof: ELEMENT, type, props, key };
  }
  class Component {
    constructor(props) { this.props = props; this.state = {}; }
    setState(next) { this.state = Object.assign({}, this.state, typeof next === 'function' ? next(this.state, this.props) : next); }
    forceUpdate() {}
  }
  Component.prototype.isReactComponent = {};
  const noop = () => {};
  return {
    Fragment: FRAGMENT, StrictMode: FRAGMENT, Suspense: FRAGMENT, createElement, Component, PureComponent: Component,
    isValidElement: (thing) => Boolean(thing) && thing.$$typeof === ELEMENT,
    cloneElement: (element, extra, ...children) => createElement(element.type, Object.assign({ key: element.key }, element.props, extra || {}), ...children),
    createRef: () => ({ current: null }),
    useState: (initial) => [typeof initial === 'function' ? initial() : initial, noop],
    useReducer: (reducer, initial, init) => [init ? init(initial) : initial, noop],
    useRef: (initial) => ({ current: initial === undefined ? null : initial }),
    useEffect: noop, useLayoutEffect: noop, useInsertionEffect: noop, useImperativeHandle: noop, useDebugValue: noop,
    useMemo: (make) => make(), useCallback: (callback) => callback, useId: () => `:w${(ids += 1)}:`,
    useContext: (context) => context._value, useTransition: () => [false, (run) => run()], useDeferredValue: (value) => value,
    useSyncExternalStore: (subscribe, snapshot) => snapshot(),
    createContext: (value) => { const context = { _value: value }; context.Provider = { $$provider: context }; context.Consumer = { $$consumer: context }; return context; },
    forwardRef: (render) => ({ $$forward: render }), memo: (component) => component, lazy: () => () => null,
    Children: { map: (c, f) => flatten(c).map(f), forEach: (c, f) => flatten(c).forEach(f), toArray: (c) => flatten(c), count: (c) => flatten(c).length, only: (c) => c },
  };
}

// ---- drawing elements to text --------------------------------------------------------------------------------
class TextOut {
  constructor() { this.parts = []; }
  add(text) { this.parts.push(String(text)); }
  line() { this.parts.push('\n'); }
  text() {
    return this.parts.join('').split('\n').map((line) => line.replace(/\s+/g, ' ').trim()).filter(Boolean).join('\n');
  }
}

function draw(node, out) {
  if (node === null || node === undefined || node === false || node === true) return;
  if (typeof node === 'string' || typeof node === 'number') { out.add(node); return; }
  if (Array.isArray(node)) { node.forEach((child) => draw(child, out)); return; }
  if (typeof node !== 'object' || node.$$typeof !== ELEMENT) return;
  const { type, props } = node;
  if (type === FRAGMENT) { draw(props.children, out); return; }
  if (typeof type === 'string') { drawHost(type.toLowerCase(), props, out); return; }
  if (type && type.$$provider) {
    const context = type.$$provider, before = context._value;
    context._value = props.value;
    try { draw(props.children, out); } finally { context._value = before; }
    return;
  }
  if (type && type.$$consumer) { draw(props.children(type.$$consumer._value), out); return; }
  if (type && type.$$forward) { draw(type.$$forward(props, null), out); return; }
  if (typeof type === 'function' && type.prototype && type.prototype.isReactComponent) {
    const instance = new type(props);
    instance.props = props;
    if (instance.state === undefined || instance.state === null) instance.state = {};
    if (type.getDerivedStateFromProps) Object.assign(instance.state, type.getDerivedStateFromProps(props, instance.state));
    draw(instance.render(), out);
    return;
  }
  if (typeof type === 'function') { draw(type(props), out); return; }
  throw new Error(`cannot draw a component of type ${String(type)}`);
}

function drawHost(tag, props, out) {
  if (SILENT.has(tag)) return;
  // A block element starts a line; an inline one is kept apart from its neighbours by a space, so two prices drawn
  // side by side read as two prices.
  const block = BLOCK.has(tag);
  if (block) out.line(); else out.add(' ');
  if (props['aria-label']) { out.add(` ${props['aria-label']} `); out.line(); }
  if ((tag === 'input' || tag === 'textarea') && props.type !== 'hidden' && props.type !== 'password') {
    const value = props.value !== undefined ? props.value : props.defaultValue;
    if (value !== undefined && value !== null && value !== '') { out.add(` ${value} `); out.line(); }
  }
  if (props.dangerouslySetInnerHTML && props.dangerouslySetInnerHTML.__html) out.add(String(props.dangerouslySetInnerHTML.__html).replace(/<[^>]+>/g, ' '));
  draw(props.children, out);
  if (block) out.line(); else out.add(' ');
}

// ---- an artboard: its template, its scripts, its DCLogic -----------------------------------------------------
function parseTemplate(source) {
  const root = { tag: '#root', attrs: {}, kids: [] };
  const stack = [root];
  const pattern = /<\/([a-zA-Z0-9-]+)\s*>|<([a-zA-Z][a-zA-Z0-9-]*)((?:\s+[^\s=>/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*(\/?)>|([^<]+)|(<)/g;
  let match;
  while ((match = pattern.exec(source))) {
    const top = stack[stack.length - 1];
    if (match[1]) {
      const tag = match[1].toLowerCase();
      let index = stack.length - 1;
      while (index > 0 && stack[index].tag !== tag) index -= 1;
      if (index > 0) stack.length = index;
    } else if (match[2]) {
      const attrs = {};
      const attribute = /([^\s=>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
      let found;
      while ((found = attribute.exec(match[3] || ''))) attrs[found[1]] = found[2] ?? found[3] ?? found[4] ?? true;
      const element = { tag: match[2].toLowerCase(), attrs, kids: [] };
      top.kids.push(element);
      if (!match[4] && !VOID.has(element.tag)) stack.push(element);
    } else if (match[5]) top.kids.push(match[5]);
    else top.kids.push('<');
  }
  return root;
}

function decode(text) {
  return text.replace(/&nbsp;|&#160;/g, ' ').replace(/&middot;/g, '·').replace(/&rarr;/g, '→').replace(/&larr;/g, '←')
    .replace(/&times;/g, '×').replace(/&minus;/g, '−').replace(/&mdash;/g, '—').replace(/&ndash;/g, '–').replace(/&hellip;/g, '…')
    .replace(/&quot;/g, '"').replace(/&#39;|&#x27;|&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}

class Artboard {
  constructor(file) {
    this.file = file;
    this.folder = path.dirname(file);
    const html = fs.readFileSync(file, 'utf8');
    const open = html.indexOf('<x-dc>');
    const close = html.lastIndexOf('</x-dc>');
    const template = open >= 0 && close > open ? html.slice(open + '<x-dc>'.length, close) : '';
    this.tree = parseTemplate(template.replace(/<helmet>[\s\S]*?<\/helmet>/g, '').replace(/<!--[\s\S]*?-->/g, ''));
    this.scripts = [...html.matchAll(/<script\b[^>]*?\bsrc\s*=\s*"([^"]+)"[^>]*>/g)].map((found) => found[1]);
    const logic = html.match(/<script\b([^>]*\btype="text\/x-dc"[^>]*)>([\s\S]*?)<\/script>/);
    this.code = logic ? logic[2] : '';
    this.defaults = {};
    const declared = logic && logic[1].match(/data-props='([^']*)'/);
    if (declared) {
      for (const [name, editor] of Object.entries(JSON.parse(declared[1]))) {
        if (editor && typeof editor === 'object' && 'default' in editor) this.defaults[name] = editor.default;
      }
    }
    this.imports = [...template.matchAll(/<dc-import\b[^>]*\bname="([^"]+)"/g)].map((found) => found[1]);
  }

  importedFile(name) {
    const file = path.join(this.folder, `${name}.dc.html`);
    if (!fs.existsSync(file)) throw new Error(`${path.basename(this.file)} dc-imports ${name}, and no ${name}.dc.html is beside it`);
    return file;
  }

  // The scripts this artboard loads that the walk runs: its own local files, never a remote one, the canvas's
  // support.js, or a React of its own, which the walk supplies.
  localScripts() {
    return this.scripts.filter((src) => !/^(https?:)?\/\//.test(src)).flatMap((src) => {
      const file = path.resolve(this.folder, src.split(/[?#]/)[0]);
      const name = path.basename(file).toLowerCase();
      if (name === 'support.js' || /^react(-dom)?([.-].*)?\.js$/.test(name)) return [];
      if (!fs.existsSync(file)) throw new Error(`${path.basename(this.file)} loads ${src}, which is not in the canvas`);
      return [file];
    });
  }
}

// ---- one render: a fresh context, the scripts, the screen built, mounted, settled, drawn ----------------------
const compiled = new Map();
const artboards = new Map();

function artboardAt(file) {
  if (!artboards.has(file)) artboards.set(file, new Artboard(file));
  return artboards.get(file);
}

function fakeElement() {
  const noop = () => {};
  return {
    style: {}, dataset: {}, children: [], childNodes: [], textContent: '', innerHTML: '', value: '',
    classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    setAttribute: noop, getAttribute: () => null, removeAttribute: noop, hasAttribute: () => false,
    appendChild: (child) => child, removeChild: noop, insertBefore: (child) => child, append: noop, remove: noop,
    addEventListener: noop, removeEventListener: noop, dispatchEvent: noop, focus: noop, blur: noop, click: noop, scrollIntoView: noop,
    querySelector: () => null, querySelectorAll: () => [], closest: () => null, contains: () => false,
    getBoundingClientRect: () => ({ top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0, x: 0, y: 0 }),
  };
}

function makeContext(clock) {
  const noop = () => {};
  const storage = { getItem: () => null, setItem: noop, removeItem: noop, clear: noop, key: () => null, length: 0 };
  class Observer { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
  const document = Object.assign(fakeElement(), {
    createElement: fakeElement, createElementNS: fakeElement, createTextNode: fakeElement, getElementById: () => null,
    getElementsByTagName: () => [], getElementsByClassName: () => [], body: fakeElement(), head: fakeElement(),
    documentElement: fakeElement(), readyState: 'complete', cookie: '', currentScript: null, activeElement: null,
  });
  const sandbox = {
    console, document, localStorage: storage, sessionStorage: storage,
    location: { hash: '', href: 'https://canvas.local/', search: '', pathname: '/', origin: 'https://canvas.local', reload: noop, assign: noop, replace: noop },
    history: { pushState: noop, replaceState: noop, back: noop, forward: noop, go: noop, state: null, length: 1 },
    navigator: { userAgent: 'story-canvas-walk', language: 'en', languages: ['en'], clipboard: { writeText: () => Promise.resolve() } },
    addEventListener: noop, removeEventListener: noop, dispatchEvent: noop, scrollTo: noop, scrollBy: noop, open: noop, alert: noop,
    confirm: () => false, prompt: () => null, getComputedStyle: () => ({ getPropertyValue: () => '' }),
    matchMedia: () => ({ matches: false, addEventListener: noop, removeEventListener: noop, addListener: noop, removeListener: noop }),
    innerWidth: 1280, innerHeight: 900, devicePixelRatio: 1,
    MutationObserver: Observer, ResizeObserver: Observer, IntersectionObserver: Observer,
    Event: class { constructor(type) { this.type = type; } }, CustomEvent: class { constructor(type, init) { this.type = type; this.detail = init && init.detail; } },
    fetch: () => Promise.reject(new Error('the walk renders screens without a network')),
    URL, URLSearchParams, TextEncoder, TextDecoder, structuredClone, queueMicrotask,
    setTimeout: (...args) => clock.setTimeout(...args), clearTimeout: (id) => clock.clear(id),
    setInterval: (...args) => clock.setInterval(...args), clearInterval: (id) => clock.clear(id),
    requestAnimationFrame: (callback) => clock.setTimeout(() => callback(clock.now), 16), cancelAnimationFrame: (id) => clock.clear(id),
    performance: { now: () => clock.now },
  };
  sandbox.window = sandbox; sandbox.self = sandbox; sandbox.top = sandbox; sandbox.parent = sandbox;
  sandbox.React = makeReact();
  sandbox.ReactDOM = { createPortal: (children) => children, createRoot: () => ({ render: noop, unmount: noop }), render: noop, flushSync: (run) => run && run() };
  vm.createContext(sandbox);
  vm.runInContext(`class DCLogic {
  constructor(props) { this.props = props || {}; this.state = null; }
  setState(next, done) { const part = typeof next === 'function' ? next(this.state || {}, this.props) : next; this.state = Object.assign({}, this.state || {}, part); if (done) done(); }
  forceUpdate(done) { if (done) done(); }
}
globalThis.DCLogic = DCLogic;`, sandbox);
  return sandbox;
}

function loadScripts(context, file, loaded) {
  const artboard = artboardAt(file);
  for (const script of artboard.localScripts()) {
    if (loaded.has(script)) continue;
    loaded.add(script);
    if (!compiled.has(script)) compiled.set(script, new vm.Script(fs.readFileSync(script, 'utf8'), { filename: script }));
    compiled.get(script).runInContext(context);
  }
  for (const name of artboard.imports) loadScripts(context, artboard.importedFile(name), loaded);
}

class Screen {
  constructor(context, file) {
    this.context = context;
    this.instances = [];
    this.classes = new Map();
    this.created = [];
    this.file = file;
  }

  componentClass(file) {
    if (!this.classes.has(file)) {
      const make = vm.runInContext(`(function (DCLogic) {\n${artboardAt(file).code}\n;return Component;\n})`, this.context, { filename: file });
      this.classes.set(file, make(this.context.DCLogic));
    }
    return this.classes.get(file);
  }

  // The DCLogic at the place'th dc component of this pass: the one made on an earlier pass, given these props, else a
  // new one, which mounts after the pass.
  instance(file, props, place) {
    const kept = this.instances[place];
    if (kept && kept.file === file) { kept.logic.props = props; return kept.logic; }
    const Component = this.componentClass(file);
    const logic = new Component(props);
    logic.props = props;
    this.instances[place] = { file, logic };
    this.created.push(logic);
    return logic;
  }

  element(file, props) {
    this.place = 0;
    return this.dcElement(file, props);
  }

  dcElement(file, given) {
    const artboard = artboardAt(file);
    const props = Object.assign({}, artboard.defaults, given);
    const logic = this.instance(file, props, this.place);
    this.place += 1;
    const vals = artboard.code ? logic.renderVals() : {};
    return this.build(artboard.tree, Object.assign({}, vals), file, 'r');
  }

  // The text the screen shows once every DCLogic it builds has mounted and settled: each pass builds the screen,
  // mounts the DCLogic made on it, and lets the clock run, until a pass makes none.
  async render(props, clock) {
    for (let pass = 0; pass < 4; pass += 1) {
      this.created = [];
      this.element(this.file, props);
      if (!this.created.length) break;
      for (const logic of this.created) if (typeof logic.componentDidMount === 'function') logic.componentDidMount();
      await clock.settle();
    }
    const out = new TextOut();
    draw(this.element(this.file, props), out);
    return out.text();
  }

  value(scope, written) {
    if (typeof written !== 'string') return written;
    const whole = /^\{\{\s*([^}]*?)\s*\}\}$/.exec(written);
    if (whole) return lookup(scope, whole[1]);
    return decode(written.replace(/\{\{\s*([^}]*?)\s*\}\}/g, (_, expression) => {
      const found = lookup(scope, expression);
      return found === undefined || found === null || typeof found === 'object' || typeof found === 'function' ? '' : String(found);
    }));
  }

  build(node, scope, file, key) {
    const React = this.context.React;
    if (typeof node === 'string') {
      const parts = [];
      let last = 0;
      const expression = /\{\{\s*([^}]*?)\s*\}\}/g;
      let found;
      while ((found = expression.exec(node))) {
        parts.push(decode(node.slice(last, found.index)));
        const value = lookup(scope, found[1]);
        if (value !== undefined && value !== null && typeof value !== 'boolean' && typeof value !== 'function') {
          parts.push(typeof value === 'object' && !React.isValidElement(value) && !Array.isArray(value) ? '' : value);
        }
        last = expression.lastIndex;
      }
      parts.push(decode(node.slice(last)));
      return parts;
    }
    const kids = (inner) => node.kids.map((kid, index) => this.build(kid, inner, file, `${key}.${index}`));
    if (node.tag === '#root') return React.createElement(React.Fragment, null, kids(scope));
    if (node.tag === 'sc-if') {
      const shown = this.value(scope, node.attrs.value);
      return shown && !(Array.isArray(shown) && !shown.length) ? React.createElement(React.Fragment, null, kids(scope)) : null;
    }
    if (node.tag === 'sc-for') {
      const list = [].concat(this.value(scope, node.attrs.list) || []);
      return React.createElement(React.Fragment, null, list.map((item, index) => kids(Object.assign({}, scope, { [node.attrs.as]: item, index }))));
    }
    if (node.tag === 'x-import') {
      const name = node.attrs['component-from-global-scope'];
      const component = String(name).split('.').reduce((held, part) => (held === undefined || held === null ? undefined : held[part]), this.context);
      if (!component) throw new Error(`${path.basename(file)} imports ${name}, which no script it loads defines`);
      return React.createElement(component, this.props(node.attrs, scope, ['component-from-global-scope']), ...kids(scope));
    }
    if (node.tag === 'dc-import') {
      const imported = artboardAt(file).importedFile(node.attrs.name);
      return this.dcElement(imported, this.props(node.attrs, scope, ['name', 'style']));
    }
    if (SILENT.has(node.tag)) return null;
    const props = {};
    for (const [name, written] of Object.entries(node.attrs)) {
      if (/^hint-/.test(name)) continue;
      props[name === 'class' ? 'className' : name] = this.value(scope, written);
    }
    return React.createElement(node.tag, props, ...kids(scope));
  }

  props(attrs, scope, leftOut) {
    const props = {};
    for (const [name, written] of Object.entries(attrs)) {
      if (leftOut.includes(name) || /^hint-/.test(name)) continue;
      props[name.replace(/-([a-z0-9])/g, (_, letter) => letter.toUpperCase())] = this.value(scope, written);
    }
    return props;
  }
}

function lookup(scope, expression) {
  const written = expression.trim();
  if (written === 'true') return true;
  if (written === 'false') return false;
  if (written === 'null') return null;
  if (/^-?\d+(\.\d+)?$/.test(written)) return Number(written);
  if (/^(['"]).*\1$/.test(written)) return written.slice(1, -1);
  return written.split('.').reduce((held, part) => (held === undefined || held === null ? undefined : held[part.trim()]), scope);
}

async function run(job) {
  const clock = new Clock();
  const context = makeContext(clock);
  loadScripts(context, job.artboard, new Set());
  const screen = new Screen(context, job.artboard);
  const props = Object.assign({}, job.props, { go: () => {} });
  const text = await screen.render(props, clock);
  if (clock.errors.length) throw clock.errors[0];
  return text;
}

async function main() {
  const { jobs } = JSON.parse(fs.readFileSync(0, 'utf8'));
  const results = [];
  for (const job of jobs) {
    try {
      results.push({ text: await run(job) });
    } catch (problem) {
      results.push({ error: String((problem && problem.message) || problem) });
    }
  }
  process.stdout.write(JSON.stringify(results));
}

main().catch((problem) => { process.stderr.write(String((problem && problem.stack) || problem)); process.exit(1); });
