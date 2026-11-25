// Keep a product's stylesheet inside the screen it draws on the design canvas. A canvas screen is a frame inside the
// canvas page, beside the story explorer's own panel, so the product's rules must neither read the browser window nor
// reach the page around the frame:
//
// - every selector is scoped to the frame (`.canvas-screen`); `:root`, `html` and `body` become the frame itself, so
//   the design tokens and the page's base rules land on the screen and nowhere else;
// - an `@media` rule that asks only about width or height becomes an `@container` rule on the frame, so the screen
//   draws its phone layout in a phone-wide frame inside a wide window; any other media rule stays as it is;
// - `vw` becomes `cqw`, the frame's width;
// - the frame contains its fixed and absolute children (`contain: layout paint`), so a sheet or a backdrop the
//   product fixes to the window covers the screen, not the explorer.
//
// A stylesheet that must keep its own selectors, such as a ported prototype's design system whose tokens answer to
// `:root` and `[data-theme="dark"]` on the page, takes only the size conversion (`containerCss`): its width and height
// media rules become container rules on the frame and `vw` becomes `cqw`, and every selector stays as written.
import { pathToFileURL } from 'node:url';

const FRAME = '.canvas-screen';
const CONTAINER = 'canvas-screen';
const UNSCOPED_AT_RULES = /^@(font-face|keyframes|-webkit-keyframes|property|page|counter-style|font-feature-values|import|charset|namespace)\b/i;
const GROUPING_AT_RULES = /^@(media|supports|container|layer|document)\b/i;
const SIZE_FEATURE = /\(\s*(min-|max-)?(width|height|aspect-ratio)\s*[:<>=]/i;
const OTHER_FEATURE = /\(\s*(?!(min-|max-)?(width|height|aspect-ratio)\s*[:<>=])[a-z-]+/i;

const FRAME_RULE = `${FRAME}{container:${CONTAINER} / inline-size;contain:layout paint;position:relative;min-height:100%}`;

// Split at the top level only: commas inside :is(...) or [attr="a,b"] stay where they are.
function splitTopLevel(text, separator) {
  const parts = [];
  let depth = 0;
  let quote = null;
  let start = 0;
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quote) { if (character === quote) quote = null; continue; }
    if (character === '"' || character === "'") quote = character;
    else if (character === '(' || character === '[') depth += 1;
    else if (character === ')' || character === ']') depth -= 1;
    else if (character === separator && depth === 0) { parts.push(text.slice(start, index)); start = index + 1; }
  }
  parts.push(text.slice(start));
  return parts;
}

export function scopeSelector(selector) {
  const written = selector.trim();
  if (!written) return written;
  if (written.startsWith(FRAME)) return written;
  const page = /^(:root|html|body)(?![\w-])/i.exec(written);
  if (page) {
    const rest = written.slice(page[0].length);
    const nested = /^\s+(:root|html|body)(?![\w-])/i.exec(rest);
    return `${FRAME}${nested ? rest.slice(nested[0].length) : rest}`;
  }
  return `${FRAME} ${written}`;
}

function scopeSelectors(selectors) {
  return splitTopLevel(selectors, ',').map(scopeSelector).join(',');
}

function containerQuery(prelude) {
  const query = prelude.replace(/^@media\s+/i, '').replace(/^(only\s+)?(screen|all)\s+and\s+/i, '');
  if (!SIZE_FEATURE.test(query) || OTHER_FEATURE.test(query) || /^(only\s+)?(print|screen|all)\b/i.test(query)) return null;
  return `@container ${CONTAINER} ${query}`;
}

function scopeDeclarations(declarations) {
  return declarations.replace(/(\d*\.?\d+)vw\b/g, '$1cqw');
}

// The end of the block that opens at text[open] ('{'), past strings and nested blocks.
function blockEnd(text, open) {
  let depth = 0;
  let quote = null;
  for (let index = open; index < text.length; index += 1) {
    const character = text[index];
    if (quote) { if (character === quote && text[index - 1] !== '\\') quote = null; continue; }
    if (character === '"' || character === "'") quote = character;
    else if (character === '{') depth += 1;
    else if (character === '}') { depth -= 1; if (depth === 0) return index; }
  }
  return text.length - 1;
}

function rewriteRules(text, scoped) {
  let out = '';
  let index = 0;
  while (index < text.length) {
    const open = text.indexOf('{', index);
    const semicolon = text.indexOf(';', index);
    if (open < 0) { out += text.slice(index); break; }
    if (semicolon >= 0 && semicolon < open && text.slice(index, semicolon).trim().startsWith('@')) {
      out += text.slice(index, semicolon + 1);
      index = semicolon + 1;
      continue;
    }
    const prelude = text.slice(index, open).trim();
    const close = blockEnd(text, open);
    const body = text.slice(open + 1, close);
    out += rewriteRule(prelude, body, scoped);
    index = close + 1;
  }
  return out;
}

function rewriteRule(prelude, body, scoped) {
  if (UNSCOPED_AT_RULES.test(prelude)) return `${prelude}{${body}}`;
  if (/^@media\b/i.test(prelude)) return `${containerQuery(prelude) || prelude}{${rewriteRules(body, scoped)}}`;
  if (GROUPING_AT_RULES.test(prelude)) return `${prelude}{${rewriteRules(body, scoped)}}`;
  if (prelude.startsWith('@')) return `${prelude}{${body}}`;
  return `${scoped ? scopeSelectors(prelude) : prelude}{${scopeDeclarations(body)}}`;
}

function withoutComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, '');
}

// The product's stylesheet kept inside the frame: selectors scoped, size media rules on the frame, the frame's rule first.
export function scopeCss(css) {
  return `${FRAME_RULE}
${rewriteRules(withoutComments(css), true)}`;
}

// The size conversion alone: width and height media rules on the frame, `vw` as `cqw`, selectors as written.
export function containerCss(css) {
  return rewriteRules(withoutComments(css), false);
}

// Run as `node scope-css.mjs --container`: reads a JSON list of stylesheets on standard input and writes the list
// converted by containerCss, in the same order, to standard output.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href && process.argv.includes('--container')) {
  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (chunk) => { input += chunk; });
  process.stdin.on('end', () => { process.stdout.write(JSON.stringify(JSON.parse(input).map(containerCss))); });
}
