Run the action on ux at ia fidelity through the tools cli

Provide guidance for creating IA, mockups, and front-end code.

Provide guidance from contexts, examples, and templates.

# Contexts

UX looks at the product through user navigatin and information architecture, from layout and transitions to more formal screens, regions, and controls — how users see and act on the solution — mapped at increasing fidelity.

**Canonical model** (reuse, do not reinvent): `UxMap` → `Screen` → `Region` → `Control` → `Interaction`, plus `Transition`, `ContentType`, `NavComponent` on the map. Optional `UxContext` holds notes/invariants not visible on screens.

**Layout (mirror Stories; colocated):**

```
sandbox/<epic>/
  ux-map.json                              <- canonical model (optional peer)
  <user-goal>.html                        <- mockup+ (one file per concrete user goal)
  <sub-epic>/…_stories.py|.js
  .context/
    information-architecture.drawio        <- ia (drawio-ux CLI: Detailed IA + Site Map)
    ux-sketch.md                           <- scratch sketch
    ux-context.md                          <- optional notes/invariants
```

Sketch/context MD stay in `.context/` (same pattern as other generators). Story / object-model JS stay where Stories / CE emit them; HTML imports those modules.

**Stories + object model:** `UxMap.story_references` / `object_references` store **paths** to Stories / Clean Engineering JS artifacts. If missing, run that generator’s `transform` to `javascript`. Mockup/spec HTML imports those paths.

**Story Demo shell (mockup+):** Generated HTML uses `templates/html/mockup_shell.html` — product screens **LEFT**, story explorer **RIGHT**. `story-demo/mount-generated-mockup.js` loads `create{Story}Story` exports, runs `PlayDualRunner`, and paints the explorer. Serve from **repo root** so `/context_tools/...` imports resolve.

**Worked example:** `context_tools/ux/examples/manage-customer-orders/` (Place New Order mockup + stories + shopping_cart domain) — general UX output sample that happens to run in the Story Demo shell.

**One control model:** `ux_model.Control` is vanilla. Controls that bind to GWT steps are `StoryDemoControl` (`bound_field` + `story_steps`) — HTML emits `data-bound-field` / `data-story-steps`. Do **not** invent a second page/control model in freehand HTML.

**Interactive (domain-agnostic):** `StoryDemoControl` may also carry `set_input`, `item_story_steps`, `item_value`, `item_label`. Emit:
- `number` / `quantity` → `data-input-field`
- `bound-list` / `list-host` → `data-bound-list` + `data-bound-field` (expose path) + optional `data-item-story-steps` / `data-set-input`  
Do **not** bake product words (catalog, cart) into the template — those are bound_field paths / story language only.

**Markdown:** optional context only (thinking, invariants, interaction notes). Primary path is **drawio (IA) → html (mockup/spec)**.

**Specifications (layouts):** `specifications/` holds the full IA screen-template set as ready-to-adapt reference artifacts, one sibling folder per style:

- `specifications/generic/` — **default.** One `.md` ASCII reference + one `.drawio` XML fragment per layout (accordion, breadcrumb, kanban-board, sidebar, tabbed, wizard-stepper, … 43 patterns), mirrored verbatim from abd-skills. No brand.
- `specifications/abd-works/` — the same 43 layouts as real, brand-styled HTML (`<id>.html` + `index.html`), all sharing `abd-works-brand.css` (tokens/type/components copied from the `abd-visual-branding` SKILL.md: colors, Inter/JetBrains Mono type scale, buttons, cards, dual Executive/Engineering mode). Use this folder instead of `generic/` whenever the screen needs the abd.works brand (see `brand-is-opt-in` below).
- Add further sibling folders under `specifications/` for other brands/styles the same way; each folder's own files stay self-contained (own stylesheet, own copies).

Before sketching a screen's ASCII box, drawio region cells, or brand-layer html, open the matching file(s) in the specification folder that applies — `generic/` unless a specific brand is asked for or already established for this work — read its slots, and alter that file for the real screen. Do not draw box art, drawio cells, or brand markup from scratch when one of these already covers the shape. `Screen.apply_layout(layout_id)` just records that choice as the layout name; append the real `Region`s yourself from the slots you just read.

**Channels:** drawio, html, markdown, json — peer parse/render; `transform` moves sideways at the same fidelity. One `html` channel deepens by fidelity (js interactions → optional brand layer + honest stubs at **mockup** → real frontend at **front_end_code**; host FE stacks welcome at **front_end_code**).

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **ia** | drawio | Site map + per-screen regions/nav (html optional via transform) |
| **mockup** | html | Wired greybox screens (html+js); one HTML per concrete user goal (not one file per screen, not one mega-file per epic); drawio remains a peer channel; optional brand layer; honest stub catalogue |
| **front_end_code** | html (or host FE stack) | Real frontend — production UI wired to real backend; not Story Demo / greybox alone |

**Templates (AI generate):** drawio + html under `templates/`. Markdown context template optional. Other formats via channels / `transform`.

**Cross-format scanners:** channels parse into the canonical model; scanners read model fields only — never file syntax.

---

## Shared rules

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when context_tools/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---

## ia

**Default format:** drawio

**Goal:** What screens exist and how users move between them — missing coverage shows as absent nodes.

- Screens, layouts, named regions, transitions, nav components, content types.
- Story names and domain terms attached as traces (from story/domain JS or sources).
- Optional `ux-context.md` for invariants / notes not on the canvas.
- No control types, no interaction JS, no brand.

### Rules

- **`tab-states-are-separate-screens`** / **`screen-story-budget`** / **`ia-named-regions-only`** — as above.
- **`system-stories-group-with-visible-trigger`** — System stories group with the closest user-visible screen.

---

## manage-customer-orders/.context/story-map.md

---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Manage Customer Orders (UX example)

**Home:** `context_tools/ux/examples/manage-customer-orders/`  
Connected lenses: Stories (exploration) · Clean Engineering (modules) · UX (mockup + Story Demo shell).  
Thin slice: `.context/thin-slice.md`

---

(E) Manage Customer Orders
    (E) Place New Order
        (S) Customer --> Select Product
        (S) Customer --> Add Item To Cart
        (S) Customer --> Remove Item From Cart
        (S) Customer --> Submit Order

---

## Scope boundary

**In scope:** Increment 1 cart spine for the Story Demo shell.  
**Out of scope:** Shipping, delivery, track, cancel (not in this example package).


## manage-customer-orders/.context/thin-slice.md

---
fidelity: [discovery]
artifact: [thin-slice]
format: md
---

# Thin slicing — Manage Customer Orders (UX example)

## Product / context

**Product:** Manage Customer Orders — catalog → cart → checkout (UX example; runs in the Story Demo shell).

**Slicing intent:** Increment 1 proves the ShoppingCart public seam (select, add, remove, submit) before shipping / cancel depth. Cart total is always visible on the cart screen — not a separate story.

**Spine vs optional:** Spine is **Select Product → Add Item To Cart → Remove Item From Cart → Submit Order**. Shipping, delivery, tracking, and cancel are out of this example package.

## Increments

### Increment 1: Shop and submit a cart

**Outcome:** Customer selects a Product, manages Cart lines (total always shown), and submits an Order.

**Slicing notes:** Fake ExampleFactory + browser Story Demo only. No shipping address or delivery options yet.

**Stories in this increment** *(order reflects flow within the slice):*

- *Select Product*
- *Add Item To Cart*
- *Remove Item From Cart*
- *Submit Order*


## manage-customer-orders/manage-customer-orders-helper.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 *
 * Epic helper — given* → ShoppingCartExampleFactory (this package).
 */

import { ShoppingCartExampleFactory } from "./shopping_cart_example_factory.js";

export class ManageCustomerOrdersHelper {
  shoppingCartExampleFactory() {
    return new ShoppingCartExampleFactory();
  }

  givenEmptyCart({ mode } = { mode: "fake" }) {
    return this.shoppingCartExampleFactory().loadEmptyCart({ mode });
  }

  givenCartWithThreeItems({ mode } = { mode: "fake" }) {
    return this.shoppingCartExampleFactory().loadCartWithThreeItems({ mode });
  }

  givenHardwareCatalog({ mode } = { mode: "fake" }) {
    return this.shoppingCartExampleFactory().loadHardwareCatalog({ mode });
  }

  givenSelectedWidget({ mode } = { mode: "fake" }) {
    return this.shoppingCartExampleFactory().loadSelectedWidget({ mode });
  }

  givenSelectedProduct({ mode, name } = { mode: "fake", name: "Widget" }) {
    return this.shoppingCartExampleFactory().loadSelectedProduct({ mode, name });
  }
}


## manage-customer-orders/place-new-order/add-item-to-cart/add-item-to-cart.fragment.html

<article class="screen" data-slug="product-detail" data-layout="stack" hidden
         data-for-story="Add Item To Cart">
  <h2>product detail</h2>
  <section class="region" data-region="detail">
    <h3>product</h3>
    <div class="field" data-bound-field="product.name" data-bound-label="product">product: —</div>
    <div class="field" data-bound-field="product.unitPrice" data-bound-label="price">price: —</div>
    <div class="field" data-bound-field="product.category" data-bound-label="category">category: —</div>
    <label class="control" data-name="Quantity">
      quantity
      <input type="number" min="1" step="1" value="2" data-input-field="quantity" />
    </label>
    <button type="button" class="control button"
            data-name="Add to Cart"
            data-story-steps='[{"kind":"when","label":"the Customer adds Product \"Widget\" with Quantity 2 to the Cart"}]'
            data-goto="shopping cart">
      Add to Cart
    </button>
  </section>
  <p class="screen-stories">Story: Add Item To Cart</p>
</article>


## manage-customer-orders/place-new-order/add-item-to-cart/add_item_to_cart_story.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Exploration — Add Item To Cart main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createAddItemToCartStory(mode) {
  story("Add Item To Cart", () => {
    scenario("selected product added to empty cart", ({ given, when, then, expose, input, session }) => {
      let cart;
      let product;

      given("an empty Cart for Customer Alex Morgan", () => {
        cart = session("cart", () => helper.givenEmptyCart({ mode }).cart);
      });

      given('And a selected Product "Widget" at 49.99 USD', () => {
        const prior = session("product", null);
        const name = input("product", null) ?? prior?.name ?? "Widget";
        product = helper.givenSelectedProduct({ mode, name }).product;
      });

      // Play / node defaults: Widget × 2; Interactive sets product + quantity inputs.
      when('the Customer adds Product "Widget" with Quantity 2 to the Cart', () => {
        cart.addItem(product.name, input("quantity", 2), product.unitPrice);
      });

      then("the Cart contains one Cart Item for Widget with Quantity 2", () => {
        const quantity = input("quantity", 2);
        assert.equal(cart.items.length, 1);
        assert.equal(cart.items[0].product, input("product", "Widget"));
        assert.equal(cart.items[0].quantity, quantity);
      });

      then("And the Cart line total for Widget is 99.98 USD", () => {
        const quantity = input("quantity", 2);
        const expected = Math.round(quantity * product.unitPrice * 100) / 100;
        assert.equal(cart.items[0].quantity * cart.items[0].unitPrice, expected);
      });

      expose(() => ({
        cart,
        product,
        quantity: input("quantity", 2),
        itemCount: cart.items.length,
        total: cart.computeTotal(),
      }));
    });
  });
}

if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createAddItemToCartStory("fake");
  }
}


## manage-customer-orders/place-new-order/compose-fragments.js

/**
 * Load [data-include] HTML fragments (story-folder screens) into the composed page.
 * Run before mount-generated-mockup.js hydrates controls.
 */

async function includeFragments(root = document) {
  const nodes = [...root.querySelectorAll("[data-include]")];
  for (const el of nodes) {
    const src = el.getAttribute("data-include");
    if (!src) continue;
    const url = new URL(src, document.baseURI).href;
    const res = await fetch(url);
    if (!res.ok) {
      console.warn(`[compose] failed to load ${src}:`, res.status);
      continue;
    }
    const html = await res.text();
    el.outerHTML = html;
  }
  // Nested includes (e.g. cart regions) — one more pass if any remain.
  if (root.querySelector("[data-include]")) {
    await includeFragments(root);
  }
}

await includeFragments(document);


## manage-customer-orders/place-new-order/place-new-order.html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>UX Story Demo — Place New Order</title>
  <style>
    :root { --ink: #222; --line: #666; --wash: #f0f0f0; --sel: #dbeafe; --emph: #2563eb; --tint: #fecaca; }
    body { margin: 0; font-family: ui-monospace, Consolas, monospace; color: var(--ink);
           min-height: 100vh; background: #fafafa; }
    header.shell-bar { display: flex; gap: 0.75rem; align-items: center; padding: 0.75rem 1rem;
                       border-bottom: 1px solid #ccc; background: #fff; }
    header.shell-bar h1 { font-size: 1rem; margin: 0; flex: 1; }
    header.shell-bar button { font: inherit; padding: 0.25rem 0.6rem; cursor: pointer; }
    header.shell-bar button.active { background: var(--sel); outline: 1px solid #6c8ebf; }
    #shell { display: grid; grid-template-columns: 2fr 1fr; min-height: calc(100vh - 3rem); }
    #story-demo-frame { padding: 1rem; overflow: auto; border-right: 1px solid #ccc; }
    #explorer-frame { padding: 0.35rem 0.5rem; overflow: auto; }
    .screen { border: 1px dashed var(--line); margin-bottom: 1rem; padding: 0.75rem;
               background: #fff; max-width: 52rem; }
    .screen[hidden] { display: none; }
    .region { margin: 0.5rem 0; padding: 0.5rem; border: 1px solid #ddd; background: var(--wash); }
    .region h3 { margin: 0 0 0.5rem; font-size: 0.9rem; }
    .control.button { display: inline-block; margin: 0.35rem 0.35rem 0 0; padding: 0.25rem 0.6rem;
                       border: 1px solid var(--ink); background: #eee; cursor: pointer; font: inherit; }
    .control.emphasized { outline: 2px solid var(--emph); background: #eff6ff; }
    .control.tinted { background: var(--tint); }
    .control.selected, .tree-node.selected { background: var(--sel); outline: 1px solid #6c8ebf; }
    .field { margin: 0.25rem 0; }
    .field.dimmed { opacity: 0.55; }
    .panel { border: 1px dashed var(--line); background: #fff; padding: 0.5rem; }
    #explorer-frame .panel { padding: 0.4rem 0.5rem; }
    .explorer-head {
      display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.35rem;
    }
    .explorer-head h2 { margin: 0; font-size: 0.8rem; flex: 1; font-weight: 600; }
    .explorer-head button { font: inherit; font-size: 0.8rem; padding: 0.15rem 0.45rem; cursor: pointer; }
    #explorer-tree, #story-list {
      margin: 0.15rem 0 0; padding: 0; list-style: none; font-size: 0.8rem;
    }
    #explorer-tree li, #story-list li { margin: 0; padding: 0.05rem 0; }
    #explorer-tree .scenario-name { font-style: italic; cursor: pointer; list-style: none; }
    #explorer-tree .step { list-style: none; padding-left: 0; }
    #explorer-tree .current, #story-list .current { background: var(--sel); font-weight: 600; }
    #story-list li { cursor: pointer; }
    .section-toggle {
      font: inherit; font-size: 0.8rem; padding: 0 0.3rem; cursor: pointer;
      border: 1px solid #ccc; background: #eee; line-height: 1.2;
    }
    .section-head { display: flex; align-items: center; gap: 0.35rem; margin: 0.45rem 0 0.15rem; }
    .section-head h3 { margin: 0; font-size: 0.8rem; flex: 1; font-weight: 600; }
    .message { color: #a00; margin-top: 0.35rem; min-height: 0; font-size: 0.8rem; }
    .chrome { margin-top: 0.5rem; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
    .chrome button { font: inherit; font-size: 0.8rem; padding: 0.15rem 0.45rem; cursor: pointer; }
    .key { font-size: 0.8rem; color: #555; margin-top: 0.25rem; }
    .nav-strip { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.75rem; }
    .nav-strip button { font: inherit; padding: 0.2rem 0.5rem; cursor: pointer; }
  </style>
</head>
<body data-story-demo-shell>
  <header class="shell-bar">
    <h1>Place New Order · <span data-story-demo-mode>Play</span></h1>
    <button type="button" data-set-mode="Play" class="active">Play</button>
    <button type="button" data-set-mode="Interactive">Interactive</button>
  </header>

  <div id="shell" data-layout="split-screen">
    <section id="story-demo-frame" aria-label="Product mockup">
      <main id="mockup">
        <nav class="nav-strip" aria-label="Screen jump">
          <button type="button" data-goto="product catalog">catalog</button>
          <button type="button" data-goto="product detail">detail</button>
          <button type="button" data-goto="shopping cart">cart</button>
          <button type="button" data-goto="checkout">checkout</button>
        </nav>

        <!-- Composed from story-folder fragments (page hierarchy ≈ story hierarchy) -->
        <div data-include="./select-product/select-product.fragment.html"></div>
        <div data-include="./add-item-to-cart/add-item-to-cart.fragment.html"></div>

        <article class="screen" data-slug="shopping-cart" data-layout="stack" hidden
                 data-for-story="Add Item To Cart,Remove Item From Cart">
          <h2>shopping cart</h2>
          <div data-include="./remove-item-from-cart/remove-item-from-cart.fragment.html"></div>
          <p class="screen-stories">Stories: Add Item To Cart · Remove Item From Cart</p>
        </article>

        <div data-include="./submit-order/submit-order.fragment.html"></div>

        <p class="key">LEFT: fragments from story folders · pick a story on the right · Play next</p>
      </main>
    </section>

    <section id="explorer-frame" aria-label="Story explorer">
      <div class="panel">
        <div class="explorer-head">
          <h2>explorer</h2>
          <button type="button" data-reset>Reset</button>
        </div>

        <div class="section-head">
          <button type="button" class="section-toggle" data-toggle-story-map aria-expanded="true">▼</button>
          <h3>story map</h3>
        </div>
        <ul id="story-list" data-story-map></ul>

        <div class="section-head">
          <h3>scenario</h3>
        </div>
        <ul id="explorer-tree" data-explorer-tree></ul>

        <div class="chrome"><button type="button" data-play-next>▶▶ Play next</button></div>
        <p class="message" data-explorer-message hidden></p>
      </div>
    </section>
  </div>

  <script type="module"
          src="/context_tools/ux/examples/manage-customer-orders/place-new-order/select-product/select_product_story.js"
          data-ux-story-ref></script>
  <script type="module"
          src="/context_tools/ux/examples/manage-customer-orders/place-new-order/add-item-to-cart/add_item_to_cart_story.js"
          data-ux-story-ref></script>
  <script type="module"
          src="/context_tools/ux/examples/manage-customer-orders/place-new-order/remove-item-from-cart/remove_item_from_cart_story.js"
          data-ux-story-ref></script>
  <script type="module"
          src="/context_tools/ux/examples/manage-customer-orders/place-new-order/submit-order/submit_order_story.js"
          data-ux-story-ref></script>
  <script type="module" src="./compose-fragments.js"></script>
  <script type="module" src="/context_tools/ux/story-demo/mount-generated-mockup.js"></script>
</body>
</html>


## manage-customer-orders/place-new-order/remove-item-from-cart/remove-item-from-cart.fragment.html

<section class="region" data-region="lines">
  <h3>cart lines</h3>
  <!-- Select list: row sets input; Remove button runs When -->
  <div data-bound-list
       data-bound-field="cart.items"
       data-set-input="product"
       data-item-value="product"
       data-item-label="{product} × {quantity} @ {unitPrice}">
    <div class="field dimmed">(list loads with story)</div>
  </div>
  <button type="button" class="control button"
          data-name="Remove"
          data-story-steps='[{"kind":"when","label":"the Customer removes a Product from the Cart"}]'>
    Remove
  </button>
</section>
<section class="region" data-region="totals">
  <h3>totals</h3>
  <div class="field" data-bound-field="itemCount" data-bound-label="items">items: —</div>
  <div class="field" data-bound-field="total" data-bound-label="total">total: —</div>
  <button type="button" class="control button" data-goto="checkout">Go to checkout</button>
</section>


## manage-customer-orders/place-new-order/remove-item-from-cart/remove_item_from_cart_story.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Exploration — Remove Item From Cart main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createRemoveItemFromCartStory(mode) {
  story("Remove Item From Cart", () => {
    scenario("cart line removed leaving remaining items", ({ given, when, then, expose, input, session }) => {
      let cart;

      given("a Cart with Cart Items for Widget and Gadget", () => {
        // Interactive keeps the live cart; Play/factory only when none yet.
        cart = session("cart", () => helper.givenCartWithThreeItems({ mode }).cart);
      });

      // Play / node default removes Gadget; Interactive selects a cart line first.
      when("the Customer removes a Product from the Cart", () => {
        cart.removeItem(input("product", "Gadget"));
      });

      then("the Cart no longer contains the removed Product", () => {
        const removed = input("product", "Gadget");
        assert.ok(!cart.items.some((i) => i.product === removed));
      });

      then("And the Cart still contains at least one other Cart Item", () => {
        assert.ok(cart.items.length >= 1);
      });

      expose(() => ({
        cart,
        product: { name: input("product", "Gadget") },
        itemCount: cart.items.length,
        total: cart.computeTotal(),
        products: cart.items.map((i) => i.product),
      }));
    });
  });
}

if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createRemoveItemFromCartStory("fake");
  }
}


## manage-customer-orders/place-new-order/select-product/select-product.fragment.html

<article class="screen" data-slug="product-catalog" data-layout="stack"
         data-for-story="Select Product">
  <h2>product catalog</h2>
  <section class="region" data-region="catalog">
    <h3>Hardware</h3>
    <!-- Generic bound-list host (not a template special-case for "catalog") -->
    <div data-bound-list
         data-bound-field="catalog.products"
         data-goto="product detail"
         data-set-input="product"
         data-item-value="name"
         data-item-label="{name} · {unitPrice} USD · {category}"
         data-item-story-steps='[{"kind":"when","label":"the Customer selects a Product from the Product Catalog"}]'>
      <div class="field dimmed">(list loads with story)</div>
    </div>
  </section>
  <p class="screen-stories">Story: Select Product</p>
</article>


## manage-customer-orders/place-new-order/select-product/select_product_story.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * Exploration — Select Product main flow (UX examples / manage-customer-orders).
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createSelectProductStory(mode) {
  story("Select Product", () => {
    scenario("product selected from catalog for cart", ({ given, when, then, expose, input, session }) => {
      let catalog;
      let selected;

      given("a Product Catalog listing Widgets under Category Hardware", () => {
        catalog = session("catalog", () => helper.givenHardwareCatalog({ mode }).catalog);
      });

      given('And a Product "Widget" priced at 49.99 USD', () => {
        assert.ok(catalog.products.some((p) => p.name === "Widget"));
      });

      // Play / node default product is Widget; Interactive sets input from catalog row.
      when("the Customer selects a Product from the Product Catalog", () => {
        const name = input("product", "Widget");
        selected = catalog.products.find((p) => p.name === name);
      });

      then("Product Detail for the selected Product is shown with its unit price", () => {
        const name = input("product", "Widget");
        const listed = catalog.products.find((p) => p.name === name);
        assert.ok(selected);
        assert.equal(selected?.name, name);
        assert.equal(selected?.unitPrice, listed?.unitPrice);
      });

      then("And the Product is ready to add to the Cart", () => {
        assert.equal(selected?.name, input("product", "Widget"));
      });

      expose(() => ({
        catalog,
        product: selected,
        productName: selected?.name ?? null,
        unitPrice: selected?.unitPrice ?? null,
      }));
    });
  });
}

if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createSelectProductStory("fake");
  }
}


## manage-customer-orders/place-new-order/submit-order/submit-order.fragment.html

<article class="screen" data-slug="checkout" data-layout="stack" hidden
         data-for-story="Submit Order">
  <h2>checkout</h2>
  <section class="region" data-region="cart summary">
    <h3>cart summary</h3>
    <div data-bound-list
         data-bound-field="cart.items"
         data-item-value="product"
         data-item-label="{product} × {quantity} @ {unitPrice}">
      <div class="field dimmed">(list loads with story)</div>
    </div>
    <div class="field" data-bound-field="itemCount" data-bound-label="items">items: —</div>
    <div class="field" data-bound-field="total" data-bound-label="total">total: —</div>
    <div class="field">payment: Visa ending 4242</div>
  </section>
  <section class="region" data-region="actions">
    <h3>actions</h3>
    <button type="button" class="control button"
            data-name="Submit Order"
            data-story-steps='[{"kind":"when","label":"the Customer confirms and submits the Order"}]'>
      Submit Order
    </button>
    <div class="field" data-bound-field="orderNumber" data-bound-label="order">order: —</div>
  </section>
  <p class="screen-stories">Story: Submit Order</p>
</article>


## manage-customer-orders/place-new-order/submit-order/submit_order_story.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 *
 * Exploration — Submit Order main flow (UX examples / manage-customer-orders).
 *
 * Run (node): import story-test-node first, then this file as test entry.
 */

import { ManageCustomerOrdersHelper } from "../../manage-customer-orders-helper.js";
import { assert } from "../../../../story-demo/play-dual-runner/soft-assert.js";
import { scenario, story } from "../../../../story-demo/play-dual-runner/story-test-core.js";

const helper = new ManageCustomerOrdersHelper();

/** @param {"fake"|"isolated"|"production"} mode */
export function createSubmitOrderStory(mode) {
  story("Submit Order", () => {
    scenario("order submitted with valid cart and payment", ({
      given,
      when,
      then,
      expose,
      session,
    }) => {
      let cart;
      let paymentMethod;
      let confirmation;

      given("a Cart with three Items totalling 149.98 USD", () => {
        cart = session("cart", () => helper.givenCartWithThreeItems({ mode }).cart);
        paymentMethod = session("paymentMethod", () => ({
          label: "Visa ending 4242",
          status: "authorised",
        }));
        confirmation = null;
      });

      given('And a Payment Method on file "Visa ending 4242"', () => {
        assert.equal(paymentMethod?.status, "authorised");
      });

      when("the Customer confirms and submits the Order", () => {
        assert.equal(paymentMethod.status, "authorised");
        confirmation = cart.checkout();
      });

      then("an Order Confirmation is issued with an Order Number", () => {
        assert.ok(confirmation?.orderNumber);
        assert.equal(confirmation.status, "placed");
      });

      then("And the Cart is emptied", () => {
        assert.equal(cart.items.length, 0);
        assert.equal(cart.checkedOut, true);
      });

      expose(() => ({
        cart,
        paymentMethod,
        confirmation,
        orderNumber: confirmation?.orderNumber ?? null,
        itemCount: cart.items.length,
        total: cart.checkedOut ? 0 : cart.computeTotal(),
      }));
    });
  });
}

if (typeof process !== "undefined" && process.versions?.node) {
  const [{ fileURLToPath }, { default: path }] = await Promise.all([
    import("node:url"),
    import("node:path"),
  ]);
  await import("../../../../story-demo/play-dual-runner/story-test-node.js");
  const thisFile = fileURLToPath(import.meta.url);
  const entry = process.argv[1] && path.resolve(process.argv[1]);
  if (entry && path.resolve(thisFile) === entry) {
    createSubmitOrderStory("fake");
  }
}


## manage-customer-orders/shopping_cart_example_factory.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 *
 * Example factory for the Manage Customer Orders UX example (fake | isolated | production).
 */

import {
  Customer,
  Product,
  ProductCatalog,
  ShoppingCart,
} from "../shopping_cart/index.js";

const examples = {
  widget: { name: "Widget", unitPrice: 49.99, category: "Hardware" },
  gadget: { name: "Gadget", unitPrice: 50.0, category: "Hardware" },
  alexMorgan: { name: "Alex Morgan" },
  emptyCart: { customerKey: "alexMorgan", total: 0 },
  cartWithThreeItems: {
    customerKey: "alexMorgan",
    lines: [
      { productKey: "widget", quantity: 2 },
      { productKey: "gadget", quantity: 1 },
    ],
    total: 149.98,
    paymentMethod: { label: "Visa ending 4242", status: "authorised" },
  },
  hardwareCatalog: { productKeys: ["widget", "gadget"] },
};

function productFrom(key) {
  const row = examples[key];
  return new Product(row.name, row.unitPrice, row.category);
}

function customerFrom(key) {
  return new Customer(examples[key].name);
}

function buildCart(data) {
  const customer = customerFrom(data.customerKey);
  const cart = new ShoppingCart(customer);
  for (const line of data.lines || []) {
    const product = productFrom(line.productKey);
    cart.addItem(product, line.quantity, product.unitPrice);
  }
  return cart;
}

export class ShoppingCartExampleFactory {
  loadEmptyCart({ mode } = { mode: "fake" }) {
    const data = examples.emptyCart;
    const cart = buildCart({ ...data, lines: [] });
    return { cart, customer: cart.customer, total: data.total, mode };
  }

  loadCartWithThreeItems({ mode } = { mode: "fake" }) {
    const data = examples.cartWithThreeItems;
    const cart = buildCart(data);
    return {
      cart,
      customer: cart.customer,
      total: data.total,
      paymentMethod: { ...data.paymentMethod },
      mode,
    };
  }

  loadHardwareCatalog({ mode } = { mode: "fake" }) {
    const products = examples.hardwareCatalog.productKeys.map(productFrom);
    const catalog = new ProductCatalog(products);
    return { catalog, products, mode };
  }

  loadSelectedWidget({ mode } = { mode: "fake" }) {
    return this.loadSelectedProduct({ mode, name: "Widget" });
  }

  /** @param {{ mode?: string, name?: string }} [opts] */
  loadSelectedProduct({ mode = "fake", name = "Widget" } = {}) {
    const key = Object.keys(examples).find((k) => examples[k]?.name === name);
    if (!key) throw new Error(`Unknown product: ${name}`);
    return { product: productFrom(key), mode };
  }
}


## README.md

# UX examples

Worked samples of UX output (mockup HTML, story modules, domain JS) — not part of the `story-demo` runtime package.

| Example | What it shows |
|--------|----------------|
| `manage-customer-orders/` | Place New Order greybox + Story Demo shell wiring |
| `shopping_cart/` | Domain modules used by that example |

## Run

From the repo root:

```
node context_tools/ux/story-demo/run.mjs
```

Then open:

`http://localhost:3000/context_tools/ux/examples/manage-customer-orders/place-new-order/place-new-order.html`

Optional: `PORT=3001` or `STORY_DEMO_EXAMPLE=/path/to/other.html`.


## shopping_cart/customer.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 *
 * Modules fidelity — Customer.
 */

export class ICustomer {
  /** Person whose identity anchors a ShoppingCart session. */
  constructor(_name) {}
  get name() {}
}

export class Customer extends ICustomer {
  constructor(name) {
    super(name);
    this._name = name;
  }

  get name() {
    return this._name;
  }
}


## shopping_cart/index.js

/**
 * Barrel — ShoppingCart example domain module.
 */

export { ICustomer, Customer } from "./customer.js";
export {
  IProduct,
  Product,
  IProductCatalog,
  ProductCatalog,
} from "./product.js";
export {
  ICartItem,
  CartItem,
  IShoppingCart,
  ShoppingCart,
} from "./shopping-cart.js";


## shopping_cart/product.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 *
 * Modules fidelity — Product + ProductCatalog.
 */

export class IProduct {
  /** A sellable item listed in the Product Catalog. */
  constructor(_name, _unitPrice, _category) {}
  get name() {}
  get unitPrice() {}
  get category() {}
}

export class Product extends IProduct {
  constructor(name, unitPrice, category) {
    super(name, unitPrice, category);
    this._name = name;
    this._unitPrice = Number(unitPrice);
    this._category = category;
  }

  get name() {
    return this._name;
  }

  get unitPrice() {
    return this._unitPrice;
  }

  get category() {
    return this._category;
  }
}

export class IProductCatalog {
  /** Browsable list of products available to order. */
  constructor(_products) {}
  listByCategory(_category) {}
  select(_productName) {}
  get products() {}
}

export class ProductCatalog extends IProductCatalog {
  constructor(products = []) {
    super(products);
    this._products = [...products];
  }

  get products() {
    return this._products;
  }

  listByCategory(category) {
    return this._products.filter((p) => p.category === category);
  }

  select(productName) {
    const found = this._products.find((p) => p.name === productName);
    if (!found) throw new Error(`product not found: ${productName}`);
    return found;
  }
}


## shopping_cart/shopping-cart.js

/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 *
 * Modules fidelity — CartItem + ShoppingCart.
 */

import { Customer } from "./customer.js";

export class ICartItem {
  /** A single product choice inside a ShoppingCart. */
  constructor(_product, _quantity, _unitPrice) {}
  get product() {}
  get quantity() {}
  get unitPrice() {}
  lineTotal() {}
  updateQuantity(_quantity) {}
}

export class CartItem extends ICartItem {
  constructor(product, quantity, unitPrice) {
    super(product, quantity, unitPrice);
    if (quantity < 1) throw new Error("quantity must be at least 1");
    this._product = typeof product === "string" ? product : product.name;
    this._quantity = quantity;
    this._unitPrice = Number(unitPrice);
  }

  get product() {
    return this._product;
  }

  get quantity() {
    return this._quantity;
  }

  get unitPrice() {
    return this._unitPrice;
  }

  lineTotal() {
    return Math.round(this._quantity * this._unitPrice * 100) / 100;
  }

  updateQuantity(quantity) {
    if (quantity < 1) throw new Error("quantity must be at least 1");
    this._quantity = quantity;
  }
}

export class IShoppingCart {
  /** Running tally of what a customer intends to buy in a single shopping session. */
  constructor(_customer) {}
  get customer() {}
  get items() {}
  get checkedOut() {}
  addItem(_product, _quantity, _unitPrice) {}
  removeItem(_product) {}
  computeTotal() {}
  checkout() {}
}

export class ShoppingCart extends IShoppingCart {
  constructor(customer) {
    super(customer);
    this._customer =
      customer instanceof Customer ? customer : new Customer(customer.name);
    this._items = [];
    this._checkedOut = false;
    this._orderNumber = null;
  }

  get customer() {
    return this._customer;
  }

  get items() {
    return this._items;
  }

  get checkedOut() {
    return this._checkedOut;
  }

  get orderNumber() {
    return this._orderNumber;
  }

  addItem(product, quantity, unitPrice) {
    if (this._checkedOut) throw new Error("cart is checked out");
    const name = typeof product === "string" ? product : product.name;
    const price =
      unitPrice != null
        ? Number(unitPrice)
        : typeof product === "object"
          ? product.unitPrice
          : undefined;
    if (price == null) throw new Error("unitPrice required");
    const existing = this._items.find((i) => i.product === name);
    if (existing) {
      existing.updateQuantity(existing.quantity + quantity);
      return;
    }
    this._items.push(new CartItem(name, quantity, price));
  }

  removeItem(product) {
    if (this._checkedOut) throw new Error("cart is checked out");
    const name = typeof product === "string" ? product : product.name;
    this._items = this._items.filter((i) => i.product !== name);
  }

  computeTotal() {
    const raw = this._items.reduce((sum, i) => sum + i.lineTotal(), 0);
    return Math.round(raw * 100) / 100;
  }

  /** Seals the cart and issues a simple order number (demo — no Inventory). */
  checkout() {
    if (this._checkedOut) throw new Error("already checked out");
    if (!this._items.length) throw new Error("cart is empty");
    this._orderNumber = `ORD-${String(Date.now()).slice(-7)}`;
    this._checkedOut = true;
    this._items = [];
    return {
      orderNumber: this._orderNumber,
      status: "placed",
    };
  }
}


## html/mockup.html

<!DOCTYPE html>
<!--
  AI mockup template (Story Demo shell).
  Prefer filling the model + HtmlUxMap.render (uses mockup_shell.html).
  When authoring HTML directly, keep this split: product LEFT + explorer RIGHT.

  Controls that participate in a story step MUST be StoryDemoControl in the model, which emits:
    data-bound-field="…"
    data-story-steps='[{"kind":"when","label":"…"}]'
  Serve from repo root. mount-generated-mockup.js collects create{Story}Story exports.
-->
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>UX — {{SCOPE}}</title>
  <style>
    body { margin: 0; font-family: ui-monospace, Consolas, monospace; }
    #shell { display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh; }
    #story-demo-frame { border-right: 1px solid #ccc; padding: 1rem; }
    #explorer-frame { padding: 1rem; }
    .control.emphasized { outline: 2px solid #2563eb; }
    .control.tinted { background: #fecaca; }
  </style>
</head>
<body data-story-demo-shell>
  <header>
    <span data-story-demo-mode>Play</span>
    <button type="button" data-set-mode="Play">Play</button>
    <button type="button" data-set-mode="Interactive">Interactive</button>
  </header>
  <div id="shell">
    <section id="story-demo-frame">
      <main id="mockup">
        <!-- screens / regions / controls — emit data-story-steps on StoryDemoControls -->
      </main>
    </section>
    <section id="explorer-frame">
      <button type="button" data-reset>Reset</button>
      <ul data-explorer-tree></ul>
      <button type="button" data-play-next>Play next</button>
      <p data-explorer-message hidden></p>
      <p data-story-demo-status></p>
      <footer id="stories"><ul><!-- story names --></ul></footer>
    </section>
  </div>
  <script type="module" src="{{STORY_MODULE}}" data-ux-story-ref></script>
  <script type="module" src="{{DOMAIN_MODULE}}" data-ux-object-ref></script>
  <script type="module" src="/context_tools/ux/story-demo/mount-generated-mockup.js"></script>
</body>
</html>


## html/mockup_shell.html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>UX — @@TITLE@@</title>
  <style>
    :root { --ink: #222; --line: #666; --wash: #f0f0f0; --sel: #dbeafe; --emph: #2563eb; --tint: #fecaca; }
    body { margin: 0; font-family: ui-monospace, Consolas, monospace; color: var(--ink);
           min-height: 100vh; background: #fafafa; }
    header.shell-bar { display: flex; gap: 0.75rem; align-items: center; padding: 0.75rem 1rem;
                       border-bottom: 1px solid #ccc; background: #fff; }
    header.shell-bar h1 { font-size: 1rem; margin: 0; flex: 1; }
    header.shell-bar button { font: inherit; padding: 0.25rem 0.6rem; cursor: pointer; }
    header.shell-bar button.active { background: var(--sel); outline: 1px solid #6c8ebf; }
    #shell { display: grid; grid-template-columns: 1fr 1fr; min-height: calc(100vh - 3rem); }
    #story-demo-frame, #explorer-frame { padding: 1rem; overflow: auto; }
    #story-demo-frame { border-right: 1px solid #ccc; }
    .screen { border: 1px dashed var(--line); margin-bottom: 1rem; padding: 0.75rem;
               background: #fff; max-width: 52rem; }
    .screen[hidden] { display: none; }
    .screen[data-layout="modal"] {
      max-width: 28rem; margin: 2rem auto; border-style: solid;
      box-shadow: 0 0 0 9999px rgba(0,0,0,0.12);
    }
    .layout { color: #666; font-size: 0.85rem; margin-top: -0.5rem; }
    .regions { display: flex; flex-direction: column; gap: 0.5rem; }
    .screen[data-layout="sidebar"] .regions { display: grid; grid-template-columns: 12rem 1fr; }
    .screen[data-layout="split-screen"] .regions { display: grid; grid-template-columns: 1fr 1fr; }
    .screen[data-layout="holy-grail"] .regions {
      display: grid; grid-template-columns: 8rem 1fr 8rem;
      grid-template-areas: "header header header" "nav body aside" "footer footer footer";
    }
    .screen[data-layout="holy-grail"] .region[data-slot="header"] { grid-area: header; }
    .screen[data-layout="holy-grail"] .region[data-slot="nav"] { grid-area: nav; }
    .screen[data-layout="holy-grail"] .region[data-slot="body"] { grid-area: body; }
    .screen[data-layout="holy-grail"] .region[data-slot="aside"] { grid-area: aside; }
    .screen[data-layout="holy-grail"] .region[data-slot="footer"] { grid-area: footer; }
    .screen[data-layout="tabbed"] .region[data-slot="tab-bar"] { background: #e8e8e8; }
    .region { margin: 0; padding: 0.5rem; border: 1px solid #ddd; background: var(--wash); }
    .region h3 { margin: 0 0 0.5rem; font-size: 0.9rem; }
    .control { display: block; margin: 0.35rem 0; }
    .control[hidden], .control.hidden { display: none !important; }
    .control.button { display: inline-block; margin-right: 0.35rem;
                       padding: 0.25rem 0.6rem; border: 1px solid var(--ink); background: #eee;
                       cursor: pointer; font: inherit; }
    .control.button.primary { background: #e5e5e5; font-weight: 600; }
    .control.button.emphasized, .control.emphasized { outline: 2px solid var(--emph); background: #eff6ff; }
    .control.button.tinted, .control.tinted { background: var(--tint); }
    .control.selected, .tree-node.selected { background: var(--sel); outline: 1px solid #6c8ebf; }
    .control.disabled, .tree-node.dimmed { opacity: 0.45; }
    .control.error { color: #a00; }
    input[type="text"], select { font: inherit; padding: 0.15rem 0.35rem;
                                   border: 1px solid var(--ink); background: #fff; min-width: 8rem; }
    .tree-node { padding: 0.1rem 0.25rem; cursor: pointer; }
    .tree-node .twist { display: inline-block; width: 1.2rem; }
    .tree-node[data-role="folder"] { font-weight: 600; cursor: default; }
    .screen-stories { font-size: 0.85rem; color: #444; }
    .key { font-size: 0.8rem; color: #555; margin-top: 0.75rem; }
    .panel { border: 1px dashed var(--line); background: #fff; padding: 0.75rem; }
    #explorer-tree ul { margin: 0.25rem 0 0.25rem 1rem; padding: 0; list-style: none; }
    #explorer-tree li.current, #explorer-tree .current { background: var(--sel); font-weight: 600; }
    .message { color: #a00; margin-top: 0.75rem; min-height: 1.2rem; }
    .chrome { margin-top: 1rem; display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
    .status { font-size: 0.8rem; color: #555; margin-top: 0.5rem; }
    .toast { position: fixed; right: 1rem; bottom: 1rem; background: #222; color: #fff;
              padding: 0.5rem 0.75rem; font-size: 0.85rem; display: none; z-index: 2; }
    .toast.show { display: block; }
  </style>
</head>
<body data-story-demo-shell>
  <header class="shell-bar">
    <h1>@@TITLE@@ · <span data-story-demo-mode>Play</span></h1>
    <button type="button" data-set-mode="Play" class="active">Play</button>
    <button type="button" data-set-mode="Interactive">Interactive</button>
  </header>

  <div id="shell" data-layout="split-screen">
    <section id="story-demo-frame" aria-label="Product mockup">
      <main id="mockup">
        @@SCREENS@@
        <p class="key">LEFT: product screens · «emph» / bind via data-bound-field · Interactive uses data-story-steps</p>
      </main>
    </section>

    <section id="explorer-frame" aria-label="Story explorer">
      <div class="panel">
        <h2>explorer</h2>
        <div class="chrome">
          <button type="button" data-reset>Reset</button>
        </div>
        <ul id="explorer-tree" data-explorer-tree></ul>
        <div class="chrome">
          <button type="button" data-play-next>▶▶ Play next</button>
        </div>
        <p class="message" data-explorer-message hidden></p>
        <p class="status" data-story-demo-status></p>
        <p class="key">RIGHT: GWT from collect · Play next is chrome only · not product controls</p>
        <footer id="stories" style="margin-top:1rem;border-top:1px solid #ddd;padding-top:0.5rem;">
          <strong>Stories</strong>
          <ul id="story-list">@@STORIES_LIST@@</ul>
        </footer>
      </div>
    </section>
  </div>

  <div id="toast" class="toast" role="status"></div>
@@ENSURE_HINT@@@@STORY_IMPORTS@@
@@OBJECT_IMPORTS@@
  <script type="module" src="/context_tools/ux/story-demo/mount-generated-mockup.js"></script>
  <script type="module">
    // Generic screen nav (data-goto). Story Play / Interactive is mounted by mount-generated-mockup.js.
    const transitions = [
@@TRANSITIONS_JS@@
    ];
    const toast = document.querySelector('#toast');
    const list = document.querySelector('#story-list');
    const seen = new Set([...list.querySelectorAll('li')].map((li) => li.textContent));

    for (const script of document.querySelectorAll('[data-ux-story-ref]')) {
      try {
        const mod = await import(script.getAttribute('src'));
        const names = mod.storyNames
          || Object.values(mod)
              .filter((value) => value && typeof value === 'object' && value.story)
              .map((value) => value.story);
        for (const name of names || []) {
          if (!name || seen.has(name)) continue;
          seen.add(name);
          const li = document.createElement('li');
          li.textContent = name;
          list.appendChild(li);
        }
      } catch (_err) {
        // Artifact may be missing until Stories transform / JS emit runs.
      }
    }

    function flash(msg) {
      toast.textContent = msg;
      toast.classList.add('show');
      clearTimeout(flash._t);
      flash._t = setTimeout(() => toast.classList.remove('show'), 1600);
    }

    function showScreen(name) {
      for (const screen of document.querySelectorAll('.screen')) {
        const title = screen.querySelector('h2')?.textContent?.trim();
        screen.hidden = title !== name;
      }
    }

    function visibleScreen() {
      return [...document.querySelectorAll('.screen:not([hidden])')][0];
    }

    document.querySelectorAll('[data-goto]').forEach((el) => {
      el.addEventListener('click', () => {
        const dest = el.getAttribute('data-goto');
        showScreen(dest);
        flash(`→ ${dest}`);
      });
    });

    document.querySelectorAll('[data-trigger]').forEach((el) => {
      el.addEventListener('click', () => {
        if (el.hasAttribute('data-story-steps')) return; // Story Demo owns these in Interactive
        const trigger = el.getAttribute('data-trigger');
        const from = visibleScreen()?.querySelector('h2')?.textContent?.trim();
        const hit = transitions.find((t) => t.from === from && t.trigger === trigger)
          || transitions.find((t) => t.trigger === trigger);
        if (hit) showScreen(hit.to);
      });
    });
  </script>
  <!-- ux-map-json:
@@MODEL_JSON@@
  -->
</body>
</html>


## md/ux-context.md

# UX context — {{SCOPE}}

Optional notes that are not easily visible on screens (same role as story-context / module-context).

## Invariants

- {{INVARIANT}}

## Notes

- {{THINKING_OR_INTERACTION_NOTE}}


Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.ux.ux:Ux
context:
  fidelity: ia
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Suggested flow (repeat and reorder as the story needs):

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.ux.ux:Ux
context:
  fidelity: ia
action: generate
```
.\tools.ps1 run -
