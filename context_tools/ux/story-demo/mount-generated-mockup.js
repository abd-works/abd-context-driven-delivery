/**
 * # @toolset-manifest python -m tools manifest context_tools.ux.ux:Ux
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.ux.ux:Ux
 * # invoke-check: action validate | toolset: context_tools.ux.ux:Ux
 *
 * Mount PlayDualRunner + explorer onto a UX-generated mockup shell.
 * Expects: #story-demo-frame (product), #explorer-frame chrome, [data-ux-story-ref] modules.
 * Multiple create{Story}Story exports → story picker (#story-list) + screens with data-for-story.
 * Serve from repo root so /context_tools/... imports resolve.
 */

import { StoryDemoControl } from "./control.js";
import { StoryDemoFrame } from "./story-demo-frame.js";
import { StoryDemoPage } from "./story-demo-page.js";

function readBound(snapshot, path) {
  if (!path || snapshot == null) return undefined;
  return path.split(".").reduce((acc, key) => acc?.[key], snapshot);
}

async function loadCreateStoryFns() {
  const fns = [];
  for (const script of document.querySelectorAll("[data-ux-story-ref]")) {
    const src = script.getAttribute("src");
    if (!src) continue;
    try {
      const url = new URL(src, document.baseURI).href;
      const mod = await import(url);
      for (const [key, value] of Object.entries(mod)) {
        if (typeof value === "function" && /^create.+Story$/.test(key)) {
          fns.push({ name: key, fn: value });
        }
      }
    } catch (err) {
      console.warn(`[story-demo] failed to load ${src}:`, err);
    }
  }
  return fns;
}

function hydrateControls(root) {
  const controls = [];
  root.querySelectorAll("[data-story-steps], [data-bound-field]").forEach((el) => {
    // List hosts are painted/wired dynamically — not static controls.
    if (
      el.hasAttribute("data-bound-list") ||
      el.getAttribute("data-type") === "bound-list"
    ) {
      return;
    }
    const control = StoryDemoControl.fromElement(el);
    if (control) {
      control._el = el;
      controls.push(control);
    }
  });
  return controls;
}

function paintStoryMap(page, el, onPickStory) {
  const mapEl = el.storyMap;
  if (!mapEl) return;
  const titles = page.explorerFrame.storyMap;
  const active = page.explorerFrame.activeStoryName ?? page.story?.name;
  const expanded = page.explorerFrame.isStoryMapExpanded();

  if (el.storyMapToggle) {
    el.storyMapToggle.textContent = expanded ? "▼" : "▶";
    el.storyMapToggle.setAttribute(
      "aria-expanded",
      expanded ? "true" : "false",
    );
    el.storyMapToggle.setAttribute(
      "aria-label",
      expanded ? "Collapse story map" : "Expand story map",
    );
  }

  mapEl.hidden = false;
  mapEl.innerHTML = "";
  const visible = expanded
    ? titles
    : titles.filter((title) => title === active);
  visible.forEach((title) => {
    const index = titles.indexOf(title);
    const li = document.createElement("li");
    li.textContent = title;
    li.style.cursor = "pointer";
    if (title === active) li.classList.add("current");
    li.addEventListener("click", () => {
      if (!expanded) {
        page.explorerFrame.expandStoryMap();
        paintAll(page, el, document, onPickStory);
        return;
      }
      onPickStory?.(index);
    });
    mapEl.appendChild(li);
  });
}

function paintExplorer(page, el, onPickStory) {
  const scenario = page.runner.scenario;
  const step = scenario?.currentStep;
  if (el.mode) el.mode.textContent = page.mode;

  paintStoryMap(page, el, onPickStory);

  // Scenario below story map — italic name, flat given/when/then (no bullet, no indent).
  if (el.tree && page.story) {
    el.tree.innerHTML = "";
    for (const sc of page.story.scenarios) {
      const scLi = document.createElement("li");
      scLi.className = "scenario-name";
      scLi.textContent = sc.name;
      scLi.addEventListener("click", () => {
        const idx = page.story.scenarios.indexOf(sc);
        page.selectScenario(idx);
        paintAll(page, el, onPickStory);
      });
      el.tree.appendChild(scLi);
      for (const s of sc.steps) {
        const stepLi = document.createElement("li");
        stepLi.className = "step";
        stepLi.textContent = `${s.kind} ${s.label}`;
        if (step && s.kind === step.kind && s.label === step.label) {
          stepLi.classList.add("current");
        }
        el.tree.appendChild(stepLi);
      }
    }
  }

  if (el.message) {
    el.message.hidden = !page.explorerFrame.message;
    el.message.textContent = page.explorerFrame.message || "";
  }
}

function paintCharacterSheet(snapshot, root) {
  const character = readBound(snapshot, "character");
  const tree = root.querySelector("[data-character-tree]");
  if (tree && character) {
    tree.querySelectorAll(".tree-node:not([data-role='folder'])").forEach((n) => n.remove());
    const node = document.createElement("div");
    node.className = "tree-node selected";
    node.textContent = `· ${character.name || "Hero"}`;
    tree.appendChild(node);
  }
  const list = root.querySelector("[data-ability-list]");
  if (list && character?.abilities) {
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
}

/**
 * Fill `{name}` / `{product}` (and other `{field}`) in item story-step templates.
 * List hosts use `data-item-story-steps` (not `data-story-steps`) so hydrate skips the container.
 */
function itemStoryStepsFor(item, rawTemplate, value) {
  if (!rawTemplate) return [];
  let template;
  try {
    template = JSON.parse(rawTemplate);
  } catch {
    return [];
  }
  if (!Array.isArray(template)) return [];
  const name = value ?? item?.name ?? item?.product ?? "";
  return template.map((step) => ({
    ...step,
    label: formatItemLabel(item, String(step.label ?? ""), name),
  }));
}

function itemPickValue(item, valueField) {
  if (valueField && item?.[valueField] != null) return String(item[valueField]);
  if (item?.name != null) return String(item.name);
  if (item?.product != null) return String(item.product);
  return "";
}

function formatItemLabel(item, template, fallbackName = "") {
  if (template) {
    return template.replace(/\{(\w+)\}/g, (_, key) => {
      if (key === "name" || key === "product") {
        return item?.[key] ?? fallbackName ?? "";
      }
      return item?.[key] ?? "";
    });
  }
  if (item?.product != null && item?.quantity != null) {
    return `${item.product} × ${item.quantity} @ ${item.unitPrice ?? ""}`;
  }
  const name = item?.name ?? fallbackName;
  const price = item?.unitPrice != null ? ` · ${item.unitPrice}` : "";
  const cat = item?.category ? ` · ${item.category}` : "";
  return `${name}${price}${cat}`.trim();
}

function removeBoundListControls(frame) {
  if (!frame) return;
  frame.controls = frame.controls.filter((c) => !c._fromBoundList);
}

function boundListHosts(root) {
  return [...root.querySelectorAll("[data-bound-list]")];
}

function itemsForBoundList(list, snapshot) {
  const path =
    list.getAttribute("data-bound-field") ||
    list.getAttribute("data-bound-list") ||
    "";
  if (path && path !== "true" && path !== "") {
    const direct = readBound(snapshot, path);
    if (Array.isArray(direct)) return direct;
  }
  return [];
}

/**
 * Generic Interactive list host: paint rows from expose path.
 * - data-item-story-steps ⇒ row click runs When (action list)
 * - else data-set-input ⇒ row click selects only (select list)
 */
function paintBoundLists(snapshot, root, page, wireInteractive, wireLineSelect) {
  removeBoundListControls(page?.storyDemoFrame);
  for (const list of boundListHosts(root)) {
    const items = itemsForBoundList(list, snapshot);
    list.innerHTML = "";
    if (!items?.length) {
      const empty = document.createElement("div");
      empty.className = "field dimmed";
      empty.textContent = "(empty)";
      list.appendChild(empty);
      continue;
    }
    const setInput = list.getAttribute("data-set-input") || "product";
    const valueField = list.getAttribute("data-item-value") || "";
    const labelTemplate = list.getAttribute("data-item-label") || "";
    const itemStepsRaw = list.getAttribute("data-item-story-steps");
    const goto = list.getAttribute("data-goto");
    const selectedName =
      page?.runner?.scenario?.input?.(setInput, undefined) ??
      readBound(snapshot, "product")?.name;
    for (const item of items) {
      const value = itemPickValue(item, valueField);
      const row = document.createElement("div");
      row.className = "control";
      row.dataset.type = "list";
      row.dataset.name = value;
      row.style.cursor = "pointer";
      row.setAttribute("data-set-input", setInput);
      row.textContent = formatItemLabel(item, labelTemplate, value);
      if (value && value === selectedName) row.classList.add("selected");
      if (goto) row.setAttribute("data-goto", goto);
      const storySteps = itemStoryStepsFor(item, itemStepsRaw, value);
      if (storySteps.length) {
        row.setAttribute("data-story-steps", JSON.stringify(storySteps));
      }
      list.appendChild(row);

      if (page?.storyDemoFrame && storySteps.length) {
        const control = new StoryDemoControl({
          name: value,
          controlType: "list",
          label: row.textContent,
          storySteps,
        });
        control._el = row;
        control._fromBoundList = true;
        page.storyDemoFrame.appendControl(control);
        wireInteractive?.(control);
      } else if (setInput) {
        wireLineSelect?.(row, { ...item, product: value, name: value }, setInput);
      }
    }
  }
}

function paintBoundFields(snapshot, root) {
  root.querySelectorAll("[data-bound-field]").forEach((el) => {
    if (el.tagName === "BUTTON") return;
    // List hosts own their children — do not overwrite with JSON blob.
    if (
      el.hasAttribute("data-bound-list") ||
      el.getAttribute("data-type") === "bound-list"
    ) {
      return;
    }
    const path = el.getAttribute("data-bound-field");
    const value = readBound(snapshot, path);
    const label = el.getAttribute("data-bound-label") || path;
    if (value === undefined || value === null) {
      el.textContent = `${label}: —`;
      return;
    }
    if (typeof value === "object") {
      el.textContent = `${label}: ${JSON.stringify(value)}`;
      return;
    }
    el.textContent = `${label}: ${value}`;
  });
}

function paintControls(page, root = document, wireInteractive, wireLineSelect) {
  const snapshot = page.runner.scenario?.expose?.() ?? {};
  const step = page.runner.scenario?.currentStep;
  paintCharacterSheet(snapshot, root);
  paintBoundLists(snapshot, root, page, wireInteractive, wireLineSelect);
  paintBoundFields(snapshot, root);
  for (const control of page.storyDemoFrame.controls) {
    const el = control._el;
    if (!el) continue;
    if (step) {
      control.clearEmphasis();
      if (control.matchesStep(step)) control.emphasize();
    }
    el.classList.toggle("emphasized", Boolean(control.emphasized));
    el.classList.toggle("tinted", Boolean(control.tinted));
  }
}

function paintAll(page, el, root = document, onPickStory, wireInteractive, wireLineSelect) {
  paintExplorer(page, el, onPickStory);
  paintControls(page, root, wireInteractive, wireLineSelect);
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
    const match = allowed.includes(storyTitle);
    if (!match) {
      screen.hidden = true;
      continue;
    }
    screen.hidden = shownFirst;
    shownFirst = true;
  }
}

function showScreen(root, dest) {
  if (!dest) return;
  for (const screen of root.querySelectorAll(".screen")) {
    const title = screen.querySelector("h2")?.textContent?.trim();
    const slug = screen.getAttribute("data-slug");
    screen.hidden = title !== dest && slug !== dest;
  }
}

function wireProductNav(root = document) {
  root.querySelectorAll("[data-goto]").forEach((el) => {
    // Story-bound controls: Interactive owns goto after When (avoid empty-screen nav).
    if (el.hasAttribute("data-story-steps")) return;
    el.addEventListener("click", () => {
      showScreen(root, el.getAttribute("data-goto"));
    });
  });

  root.querySelectorAll(".tree-node:not([data-role='folder'])").forEach((el) => {
    el.addEventListener("click", () => {
      const tree = el.closest("[data-region]");
      tree?.querySelectorAll(".tree-node").forEach((n) => n.classList.remove("selected"));
      el.classList.add("selected");
    });
  });

  root.querySelectorAll("[data-type='list']").forEach((el) => {
    el.addEventListener("click", () => {
      const region = el.closest("[data-region]");
      region?.querySelectorAll("[data-type='list']").forEach((n) => n.classList.remove("selected"));
      el.classList.add("selected");
    });
  });
}

/**
 * @param {ParentNode} [root]
 * @returns {Promise<StoryDemoPage | null>}
 */
export async function mountGeneratedMockup(root = document) {
  // Fragments must be inlined before hydrate (compose-fragments.js top-level await).
  if (root.querySelector?.("[data-include]")) {
    await new Promise((resolve) => {
      const start = performance.now();
      const tick = () => {
        if (!root.querySelector("[data-include]") || performance.now() - start > 3000) {
          resolve();
          return;
        }
        requestAnimationFrame(tick);
      };
      tick();
    });
  }

  const frameRoot = root.querySelector("#story-demo-frame") || root.querySelector("#mockup");
  const controls = hydrateControls(frameRoot || root);
  const frame = new StoryDemoFrame(controls);
  const createStories = await loadCreateStoryFns();

  const el = {
    mode: root.querySelector("[data-story-demo-mode]"),
    storyMap: root.querySelector("[data-story-map]") || root.querySelector("#story-list"),
    storyMapToggle: root.querySelector("[data-toggle-story-map]"),
    tree: root.querySelector("[data-explorer-tree]"),
    message: root.querySelector("[data-explorer-message]"),
    playNext: root.querySelector("[data-play-next]"),
    reset: root.querySelector("[data-reset]"),
  };

  wireProductNav(root);

  if (!createStories.length) {
    if (el.tree) {
      el.tree.innerHTML = "<li>(story modules not playable in browser yet)</li>";
    }
    return null;
  }

  const catalog = createStories.map(({ name, fn }) => {
    const probe = StoryDemoPage.load(fn, "fake", {});
    return { createName: name, fn, title: probe.story.name, story: probe.story };
  });
  const mapTitles = catalog.map((e) => e.title);

  /** When label → catalog index — Interactive can jump to the owning story. */
  const whenLabelToStoryIndex = new Map();
  catalog.forEach((entry, index) => {
    for (const sc of entry.story.scenarios ?? []) {
      for (const step of sc.steps ?? []) {
        if (step.kind === "when" && step.label) {
          whenLabelToStoryIndex.set(step.label, index);
        }
      }
    }
  });

  /** @type {{ page: StoryDemoPage | null, index: number, mode: string, session: Record<string, unknown> }} */
  const state = { page: null, index: 0, mode: "Play", session: {} };

  function captureSession() {
    if (state.mode !== "Interactive" || !state.page) return;
    const snap = state.page.runner.scenario?.expose?.() ?? {};
    for (const key of ["cart", "product", "catalog", "paymentMethod"]) {
      if (snap[key] != null) state.session[key] = snap[key];
    }
  }

  function carryInputsFrom(page, control) {
    const carry = {};
    const exposed = page?.runner?.scenario?.expose?.();
    if (exposed?.product?.name) carry.product = exposed.product.name;
    const setKey = control?._el?.getAttribute("data-set-input");
    if (setKey && control.name) carry[setKey] = control.name;
    return carry;
  }

  function activateStoryForControl(control) {
    const whenLabel = (control.story_steps || []).find((s) => s.kind === "when")?.label;
    if (!whenLabel) return;
    const index = whenLabelToStoryIndex.get(whenLabel);
    const carry = carryInputsFrom(state.page, control);
    if (index == null || index === state.index) {
      if (Object.keys(carry).length) state.page?.runner?.scenario?.setInputs?.(carry);
      return;
    }
    activateStory(index, carry);
  }

  function wireInteractive(control) {
    if (!control || control._interactiveWired) return;
    control._interactiveWired = true;
    control.appendInteraction({
      trigger: "click",
      effect: (c) => {
        if (state.page?.mode !== "Interactive") return;
        // Control may belong to another story on the map (e.g. Add to Cart while
        // Select Product is active) — switch first so When can match.
        activateStoryForControl(c);
        const ok = state.page.onControlTrigger(c, root);
        if (ok) {
          captureSession();
          showScreen(root, c._el?.getAttribute("data-goto"));
        }
        repaint();
      },
    });
    control._el?.addEventListener("click", () => {
      if (state.page?.mode === "Interactive") {
        control.trigger("click");
      }
    });
  }

  /** Cart line click selects which product Remove (etc.) will use — no When yet. */
  function wireLineSelect(row, item, setInput) {
    row.addEventListener("click", () => {
      if (state.page?.mode !== "Interactive") return;
      const scenario = state.page.runner.scenario;
      if (!scenario?.setInputs) return;
      scenario.setInputs({ [setInput]: item.product });
      repaint();
    });
  }

  function repaint() {
    if (state.page) {
      paintAll(state.page, el, root, activateStory, wireInteractive, wireLineSelect);
    }
  }

  /** Interactive needs Givens applied so bound lists (catalog) can paint and receive clicks. */
  function ensureInteractiveGivens() {
    if (state.mode !== "Interactive" || !state.page) return;
    const scenario = state.page.runner.scenario;
    if (!scenario) return;
    while (scenario.steps[scenario.index]?.kind === "given") {
      state.page.runner.playNext();
    }
  }

  function activateStory(index, carryInputs = {}) {
    state.index = index;
    const entry = catalog[index];
    // Drop prior dynamic bound-list controls; static ones stay on the shared frame.
    removeBoundListControls(frame);
    state.page = StoryDemoPage.load(entry.fn, "fake", {
      mode: state.mode,
      storyDemoFrame: frame,
    });
    state.page.explorerFrame.bindStoryMap(mapTitles, entry.title);
    state.page.selectScenario(0);
    if (state.mode === "Interactive" && Object.keys(state.session).length) {
      state.page.runner.scenario.setSeed(state.session);
    }
    if (Object.keys(carryInputs).length) {
      state.page.runner.scenario.setInputs(carryInputs);
    }
    ensureInteractiveGivens();
    captureSession();
    showScreensForStory(entry.title, root);
    repaint();
    return state.page;
  }

  for (const control of controls) {
    wireInteractive(control);
  }

  el.storyMapToggle?.addEventListener("click", () => {
    state.page?.explorerFrame.toggleStoryMap();
    repaint();
  });

  el.playNext?.addEventListener("click", () => {
    const page = state.page;
    if (!page) return;
    const scenario = page.runner.scenario;
    const atEnd =
      scenario != null && scenario.index >= (scenario.steps?.length ?? 0);
    if (atEnd) {
      const scIdx = page.story.scenarios.indexOf(scenario);
      if (scIdx >= 0 && scIdx < page.story.scenarios.length - 1) {
        page.selectScenario(scIdx + 1);
      } else if (state.index < catalog.length - 1) {
        activateStory(state.index + 1);
        return;
      }
    } else {
      page.explorerFrame.playNextControl.trigger("click");
    }
    repaint();
  });

  el.reset?.addEventListener("click", () => {
    state.session = {};
    activateStory(state.index);
    state.page?.storyDemoFrame.clearEmphasis();
    state.page?.explorerFrame.clearMessage();
  });

  root.querySelectorAll("[data-set-mode]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.mode = btn.getAttribute("data-set-mode") || "Play";
      if (state.page) state.page.mode = state.mode;
      root.querySelectorAll("[data-set-mode]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      ensureInteractiveGivens();
      repaint();
    });
  });

  return activateStory(0);
}

if (typeof document !== "undefined" && document.querySelector("[data-story-demo-shell]")) {
  mountGeneratedMockup(document);
}
