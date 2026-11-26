// React's automatic JSX runtime (what React 17+ compiles JSX to), answered with the canvas's createElement, so a view
// compiled for React 19 runs on the canvas's React 18.
var React = window.React;

function element(type, props, key, spreadChildren) {
  var given = props || {};
  var rest = {};
  for (var name in given) if (name !== 'children') rest[name] = given[name];
  if (key !== undefined) rest.key = key;
  var children = given.children;
  if (children === undefined) return React.createElement(type, rest);
  // jsxs marks children the compiler wrote side by side, which need no keys: hand them over one by one.
  if (spreadChildren && Array.isArray(children)) return React.createElement.apply(null, [type, rest].concat(children));
  return React.createElement(type, rest, children);
}

function jsx(type, props, key) { return element(type, props, key, false); }
function jsxs(type, props, key) { return element(type, props, key, true); }

module.exports = { jsx: jsx, jsxs: jsxs, jsxDEV: jsx, Fragment: React.Fragment };
