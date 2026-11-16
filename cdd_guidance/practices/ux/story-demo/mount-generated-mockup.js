/**
 * # @toolset-manifest python -m tools manifest practices.ux.ux:Ux
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: practices.ux.ux:Ux
 * # invoke-check: action validate | toolset: practices.ux.ux:Ux
 *
 * Mount PlayDualRunner + explorer onto a UX-generated mockup shell.
 * Expects: #story-demo-frame (product), #explorer-frame chrome, [data-ux-story-ref] modules.
 * Multiple create{Story}Story exports → story picker (#story-list) + screens with data-for-story.
 * Serve from repo root so /practices/... imports resolve.
 */

import { StoryDemoControl } from "./control.js";
import { StoryDemoFrame } from "./story-demo-frame.js";
import { StoryDemoPage } from "./story-demo-page.js";
import { readExplorerTree, ScreenTree, ScreenTreeExpansion } from "./screen-tree.js";

/** How long the mount waits for composed fragments (`[data-include]`) to be inlined before it reads the page. */
const INCLUDE_WAIT_MILLISECONDS = 3000;
/** The mode each story function is collected in for the browser demo. */
const COLLECT_MODE = "fake";
/** Exposed domain values Interactive carries from one story to the next. */
const SESSION_KEYS = ["cart", "product", "catalog", "paymentMethod"];

function readBound(snapshot, path) {
  if (!path || snapshot == null) return undefined;
  return path.split(".").reduce((acc, key) => acc?.[key], snapshot);
}

/** List hosts are painted and wired from the scenario on every repaint, so they are not static controls or fields. */
function isBoundListHost(element) {
  return element.hasAttribute("data-bound-list") || element.getAttribute("data-type") === "bound-list";
}

function storyFunctionsIn(storyModule) {
  return Object.entries(storyModule)
    .filter(([exportName, exported]) => typeof exported === "function" && /^create.+Story$/.test(exportName))
    .map(([exportName, exported]) => ({ name: exportName, fn: exported }));
}

async function loadCreateStoryFns() {
  const fns = [];
  for (const script of document.querySelectorAll("[data-ux-story-ref]")) {
    const src = script.getAttribute("src");
    if (!src) continue;
    try {
      const storyModule = await import(new URL(src, document.baseURI).href);
      fns.push(...storyFunctionsIn(storyModule));
    } catch (err) {
      console.warn(`[story-demo] failed to load ${src}:`, err);
    }
  }
  return fns;
}

/** Fragments must be inlined before the controls are read (compose-fragments.js top-level await). */
function composedFragments(root) {
  if (!root.querySelector?.("[data-include]")) return Promise.resolve();
  return new Promise((resolve) => {
    const start = performance.now();
    const tick = () => {
      if (!root.querySelector("[data-include]") || performance.now() - start > INCLUDE_WAIT_MILLISECONDS) {
        resolve();
        return;
      }
      requestAnimationFrame(tick);
    };
    tick();
  });
}

function controlsOn(root) {
  return [...root.querySelectorAll("[data-story-steps], [data-bound-field]")]
    .filter((element) => !isBoundListHost(element))
    .map((element) => StoryDemoControl.fromElement(element))
    .filter(Boolean);
}

function explorerChromeOn(root) {
  return {
    storyMap: root.querySelector("[data-story-map]") || root.querySelector("#story-list"),
    storyMapToggle: root.querySelector("[data-toggle-story-map]"),
    tree: root.querySelector("[data-explorer-tree]"),
    message: root.querySelector("[data-explorer-message]"),
    playNext: root.querySelector("[data-play-next]"),
    reset: root.querySelector("[data-reset]"),
  };
}

/**
 * Fill `{name}` / `{product}` (and other `{field}`) in item story-step templates.
 * List hosts use `data-item-story-steps` (not `data-story-steps`) so reading the controls skips the container.
 */
function itemStoryStepsFor(lineItem, rawTemplate, pickedName) {
  if (!rawTemplate) return [];
  // The template is the step list the UX map wrote; one that does not read back is a defect to show, not hide.
  const template = JSON.parse(rawTemplate);
  if (!Array.isArray(template)) throw new Error(`data-item-story-steps holds no step list: ${rawTemplate}`);
  const name = pickedName ?? lineItem?.name ?? lineItem?.product ?? "";
  return template.map((step) => ({
    ...step,
    label: formatItemLabel(lineItem, String(step.label ?? ""), name),
  }));
}

function pickNameOf(lineItem, valueField) {
  if (valueField && lineItem?.[valueField] != null) return String(lineItem[valueField]);
  if (lineItem?.name != null) return String(lineItem.name);
  if (lineItem?.product != null) return String(lineItem.product);
  return "";
}

function formatItemLabel(lineItem, template, fallbackName = "") {
  if (template) {
    return template.replace(/\{(\w+)\}/g, (_, key) => {
      if (key === "name" || key === "product") {
        return lineItem?.[key] ?? fallbackName ?? "";
      }
      return lineItem?.[key] ?? "";
    });
  }
  if (lineItem?.product != null && lineItem?.quantity != null) {
    return `${lineItem.product} × ${lineItem.quantity} @ ${lineItem.unitPrice ?? ""}`;
  }
  const name = lineItem?.name ?? fallbackName;
  const price = lineItem?.unitPrice != null ? ` · ${lineItem.unitPrice}` : "";
  const category = lineItem?.category ? ` · ${lineItem.category}` : "";
  return `${name}${price}${category}`.trim();
}

/**
 * A list host on a screen (`data-bound-list`): it paints one line per item the scenario exposes at its path.
 * - data-item-story-steps ⇒ a line click runs When (action list)
 * - else data-set-input ⇒ a line click selects only (select list)
 */
class BoundListHost {
  constructor(element) {
    this.element = element;
  }

  get inputKey() {
    return this.element.getAttribute("data-set-input") || "product";
  }

  get valueField() {
    return this.element.getAttribute("data-item-value") || "";
  }

  get labelTemplate() {
    return this.element.getAttribute("data-item-label") || "";
  }

  get itemStepsTemplate() {
    return this.element.getAttribute("data-item-story-steps");
  }

  get destination() {
    return this.element.getAttribute("data-goto");
  }

  items(snapshot) {
    const path = this.element.getAttribute("data-bound-field") || this.element.getAttribute("data-bound-list") || "";
    if (!path || path === "true") return [];
    const direct = readBound(snapshot, path);
    return Array.isArray(direct) ? direct : [];
  }

  clear() {
    this.element.innerHTML = "";
    return this;
  }

  showEmpty() {
    const empty = document.createElement("div");
    empty.className = "field dimmed";
    empty.textContent = "(empty)";
    this.element.appendChild(empty);
    return this;
  }
}

/** One painted line of a list host, for one item the scenario exposed. */
class BoundListLine {
  constructor(host, lineItem) {
    this.host = host;
    this.lineItem = lineItem;
    this.pickedName = pickNameOf(lineItem, host.valueField);
    this.storySteps = itemStoryStepsFor(lineItem, host.itemStepsTemplate, this.pickedName);
    this.row = null;
  }

  paint(selectedName) {
    const row = document.createElement("div");
    row.className = "control";
    row.dataset.type = "list";
    row.dataset.name = this.pickedName;
    row.style.cursor = "pointer";
    row.setAttribute("data-set-input", this.host.inputKey);
    row.textContent = formatItemLabel(this.lineItem, this.host.labelTemplate, this.pickedName);
    if (this.pickedName && this.pickedName === selectedName) row.classList.add("selected");
    if (this.host.destination) row.setAttribute("data-goto", this.host.destination);
    if (this.storySteps.length) row.setAttribute("data-story-steps", JSON.stringify(this.storySteps));
    this.host.element.appendChild(row);
    this.row = row;
    return this;
  }

  get runsWhen() {
    return this.storySteps.length > 0;
  }

  control() {
    return new StoryDemoControl({
      name: this.pickedName,
      controlType: "list",
      label: this.row.textContent,
      storySteps: this.storySteps,
      element: this.row,
      fromBoundList: true,
    });
  }
}

/** The story functions the mockup loaded, in map order, with the story each one collects to. */
class StoryCatalog {
  constructor(entries) {
    this.entries = entries;
    /** When label → story index, so Interactive can jump to the story that owns a control's When. */
    this.whenStoryIndex = this._indexWhens();
  }

  static fromStoryFunctions(createStories) {
    return new StoryCatalog(createStories.map(({ name, fn }) => {
      const story = StoryDemoPage.load(fn, COLLECT_MODE, {}).story;
      return { createName: name, fn, title: story.name, story };
    }));
  }

  get titles() {
    return this.entries.map((entry) => entry.title);
  }

  get length() {
    return this.entries.length;
  }

  entry(storyIndex) {
    return this.entries[storyIndex];
  }

  /** The index of the story the explorer names: the loaded story function of that title. */
  indexNamed(name) {
    return this.entries.findIndex((entry) => entry.title === name || entry.story?.name === name);
  }

  storyIndexForWhen(whenLabel) {
    return this.whenStoryIndex.get(whenLabel);
  }

  _indexWhens() {
    const index = new Map();
    this.entries.forEach((entry, storyIndex) => {
      const steps = (entry.story.scenarios ?? []).flatMap((scenario) => scenario.steps ?? []);
      for (const step of steps) {
        if (step.kind === "when" && step.label) index.set(step.label, storyIndex);
      }
    });
    return index;
  }
}

function paintCharacterTree(character, root) {
  const tree = root.querySelector("[data-character-tree]");
  if (!tree || !character) return;
  tree.querySelectorAll(".tree-node:not([data-role='folder'])").forEach((node) => node.remove());
  const node = document.createElement("div");
  node.className = "tree-node selected";
  node.textContent = `· ${character.name || "Hero"}`;
  tree.appendChild(node);
}

function paintAbilities(character, root) {
  const list = root.querySelector("[data-ability-list]");
  if (!list || !character?.abilities) return;
  list.innerHTML = "";
  for (const [name, ability] of Object.entries(character.abilities)) {
    if (name === "pointContribution") continue;
    const row = document.createElement("div");
    row.className = "control";
    row.dataset.type = "list";
    row.dataset.name = name;
    row.textContent = `${name} · ${ability.rank ?? 0}`;
    list.appendChild(row);
  }
}

function boundFieldText(element, snapshot) {
  const path = element.getAttribute("data-bound-field");
  const boundValue = readBound(snapshot, path);
  const label = element.getAttribute("data-bound-label") || path;
  if (boundValue === undefined || boundValue === null) return `${label}: —`;
  if (typeof boundValue === "object") return `${label}: ${JSON.stringify(boundValue)}`;
  return `${label}: ${boundValue}`;
}

function paintBoundFields(snapshot, root) {
  root.querySelectorAll("[data-bound-field]").forEach((element) => {
    if (element.tagName === "BUTTON" || isBoundListHost(element)) return;
    element.textContent = boundFieldText(element, snapshot);
  });
}

function showScreensForStory(storyTitle, root) {
  const screens = [...root.querySelectorAll(".screen[data-for-story]")];
  if (!screens.length) return;
  let shownFirst = false;
  for (const screen of screens) {
    const allowed = screen
      .getAttribute("data-for-story")
      .split(",")
      .map((s) => s.trim());
    screen.classList.remove("current");
    if (!allowed.includes(storyTitle)) {
      screen.hidden = true;
      continue;
    }
    screen.hidden = shownFirst;
    if (!shownFirst) screen.classList.add("current");
    shownFirst = true;
  }
}

function showScreen(root, dest) {
  if (!dest) return;
  for (const screen of root.querySelectorAll(".screen")) {
    const title = screen.querySelector("h2")?.textContent?.trim();
    const slug = screen.getAttribute("data-slug");
    const match = title === dest || slug === dest;
    screen.hidden = !match;
    screen.classList.toggle("current", match);
  }
}

/** A click on one `clickable` selects it and clears the selection from the `siblings` in its region. */
function selectWithinRegion(root, clickable, siblings) {
  root.querySelectorAll(clickable).forEach((element) => {
    element.addEventListener("click", () => {
      const region = element.closest("[data-region]");
      region?.querySelectorAll(siblings).forEach((sibling) => sibling.classList.remove("selected"));
      element.classList.add("selected");
    });
  });
}

/** The explorer beside the product: the screen tree, or the story map when the page has no screens, and its message. */
class ExplorerPanel {
  /**
   * @param {GeneratedMockup} mockup
   * @param {ReturnType<typeof explorerChromeOn>} chrome
   * @param {ScreenTreeExpansion} expansion
   */
  constructor(mockup, chrome, expansion) {
    this.mockup = mockup;
    this.chrome = chrome;
    this.expansion = expansion;
    this._explorerTree = null;
  }

  /** Scroll the current screen into view on the next painting. */
  requestScroll() {
    this.expansion.requestScroll();
    return this;
  }

  /** The explorer tree the page carries, read the first time a screen is drawn. */
  get explorerTree() {
    this._explorerTree ??= readExplorerTree(this.mockup.root);
    return this._explorerTree;
  }

  paint() {
    const screens = [...this.mockup.root.querySelectorAll(".screen")];
    if (this.chrome.tree && !screens.length && this.mockup.page.story) this._paintStoryMap();
    else if (this.chrome.tree && screens.length) this._paintScreenTree(screens);
    this._paintMessage();
  }

  _paintScreenTree(screens) {
    const currentName = this._currentScreenName(screens);
    this.expansion.followScreen(currentName, this.explorerTree.screenKeys[currentName]);
    const scenario = this.mockup.page.runner.scenario;
    const model = {
      nodes: this.explorerTree.nodes,
      expansion: this.expansion,
      currentScreen: currentName,
      currentStory: this.mockup.page.story?.name ?? null,
      currentScenario: scenario?.name ?? null,
      currentStep: scenario?.currentStep ?? null,
      scrollToCurrentScreen: this.expansion.takeScrollRequest(),
    };
    new ScreenTree(model, this._treeHandlers()).drawInto(this.chrome.tree);
  }

  _currentScreenName(screens) {
    const current = screens.find((screen) => screen.classList.contains("current"))
      || screens.find((screen) => !screen.hidden);
    return current?.getAttribute("data-slug") || current?.querySelector("h2")?.textContent?.trim() || "";
  }

  _treeHandlers() {
    return {
      onToggle: (key) => {
        this.expansion.toggle(key);
        this.mockup.repaint();
      },
      onScreen: (name) => {
        showScreen(this.mockup.root, name);
        this.expansion.forgetOpenScreen().requestScroll();
        this.mockup.repaint();
      },
      onStory: (storyName) => {
        const storyIndex = this.mockup.catalog.indexNamed(storyName);
        if (storyIndex >= 0) this.mockup.activateStory(storyIndex);
      },
      onScenario: (storyName, scenarioIndex, key) => {
        this.expansion.open(key);
        this.mockup.openScenario(this.mockup.catalog.indexNamed(storyName), scenarioIndex);
      },
    };
  }

  _paintStoryMap() {
    const mapElement = this.chrome.storyMap || this.chrome.tree;
    if (!mapElement) return;
    const storyMap = this.mockup.page.explorerFrame.storyMap;
    this._paintStoryMapToggle(storyMap.expanded);
    mapElement.hidden = false;
    mapElement.innerHTML = "";
    for (const title of storyMap.visibleTitles()) mapElement.appendChild(this._storyMapItem(title, storyMap));
  }

  _paintStoryMapToggle(expanded) {
    const toggle = this.chrome.storyMapToggle;
    if (!toggle) return;
    toggle.textContent = expanded ? "▼" : "▶";
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    toggle.setAttribute("aria-label", expanded ? "Collapse story map" : "Expand story map");
  }

  _storyMapItem(title, storyMap) {
    const storyIndex = storyMap.titles.indexOf(title);
    const item = document.createElement("li");
    item.textContent = title;
    item.style.cursor = "pointer";
    if (title === storyMap.activeTitle) item.classList.add("current");
    item.addEventListener("click", () => {
      if (!storyMap.expanded) {
        storyMap.expand();
        this.mockup.repaint();
        return;
      }
      this.mockup.activateStory(storyIndex);
    });
    return item;
  }

  _paintMessage() {
    const messageElement = this.chrome.message;
    if (!messageElement) return;
    const message = this.mockup.page.explorerFrame.message;
    messageElement.hidden = !message;
    messageElement.textContent = message || "";
  }
}

/** The product frame: the scenario's exposed values painted into its fields, lists, and controls. */
class ProductPanel {
  /** @param {GeneratedMockup} mockup */
  constructor(mockup) {
    this.mockup = mockup;
  }

  paint() {
    const scenario = this.mockup.page.runner.scenario;
    const snapshot = scenario?.expose?.() ?? {};
    const character = readBound(snapshot, "character");
    paintCharacterTree(character, this.mockup.root);
    paintAbilities(character, this.mockup.root);
    this._paintBoundLists(snapshot);
    paintBoundFields(snapshot, this.mockup.root);
    if (scenario?.currentStep) this.mockup.frame.emphasize(scenario.currentStep);
    this.mockup.frame.paintEmphasis();
  }

  _paintBoundLists(snapshot) {
    this.mockup.frame.dropBoundListControls();
    for (const element of this.mockup.root.querySelectorAll("[data-bound-list]")) {
      this._paintBoundList(new BoundListHost(element), snapshot);
    }
  }

  _paintBoundList(host, snapshot) {
    const items = host.items(snapshot);
    host.clear();
    if (!items.length) {
      host.showEmpty();
      return;
    }
    const selectedName = this.mockup.page.runner.scenario?.input?.(host.inputKey, undefined)
      ?? readBound(snapshot, "product")?.name;
    for (const lineItem of items) this._paintBoundListLine(new BoundListLine(host, lineItem), selectedName);
  }

  _paintBoundListLine(line, selectedName) {
    line.paint(selectedName);
    if (line.runsWhen) {
      const control = line.control();
      this.mockup.frame.appendControl(control);
      this.mockup.wireInteractive(control);
    } else {
      this.mockup.wireLineSelect(line.row, line.pickedName, line.host.inputKey);
    }
  }
}

/** A UX-generated mockup page playing its stories: the product frame on the left, the explorer on the right. */
class GeneratedMockup {
  /**
   * @param {ParentNode} root
   * @param {StoryCatalog} catalog
   * @param {{ frame: StoryDemoFrame, chrome: ReturnType<typeof explorerChromeOn>, expansion: ScreenTreeExpansion }} parts
   */
  constructor(root, catalog, { frame, chrome, expansion }) {
    this.root = root;
    this.catalog = catalog;
    this.frame = frame;
    this.chrome = chrome;
    /** @type {StoryDemoPage | null} */
    this.page = null;
    this.index = 0;
    this.mode = "Play";
    /** @type {Record<string, unknown>} */
    this.session = {};
    this.wiredControls = new WeakSet();
    this.explorer = new ExplorerPanel(this, chrome, expansion);
    this.product = new ProductPanel(this);
  }

  start() {
    this._wireProductNav();
    for (const control of this.frame.controls) this.wireInteractive(control);
    this.chrome.storyMapToggle?.addEventListener("click", () => {
      this.page?.explorerFrame.storyMap.toggle();
      this.repaint();
    });
    this.chrome.playNext?.addEventListener("click", () => this.playNext());
    this.chrome.reset?.addEventListener("click", () => this.reset());
    return this.activateStory(0);
  }

  activateStory(storyIndex, carryInputs = {}) {
    this.index = storyIndex;
    const entry = this.catalog.entry(storyIndex);
    // Drop prior dynamic bound-list controls; static ones stay on the shared frame.
    this.frame.dropBoundListControls();
    this.page = this._loadPage(entry);
    this.page.selectScenario(0);
    this._applyCarried(carryInputs);
    this._ensureInteractiveGivens();
    this._captureSession();
    showScreensForStory(entry.title, this.root);
    this.repaint();
    return this.page;
  }

  _loadPage(entry) {
    const page = StoryDemoPage.load(entry.fn, COLLECT_MODE, { mode: this.mode, storyDemoFrame: this.frame });
    page.explorerFrame.storyMap.show(this.catalog.titles, entry.title);
    return page;
  }

  _applyCarried(carryInputs) {
    const scenario = this.page.runner.scenario;
    if (this.mode === "Interactive" && Object.keys(this.session).length) scenario.setSeed(this.session);
    if (Object.keys(carryInputs).length) scenario.setInputs(carryInputs);
  }

  /** Interactive needs Givens applied so bound lists (catalog) can paint and receive clicks. */
  _ensureInteractiveGivens() {
    if (this.mode !== "Interactive" || !this.page) return;
    const scenario = this.page.runner.scenario;
    if (!scenario) return;
    while (scenario.steps[scenario.index]?.kind === "given") {
      this.page.runner.playNext();
    }
  }

  _captureSession() {
    if (this.mode !== "Interactive" || !this.page) return;
    const snapshot = this.page.runner.scenario?.expose?.() ?? {};
    for (const key of SESSION_KEYS) {
      if (snapshot[key] != null) this.session[key] = snapshot[key];
    }
  }

  playNext() {
    if (!this.page) return;
    const scenario = this.page.runner.scenario;
    const atEnd = scenario != null && scenario.index >= (scenario.steps?.length ?? 0);
    if (!atEnd) this.page.explorerFrame.playNextControl.trigger("click");
    else if (this._playPastEnd(scenario)) return;
    this.repaint();
  }

  /** Past a scenario's last step: play the story's next scenario, or open the next story. True when a story opened. */
  _playPastEnd(scenario) {
    const scenarios = this.page.story.scenarios;
    const scenarioIndex = scenarios.indexOf(scenario);
    if (scenarioIndex >= 0 && scenarioIndex < scenarios.length - 1) {
      this.page.selectScenario(scenarioIndex + 1);
      return false;
    }
    if (this.index >= this.catalog.length - 1) return false;
    this.activateStory(this.index + 1);
    return true;
  }

  reset() {
    this.session = {};
    this.activateStory(this.index);
    this.page?.storyDemoFrame.clearEmphasis();
    this.page?.explorerFrame.clearMessage();
  }

  openScenario(storyIndex, scenarioIndex) {
    if (storyIndex >= 0 && storyIndex !== this.index) this.activateStory(storyIndex);
    if (this.page && scenarioIndex >= 0) this.page.selectScenario(scenarioIndex);
    this.repaint();
  }

  wireInteractive(control) {
    if (!control || this.wiredControls.has(control)) return;
    this.wiredControls.add(control);
    control.appendInteraction({ trigger: "click", effect: (triggered) => this._runControl(triggered) });
    control.listenForClicks(() => {
      if (this.page?.mode === "Interactive") control.trigger("click");
    });
  }

  _runControl(control) {
    if (this.page?.mode !== "Interactive") return;
    // Control may belong to another story on the map (e.g. Add to Cart while
    // Select Product is active) — switch first so When can match.
    this._activateStoryForControl(control);
    if (this.page.onControlTrigger(control, this.root)) {
      this._captureSession();
      showScreen(this.root, control.destination);
    }
    this.repaint();
  }

  _activateStoryForControl(control) {
    const whenLabel = (control.story_steps || []).find((s) => s.kind === "when")?.label;
    if (!whenLabel) return;
    const storyIndex = this.catalog.storyIndexForWhen(whenLabel);
    const carry = this._carryInputsFrom(control);
    if (storyIndex == null || storyIndex === this.index) {
      if (Object.keys(carry).length) this.page?.runner?.scenario?.setInputs?.(carry);
      return;
    }
    this.activateStory(storyIndex, carry);
  }

  _carryInputsFrom(control) {
    const carry = {};
    const exposed = this.page?.runner?.scenario?.expose?.();
    if (exposed?.product?.name) carry.product = exposed.product.name;
    if (control?.inputKey && control.name) carry[control.inputKey] = control.name;
    return carry;
  }

  /** A cart line click selects which product Remove (etc.) will use — no When yet. */
  wireLineSelect(row, pickedName, inputKey) {
    row.addEventListener("click", () => {
      if (this.page?.mode !== "Interactive") return;
      const scenario = this.page.runner.scenario;
      if (!scenario?.setInputs) return;
      scenario.setInputs({ [inputKey]: pickedName });
      this.repaint();
    });
  }

  _wireProductNav() {
    this._wireScreenClicks();
    this._wireGotoLinks();
    selectWithinRegion(this.root, ".tree-node:not([data-role='folder'])", ".tree-node");
    selectWithinRegion(this.root, "[data-type='list']", "[data-type='list']");
  }

  _wireScreenClicks() {
    const mockup = this.root.querySelector("#mockup");
    mockup?.addEventListener("click", (event) => {
      if (event.target.closest("[data-goto]")) return;
      const screen = event.target.closest(".screen");
      if (!screen || !mockup.contains(screen)) return;
      showScreen(this.root, screen.getAttribute("data-slug") || screen.querySelector("h2")?.textContent?.trim());
      if (!this.page) return;
      this.explorer.requestScroll();
      this.repaint();
    });
  }

  _wireGotoLinks() {
    this.root.querySelectorAll("[data-goto]").forEach((element) => {
      // Story-bound controls: Interactive owns goto after When (avoid empty-screen nav).
      if (element.hasAttribute("data-story-steps")) return;
      element.addEventListener("click", () => {
        showScreen(this.root, element.getAttribute("data-goto"));
      });
    });
  }

  repaint() {
    if (!this.page) return;
    this.explorer.paint();
    this.product.paint();
  }
}

/**
 * @param {ParentNode} [root]
 * @returns {Promise<StoryDemoPage | null>}
 */
export async function mountGeneratedMockup(root = document) {
  await composedFragments(root);
  const frameRoot = root.querySelector("#story-demo-frame") || root.querySelector("#mockup");
  const frame = new StoryDemoFrame(controlsOn(frameRoot || root));
  const chrome = explorerChromeOn(root);
  const createStories = await loadCreateStoryFns();
  if (!createStories.length) {
    if (chrome.tree) chrome.tree.innerHTML = "<li>(story modules not playable in browser yet)</li>";
    return null;
  }
  const catalog = StoryCatalog.fromStoryFunctions(createStories);
  return new GeneratedMockup(root, catalog, { frame, chrome, expansion: new ScreenTreeExpansion() }).start();
}

if (typeof document !== "undefined" && document.querySelector("[data-story-demo-shell]")) {
  mountGeneratedMockup(document);
}
