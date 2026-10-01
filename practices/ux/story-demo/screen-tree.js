/**
 * Explorer tree: epic → sub-epic → screen → story → scenario → step.
 * A screen sits on the epic when that epic has no sub-epic.
 * The current screen's epic, sub-epic, and screen start expanded.
 */

export function epicKey(name) {
  return `epic:${name}`;
}

export function subEpicKey(epic, name) {
  return `subepic:${epic}/${name}`;
}

export function screenKey(name, epic = "", sub = "") {
  return epic ? `screen:${epic}/${sub}/${name}` : `screen:${name}`;
}

export function storyKey(screen, story) {
  return `story:${screen}/${story}`;
}

export function scenarioKey(screen, story, scenario) {
  return `scenario:${screen}/${story}/${scenario}`;
}

export function storyNamesOnScreen(screenEl) {
  const raw =
    screenEl.getAttribute("data-stories") ||
    screenEl.getAttribute("data-for-story") ||
    "";
  return raw
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
}

/**
 * @param {Element[]} screenEls
 * @param {{ title?: string, story?: { name?: string, scenarios?: object[] } }[]} catalog
 */
export function buildScreenNodes(screenEls, catalog) {
  return screenEls.map((el) => {
    const name =
      el.getAttribute("data-slug") ||
      el.querySelector("h2")?.textContent?.trim() ||
      "";
    const stories = storyNamesOnScreen(el).map((storyName) => {
      const storyIndex = catalog.findIndex(
        (entry) => entry.title === storyName || entry.story?.name === storyName,
      );
      const entry = storyIndex >= 0 ? catalog[storyIndex] : null;
      const scenarios = (entry?.story?.scenarios ?? []).map((sc, scenarioIndex) => ({
        name: sc.name,
        scenarioIndex,
        steps: (sc.steps ?? []).map((step) => ({
          kind: step.kind,
          label: step.label,
        })),
      }));
      return { name: storyName, storyIndex, scenarios };
    });
    return { name, stories };
  });
}

/**
 * Place screens under the story-map outline.
 * A group with a name is a sub-epic. A group without one hangs its screens on the epic.
 * Groups with no matching screen are left off the tree.
 * @param {{ name: string, stories?: object[] }[]} screens
 * @param {{ name: string, groups?: { name?: string, stories?: string[] }[], stories?: string[] }[]} outline
 */
export function nestScreens(screens, outline) {
  const screenNodes = screens.map(toScreenNode);
  if (!outline?.length) return screenNodes;
  const epics = [];
  for (const epic of outline) {
    const children = [];
    for (const group of epic.groups || []) {
      const placed = placeScreens(screenNodes, group.stories || [], epic.name, group.name || "");
      if (!placed.length) continue;
      if (group.name) {
        children.push({
          kind: "subepic",
          name: group.name,
          key: subEpicKey(epic.name, group.name),
          children: placed,
        });
      } else {
        children.push(...placed);
      }
    }
    if (epic.stories?.length) {
      children.push(...placeScreens(screenNodes, epic.stories, epic.name, ""));
    }
    if (!children.length) continue;
    epics.push({
      kind: "epic",
      name: epic.name,
      key: epicKey(epic.name),
      children,
    });
  }
  return epics.length ? epics : screenNodes;
}

/** Keys to open so the named screen is visible: epic, sub-epic, and the screen. */
export function keysForCurrentScreen(nodes, screenName) {
  let match = null;
  function walk(node, trail) {
    if (match || !node || node.kind === "step") return;
    const next = node.key ? [...trail, node.key] : trail;
    if (node.kind === "screen" && node.name === screenName) {
      match = next;
      return;
    }
    for (const child of node.children || []) walk(child, next);
  }
  for (const node of nodes || []) walk(node, []);
  return match || [];
}

function toScreenNode(screen) {
  return {
    kind: "screen",
    name: screen.name,
    key: screenKey(screen.name),
    children: (screen.stories || []).map((story) => storyToNode(screen.name, story)),
  };
}

function storyToNode(screenName, story) {
  return {
    kind: "story",
    name: story.name,
    screenName,
    key: storyKey(screenName, story.name),
    storyIndex: story.storyIndex ?? -1,
    children: (story.scenarios || []).map((scenario, index) => {
      const key = scenarioKey(screenName, story.name, scenario.name);
      return {
        kind: "scenario",
        name: scenario.name,
        screenName,
        key,
        storyName: story.name,
        storyIndex: story.storyIndex ?? -1,
        scenarioIndex: scenario.scenarioIndex ?? index,
        children: (scenario.steps || []).map((step) => ({
          kind: "step",
          screenName,
          stepKind: step.kind,
          label: step.label,
          storyIndex: story.storyIndex ?? -1,
          scenarioIndex: scenario.scenarioIndex ?? index,
          scenarioKey: key,
        })),
      };
    }),
  };
}

function placeScreens(screenNodes, storyNames, epicName, subName) {
  const order = new Map(storyNames.map((name, index) => [name, index]));
  const placed = [];
  for (const screen of screenNodes) {
    const stories = (screen.children || [])
      .filter((story) => order.has(story.name))
      .sort((a, b) => order.get(a.name) - order.get(b.name));
    if (!stories.length) continue;
    placed.push({
      rank: Math.min(...stories.map((story) => order.get(story.name))),
      node: {
        kind: "screen",
        name: screen.name,
        key: screenKey(screen.name, epicName, subName),
        children: stories,
      },
    });
  }
  placed.sort((a, b) => a.rank - b.rank);
  return placed.map((item) => item.node);
}

function twistButton(expanded, key, onToggle, onSelect) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "twist";
  button.setAttribute("aria-expanded", expanded ? "true" : "false");
  button.setAttribute("aria-label", expanded ? "Collapse" : "Expand");
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    onSelect?.();
    onToggle(key);
  });
  return button;
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

const DOMAIN_NOUNS = [
  "My Paradise",
  "Mavenir shopping cart",
  "Apple Pay",
  "Mavenir",
  "Cognito",
  "Vouchera",
  "Persona",
  "Twilio",
  "Zendesk",
  "MSISDN",
  "Customer",
  "User",
];

function appendNouns(fragment, text) {
  const pattern = new RegExp(
    DOMAIN_NOUNS.map((noun) => noun.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|"),
    "gi",
  );
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

function stepLabel(label) {
  const fragment = document.createDocumentFragment();
  const marked = /\+\+([^+]+)\+\+/g;
  let cursor = 0;
  let match = marked.exec(label);
  while (match) {
    if (match.index > cursor) appendNouns(fragment, label.slice(cursor, match.index));
    const noun = document.createElement("u");
    noun.textContent = match[1];
    fragment.appendChild(noun);
    cursor = match.index + match[0].length;
    match = marked.exec(label);
  }
  if (cursor < label.length) appendNouns(fragment, label.slice(cursor));
  return fragment;
}

function labelButton(text, className, kind, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `node-label ${className}`;
  const kindName = KIND_LABEL[kind] || kind;
  button.title = kindName;
  button.setAttribute("aria-label", `${kindName} ${text}`);
  button.appendChild(glyph(kind));
  const span = document.createElement("span");
  span.textContent = text;
  button.appendChild(span);
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    onClick();
  });
  return button;
}

function childList(expanded, nodes) {
  const list = document.createElement("ul");
  if (!expanded) list.hidden = true;
  for (const node of nodes) list.appendChild(node);
  return list;
}

const EMPTY = {
  screen: "No story on this screen",
  story: "No scenarios recorded",
  scenario: "No steps recorded",
};

/** Scroll the explorer panel so the screen row for `screenName` is visible. */
export function scrollExplorerToScreen(container, screenName) {
  if (!container || !screenName) return;
  const scrollRoot = container.closest("#explorer-frame");
  const node = [...container.querySelectorAll("li.screen-node")].find(
    (li) => li.dataset.screen === screenName,
  );
  if (!node) return;
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

/**
 * @param {HTMLElement} container
 * @param {{ nodes?: object[], screens?: object[], outline?: object[], expanded: Set<string>, currentScreen?: string, currentStory?: string, currentScenario?: string, currentStep?: { kind?: string, label?: string }, scrollToCurrentScreen?: boolean }} model
 * @param {{ onToggle: (key: string) => void, onScreen: (name: string) => void, onStory: (storyIndex: number, name: string) => void, onScenario: (storyIndex: number, scenarioIndex: number, key: string) => void }} handlers
 */
export function renderScreenTree(container, model, handlers) {
  container.innerHTML = "";
  const nodes = model.nodes || nestScreens(model.screens || [], model.outline || []);
  for (const node of nodes) container.appendChild(renderBranch(node, model, handlers, false, ""));
  if (model.scrollToCurrentScreen && model.currentScreen) {
    scrollExplorerToScreen(container, model.currentScreen);
  }
}

function renderBranch(node, model, handlers, activeScenario, owningScreen) {
  if (node.kind === "step") return renderStep(node, model, handlers, activeScenario, owningScreen || node.screenName || "");
  const screenName = node.kind === "screen" ? node.name : (owningScreen || node.screenName || "");
  const selectScreen = () => {
    if (screenName) handlers.onScreen?.(screenName);
  };
  const open = model.expanded.has(node.key);
  const li = document.createElement("li");
  li.className = `${node.kind}-node`;
  if (screenName) li.dataset.owningScreen = screenName;
  if (node.kind === "screen") li.dataset.screen = node.name;
  if (isCurrent(node, model)) li.classList.add("current");
  li.appendChild(twistButton(open, node.key, handlers.onToggle, selectScreen));
  li.appendChild(
    labelButton(node.name, `${node.kind}-label`, node.kind, () => {
      if (!open) handlers.onToggle(node.key);
      if (node.kind === "story") handlers.onStory(node.storyIndex ?? -1, node.name);
      if (node.kind === "scenario") {
        handlers.onScenario(node.storyIndex ?? -1, node.scenarioIndex ?? -1, node.key);
      }
      selectScreen();
    }),
  );
  const children = (node.children || []).filter((child) => child.kind !== "step" || node.kind === "scenario");
  const scenarioOpen = node.kind === "scenario" && isCurrent(node, model);
  const body = children.length
    ? children.map((child) => renderBranch(child, model, handlers, scenarioOpen, screenName))
    : EMPTY[node.kind]
      ? [emptyItem(EMPTY[node.kind])]
      : [];
  if (body.length) li.appendChild(childList(open, body));
  return li;
}

function isCurrent(node, model) {
  if (node.kind === "screen") return node.name === model.currentScreen;
  if (node.kind === "story") return node.name === model.currentStory;
  if (node.kind === "scenario") {
    return node.name === model.currentScenario && (!model.currentStory || node.storyName === model.currentStory);
  }
  return false;
}

function renderStep(step, model, handlers, activeScenario, owningScreen) {
  const screenName = owningScreen || step.screenName || "";
  const stepLi = document.createElement("li");
  stepLi.className = "step";
  stepLi.title = KIND_LABEL.step;
  if (screenName) stepLi.dataset.owningScreen = screenName;
  stepLi.tabIndex = 0;
  stepLi.addEventListener("click", () => {
    handlers.onScenario?.(step.storyIndex ?? -1, step.scenarioIndex ?? -1, step.scenarioKey);
    if (screenName) handlers.onScreen?.(screenName);
  });
  const kind = document.createElement("span");
  kind.className = "step-kind";
  if (step.stepKind === "when" || step.stepKind === "then") kind.classList.add("emph");
  kind.textContent = step.stepKind;
  stepLi.appendChild(kind);
  stepLi.appendChild(document.createTextNode(" "));
  stepLi.appendChild(stepLabel(step.label));
  const current = model.currentStep;
  if (
    activeScenario &&
    current &&
    current.kind === step.stepKind &&
    current.label === step.label
  ) {
    stepLi.classList.add("current");
  }
  return stepLi;
}

function emptyItem(text) {
  const li = document.createElement("li");
  li.className = "empty";
  li.textContent = text;
  return li;
}
