/**
 * Explorer tree: epic → sub-epic → screen → story → scenario → step.
 * The UX map writes the tree into the mockup page (#story-explorer-tree): where each screen sits, which stories and
 * scenarios it holds, and the keys that open each screen. This module only draws it.
 * The current screen's epic, sub-epic, and screen start expanded.
 */

/**
 * The tree the mockup page carries: `{ nodes, screenKeys }`.
 * A page with no tree, or a tree that is not JSON, raises: the page was not rendered from a UX map.
 * @param {ParentNode} root
 */
export function readExplorerTree(root) {
  const el = root.querySelector("#story-explorer-tree");
  if (!el) throw new Error("This mockup carries no #story-explorer-tree; render the UX map to HTML again.");
  return JSON.parse(el.textContent);
}

const SVG = "http://www.w3.org/2000/svg";

function svgEl(name, attrs) {
  const el = document.createElementNS(SVG, name);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  return el;
}

function glyph(kind) {
  const svg = svgEl("svg", { viewBox: "0 0 16 16", class: "glyph", "aria-hidden": "true" });
  const add = (name, attrs) => svg.appendChild(svgEl(name, attrs));
  if (kind === "epic") {
    add("rect", { x: "1.5", y: "2", width: "13", height: "3", rx: "0.6" });
    add("rect", { x: "1.5", y: "6.5", width: "13", height: "3", rx: "0.6" });
    add("rect", { x: "1.5", y: "11", width: "13", height: "3", rx: "0.6" });
  } else if (kind === "subepic") {
    add("path", { d: "M1.5 5.5 H6 L7.4 3.5 H14.5 V13.5 H1.5 Z" });
  } else if (kind === "screen") {
    add("rect", { x: "2", y: "1.5", width: "12", height: "13", rx: "1" });
    add("path", { d: "M4 5 H12 M4 8 H12 M4 11 H9" });
  } else if (kind === "story") {
    add("path", { d: "M1.5 3.5 L8 5.2 V13.2 L1.5 11.5 Z M14.5 3.5 L8 5.2 V13.2 L14.5 11.5 Z" });
  } else if (kind === "scenario") {
    add("rect", { x: "3.2", y: "2.8", width: "9.6", height: "11", rx: "1" });
    add("path", { d: "M6 1.6 H10 V3.6 H6 Z M5.4 7 H11 M5.4 9.4 H11 M5.4 11.8 H8.6" });
  }
  return svg;
}

const KIND_LABEL = {
  epic: "Epic",
  subepic: "Sub-epic",
  screen: "Screen",
  story: "Story",
  scenario: "Scenario",
  step: "Step",
};

function nounPattern(terms) {
  return new RegExp(
    terms.map((term) => term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|"),
    "gi",
  );
}

// Underline the domain terms the model gives a step's screen (step.domainTerms); the page decides none itself.
function appendNouns(fragment, text, terms) {
  if (!terms.length) {
    fragment.appendChild(document.createTextNode(text));
    return;
  }
  const pattern = nounPattern(terms);
  let cursor = 0;
  let match = pattern.exec(text);
  while (match) {
    if (match.index > cursor) {
      fragment.appendChild(document.createTextNode(text.slice(cursor, match.index)));
    }
    const noun = document.createElement("u");
    noun.textContent = match[0];
    fragment.appendChild(noun);
    cursor = match.index + match[0].length;
    match = pattern.exec(text);
  }
  if (cursor < text.length) fragment.appendChild(document.createTextNode(text.slice(cursor)));
}

function stepLabel(label, terms) {
  const fragment = document.createDocumentFragment();
  const marked = /\+\+([^+]+)\+\+/g;
  let cursor = 0;
  let match = marked.exec(label);
  while (match) {
    if (match.index > cursor) appendNouns(fragment, label.slice(cursor, match.index), terms);
    const noun = document.createElement("u");
    noun.textContent = match[1];
    fragment.appendChild(noun);
    cursor = match.index + match[0].length;
    match = marked.exec(label);
  }
  if (cursor < label.length) appendNouns(fragment, label.slice(cursor), terms);
  return fragment;
}

function childList(expanded, nodes) {
  const list = document.createElement("ul");
  if (!expanded) list.hidden = true;
  for (const node of nodes) list.appendChild(node);
  return list;
}

function emptyItem(text) {
  const li = document.createElement("li");
  li.className = "empty";
  li.textContent = text;
  return li;
}

const EMPTY = {
  screen: "No story on this screen",
  story: "No scenarios recorded",
  scenario: "No steps recorded",
};

/**
 * Which tree nodes the explorer shows open, the screen it last opened because that screen became current,
 * and whether the next drawing should scroll that screen into view. One expansion outlives each story the
 * explorer loads, so what the person opened stays open.
 */
export class ScreenTreeExpansion {
  constructor() {
    this.openKeys = new Set();
    this.openScreen = null;
    this.scrollRequested = false;
  }

  isOpen(key) {
    return this.openKeys.has(key);
  }

  open(key) {
    this.openKeys.add(key);
    return this;
  }

  toggle(key) {
    if (this.openKeys.has(key)) this.openKeys.delete(key);
    else this.openKeys.add(key);
    return this;
  }

  /** Open the keys of `screenName` the first time it becomes the current screen. */
  followScreen(screenName, keys) {
    if (!screenName || this.openScreen === screenName) return this;
    this.openScreen = screenName;
    for (const key of keys || []) this.openKeys.add(key);
    return this;
  }

  /** Forget the followed screen, so the next current screen opens its keys again. */
  forgetOpenScreen() {
    this.openScreen = null;
    return this;
  }

  clear() {
    this.openKeys.clear();
    this.openScreen = null;
    return this;
  }

  requestScroll() {
    this.scrollRequested = true;
    return this;
  }

  /** Whether a scroll was requested since the last drawing; asking clears the request. */
  takeScrollRequest() {
    const requested = this.scrollRequested;
    this.scrollRequested = false;
    return requested;
  }
}

/**
 * Draws the explorer tree for one moment of the story demo.
 * `model`: `{ nodes, expansion: ScreenTreeExpansion, currentScreen?, currentStory?, currentScenario?, currentStep?, scrollToCurrentScreen? }`.
 * `handlers`: `{ onToggle(key), onScreen(name), onStory(storyName), onScenario(storyName, scenarioIndex, key) }`.
 */
export class ScreenTree {
  constructor(model, handlers) {
    this.model = model;
    this.handlers = handlers;
  }

  drawInto(container) {
    container.innerHTML = "";
    for (const node of this.model.nodes) container.appendChild(this._branch(node, false, ""));
    if (this.model.scrollToCurrentScreen && this.model.currentScreen) {
      this._scrollToScreen(container, this.model.currentScreen);
    }
    return container;
  }

  /** Scroll the explorer panel so the screen node for `screenName` is visible. */
  _scrollToScreen(container, screenName) {
    const node = [...container.querySelectorAll("li.screen-node")].find(
      (li) => li.dataset.screen === screenName,
    );
    if (!node) return;
    const scrollRoot = container.closest("#explorer-frame");
    requestAnimationFrame(() => {
      if (!scrollRoot) {
        node.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }
      const rootRect = scrollRoot.getBoundingClientRect();
      const nodeRect = node.getBoundingClientRect();
      const target =
        nodeRect.top - rootRect.top + scrollRoot.scrollTop - (rootRect.height - nodeRect.height) / 2;
      scrollRoot.scrollTo({ top: Math.max(0, target), behavior: "smooth" });
    });
  }

  _branch(node, activeScenario, owningScreen) {
    if (node.kind === "step") return this._step(node, activeScenario, owningScreen || node.screenName || "");
    const screenName = node.kind === "screen" ? node.name : (owningScreen || node.screenName || "");
    const selectScreen = () => {
      if (screenName) this.handlers.onScreen?.(screenName);
    };
    const open = this.model.expansion.isOpen(node.key);
    const li = this._branchItem(node, screenName);
    li.appendChild(this._twistButton(node, open, selectScreen));
    li.appendChild(this._labelButton(node, () => this._select(node, open, selectScreen)));
    const body = this._branchBody(node, screenName);
    if (body.length) li.appendChild(childList(open, body));
    return li;
  }

  _branchItem(node, screenName) {
    const li = document.createElement("li");
    li.className = `${node.kind}-node`;
    if (screenName) li.dataset.owningScreen = screenName;
    if (node.kind === "screen") li.dataset.screen = node.name;
    if (this._isCurrent(node)) li.classList.add("current");
    return li;
  }

  _select(node, open, selectScreen) {
    if (!open) this.handlers.onToggle(node.key);
    if (node.kind === "story") this.handlers.onStory(node.name);
    if (node.kind === "scenario") this.handlers.onScenario(node.storyName, node.scenarioIndex, node.key);
    selectScreen();
  }

  /** A node's drawn children: steps only under a scenario, or a note that the node holds nothing yet. */
  _branchBody(node, screenName) {
    const children = (node.children || []).filter((child) => child.kind !== "step" || node.kind === "scenario");
    const scenarioOpen = node.kind === "scenario" && this._isCurrent(node);
    if (children.length) return children.map((child) => this._branch(child, scenarioOpen, screenName));
    return EMPTY[node.kind] ? [emptyItem(EMPTY[node.kind])] : [];
  }

  _twistButton(node, open, selectScreen) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "twist";
    button.setAttribute("aria-expanded", open ? "true" : "false");
    button.setAttribute("aria-label", open ? "Collapse" : "Expand");
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      selectScreen();
      this.handlers.onToggle(node.key);
    });
    return button;
  }

  _labelButton(node, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `node-label ${node.kind}-label`;
    const kindName = KIND_LABEL[node.kind] || node.kind;
    button.title = kindName;
    button.setAttribute("aria-label", `${kindName} ${node.name}`);
    button.appendChild(glyph(node.kind));
    const span = document.createElement("span");
    span.textContent = node.name;
    button.appendChild(span);
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      onClick();
    });
    return button;
  }

  _isCurrent(node) {
    if (node.kind === "screen") return node.name === this.model.currentScreen;
    if (node.kind === "story") return node.name === this.model.currentStory;
    if (node.kind === "scenario") {
      return node.name === this.model.currentScenario
        && (!this.model.currentStory || node.storyName === this.model.currentStory);
    }
    return false;
  }

  _step(step, activeScenario, owningScreen) {
    const screenName = owningScreen || step.screenName || "";
    const stepLi = document.createElement("li");
    stepLi.className = "step";
    stepLi.title = KIND_LABEL.step;
    if (screenName) stepLi.dataset.owningScreen = screenName;
    stepLi.tabIndex = 0;
    stepLi.addEventListener("click", () => {
      this.handlers.onScenario?.(step.storyName, step.scenarioIndex, step.scenarioKey);
      if (screenName) this.handlers.onScreen?.(screenName);
    });
    stepLi.appendChild(this._stepKind(step));
    stepLi.appendChild(document.createTextNode(" "));
    stepLi.appendChild(stepLabel(step.label, step.domainTerms || []));
    if (activeScenario && this._isCurrentStep(step)) stepLi.classList.add("current");
    return stepLi;
  }

  _stepKind(step) {
    const kind = document.createElement("span");
    kind.className = "step-kind";
    if (step.stepKind === "when" || step.stepKind === "then") kind.classList.add("emph");
    kind.textContent = step.stepKind;
    return kind;
  }

  _isCurrentStep(step) {
    const current = this.model.currentStep;
    return Boolean(current && current.kind === step.stepKind && current.label === step.label);
  }
}
