Run the action on clean_engineering at modules fidelity through the tools cli

Provide guidance for creating OO modules, models, and code.

Provide guidance from contexts, examples, and templates.

# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

**Progression:** `partition` (action) → **scaffold** → **modules** → **model** → **code**.

| Fidelity | Default format | Produce |
|---|---|---|
| **modules** | markdown (+ drawio) | Independent modules, one-way deps, build order, thin seam terms |
| **model** | python | Empty public seam (on `Class` directly by default, or on a separate `I{Class}` contract **only when interfaces are explicitly requested**) + full module-context; stub example factories |
| **code** | python | Typed contracts (`Class(I{Class})` when an interface was requested, otherwise `Class` directly) → full production implementation |

**Interfaces (`I{Class}`) are optional, not automatic.** See `## model` § Interfaces for the trigger — ask for one, or a genuine multi-layer/multi-implementation seam.

---

## Language companion (not a fidelity)

**Language is not invocable** (`context.fidelity: language` is rejected). Natural-language identity is a **companion** that deepens at every stage through code.

- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Do **not** invent types, method bodies, relationship kinds, or Public API ahead of the active fidelity.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place — never a separate language-only generate run.

---

## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view — blue boxes, seam-term bullets, one-way dependency arrows; template `templates/modules.drawio`). Language channels (python/java/…) are for **model** and later — not required here.

**Goal:** Refine **modules** purpose, primary use case, rationale, key terms, and relationship to other modules. Strive for **independent modules with one-way dependencies** and an explicit **build order**. Thin class/term identification only — enough to show independence.

A **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

- Consume the existing `{session}/.context/{subject}-index.md` and partition chunks if they exist — **do not edit** or wipe partitions.
- Create module structure (`physical-folder` / `nested-physical-folder`) under `{session}/{module}/`.
- When nesting, the **parent module** owns shared base classes/terms (e.g. `powers` owns `Effect`). Specializing children use a path under the parent (`powers/attack`) and depend on the parent — not on siblings. Do **not** invent a `parent/base` submodule (e.g. no `powers/effect`) just to hold shared content; that content belongs on the parent. Diagram: path nesting = containment (children drawn inside the parent box).
- Seed `{session}/{module}/.context/module-context.md` — **public seam only** (see **`module-context.md` — public seam only** below). Thin: **Purpose**, **Seam** (public term/class names), **Dependencies**, optional **Extend** / **Mechanism** note. No full Public API / `I{Class}` yet. **Never** internals.
- Write `{session}/.context/module-build-order.md` (or a **Build order** section on the subject index): topological order from one-way deps. **Cycles are a hard fail** — grill until deps are one-way.
- Name terms/classes only enough to show independence. Seed **language companion** prose for those names.
- Seam terms: **one name per concept** (prefer the type name). Do not list singular and plural of the same term (e.g. `Ability` — not `Ability, Abilities`).
- Do not add types, method bodies, or relationship kinds (composition / aggregation / association).

**Dependency rules**

- Dependencies are **one-way** (A → B means B is built before A).
- Children → parent base; never sibling → sibling.
- Partition's thin Deps column is a hint; **modules** owns the formal graph and build order.

### Nested modules

When several independently implementable modules share a **real common seam** (shared types, cost rules, activation protocol), nest them under a **parent module** rather than flattening siblings or duplicating the base into every child.

| Kind | Owns | Example |
|------|------|---------|
| **Parent** | Shared base types/mechanics + optional parent seam; folder that contains children | `powers/` owns shared **Effect** (rank, duration, descriptors, activate protocol) |
| **Child** | One independently implementable specialization | `powers/attack`, `powers/movement`, `powers/extras` |
| **Organisational folder only** | No seam — **not** a module | Do not invent empty parents |

**Rules**

- **`nested-physical-folder`** — Child module path is `{parent}/{child}/` (e.g. `powers/attack/`). Each module that is a real seam owns its own folder and `.context/module-context.md`. Parent shared code lives in the **parent** folder (e.g. types at `powers/`), not copy-pasted into every child — do not invent a `powers/effect` submodule for shared base.
- **`shared-base-before-siblings`** — If children would duplicate the same mechanics, extract **parent-owned base** types first; children depend on that base through a thin interface.
- **`nest-when-shared-else-flat`** — Nest under a parent only when there is shared mechanics or a clear sub-system boundary. Independent top-level concepts (`checks`, `character`) stay flat.
- **`independent-child`** — A child must still pass "implement with siblings stubbed"; it may depend on the **parent base**, not on sibling children.
- **Naming** — Domain nouns; path form `parent/child` in indexes and sketches (`powers/general`, `conflicts/turns`).

Examples: `powers` (owns Effect) + `powers/attack|control|defense|movement|sensory|general` + `powers/extras|flaws`; `conflicts/turns|actions|conditions`; `gear/equipment|headquarters|vehicles`.

### Module rules

- **`high-cohesion`** — Classes inside a module share a common purpose and operate on the same domain concept. Cross-class relationships within the module are strong and semantic, not incidental.
- **`low-coupling`** — Modules depend on each other only through well-defined interfaces. Cross-module dependencies are explicit and minimal — no module reaches into another's internals.
- **`single-boundary`** — Each module is the single source of truth for its domain concept. No other module holds, mutates, or duplicates that concept's state or rules.
- **`named-seam-and-constraint`** — Every module owns a *seam* — the public surface of classes and operations callers depend on — paired with a *constraint* stating what callers must do or must not do at that boundary. A module is described by what it requires of its callers, not only by what it holds.
- **`public-seam-only`** — `.context/module-context.md` documents **only** the public seam: how to **use** the module, how to **extend** it, and what its **dependencies** are. Internals are banned (see dedicated section below). Scanner: `public-seam-only`.
- **`deep-module`** — The seam stays a short named list of classes and operations with substantial functionality behind it (Ousterhout: small interface, large hidden implementation). If internal helpers leak into the seam, encapsulation is overhead without benefit. Scanner heuristic: at most **40%** of top-level symbols may be public (leading underscore for the rest).
- **`physical-folder`** — Each module occupies its own folder; class files, markdown documents, and other module-level artifacts live in it. Generated code belongs in that folder — not beside the module, not in a flat dump outside it. Nested modules use child folders under the parent (`nested-physical-folder`). Not every folder is a module — chapter or organisational folders may group several modules and must not be treated as one module unless they own `.context/module-context.md`. **Do not stop at an arbitrary depth** — every folder that is a cohesive functional unit owns `.context/module-context.md`; folders that are only implementation detail (`assets/`, thin config/) are absorbed into the parent description. Stopping mid-tree at `pages/My` while leaving nested pages, hooks, and services undocumented is a defect. **`module-context.md` never lives under `.context/sessions/`** — the session folder is for sprint artifacts; the context file belongs beside the source it describes.
- **`output-format`** — Written markdown is human-readable only. Strip template markup (`<!-- Mu -->`, `<!-- Mv -->`, and similar) before writing. A module heading sits immediately above its `- **Purpose:**` block — no blank line between them.
- **`cohesive-file`** — Put a **class family** in one file: the primary type, its subtypes, and tightly connected peers that only make sense together (element + collection, small aggregate + its part). Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`). Split into another file only when a type is independently reused across families or the file becomes a grab-bag of unrelated types. Do not default to one class per file. **Exception:** `{Type}ExampleFactory` (and its `examples` data, plus `I{Type}ExampleFactory` when one was requested) always live in a **sibling file** — never in the production family file (see **Example factories**).
- **`abstraction-focus`** — Module description names *what* the module does at a higher level than the classes inside it; public verbs are caller-facing, not internal steps or storage layouts.
- **`layer-separation`** — Adjacent modules operate at different abstraction levels; collapse pass-through modules.
- **`complexity-absorption`** — Push configuration and edge-case handling into the module; callers pass intent, not setup flags.
- **`information-hiding`** — Volatile implementation choices must not appear in public signatures or return types.
- **`temporal-independence`** — Every public operation leaves the module in a valid state; avoid order-coupled APIs or document the constraint.
- **`general-purpose-surface`** — Public interface is not hardcoded to one caller's UI/workflow.
- **`errors-out-of-existence`** — Prefer total functions / empty states for routine edges; reserve exceptions for real failures.

### Vanilla module vs. mechanism

A module is either a **vanilla module** or a **mechanism**. Most modules are vanilla — they own one domain concept and are instantiated once.

A **mechanism** is a structural pattern the codebase instantiates more than once. It has:
- **Variation points** — what changes per instance (the parameters of the pattern).
- **Fixed parts** — what the pattern enforces across all instances (the constants of the pattern).

Whether a module is a mechanism is stereotyped lightly at **modules** fidelity and made precise at **model** / **code** (variation points and fixed parts listed in the context file). Mechanism identification is optional and exploratory — pursue it when the pattern is genuinely recurring, not as a default.

At **modules** fidelity, `.context/module-context.md` is thin: Purpose, Seam (term list), Dependencies (one-way), optional Extend / Mechanism note — plus `{session}/.context/module-build-order.md`. At **model** fidelity it expands within the **same public-seam-only allowlist** (Purpose, Primary use case, Rationale, Seam, Public API, Constraint, Extend, Dependencies).

### `module-context.md` — public seam only

`.context/module-context.md` (and any `.module-context` synonym) is the **caller-facing contract**. It must contain **only**:

| Concern | Allowed headings / content |
|---|---|
| **Use** | **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API** / **Public surface**, **Constraint** — what callers invoke and what they must / must not do |
| **Extend** | **Extend**, **Extension**, **How to extend**, optional **Mechanism** / **Mechanism stereotype** — variation points and fixed parts that are part of the *public* extension contract; authoring annotations that callers use to extend |
| **Dependencies** | **Dependencies** — one-way module / package names only |

**Allowed headings (exact, case-insensitive):** `Purpose`, `Primary use case`, `Rationale`, `Seam`, `Public API`, `Public surface`, `Constraint`, `Dependencies`, `Extend`, `Extension`, `How to extend`, `Mechanism`, `Mechanism stereotype`. Authoring tables that document the public annotation protocol (e.g. `@toolset` / `@agent_tool`) may sit under **Extend** or **Seam** — they are how to extend, not internals.

**Hard ban — never put these in module-context:**

- **Internal design**, **Internals**, **Participants** (private collaborators), **Domain separation**, **Pickup**, **Layout** (as an implementation dump), **Known scan notes**, **Implementation**, **Scan violations**, **Tests**, **Scanners** (as a private inventory), or any heading containing *internal*
- Underscore-prefixed **types**, **helpers**, or **methods** (`_CliAgentLog`, `_Pickup`, `_await_pickup`, `_ensure_work_session`, `_scanner_collection`, …) — leading underscore means private; keep them out of the seam list and out of prose
- Abstract bases, doers/judges, job-template stores, and other **private participants** that are not the public contract callers import
- Implementation notes, pickup/transcript heuristics, test inventories, scanner FP notes, private marker wiring beyond the public authoring annotations

**Exception:** public authoring markers of the form `_is_*` (e.g. `_is_toolset`) may appear in an **Extend** / annotation table when they *are* the published protocol. Every other `_…` name is banned.

**Do not** add **Internal design**, **Participants**, or **Domain separation** at **code** (or any) fidelity — those belong in source, sketches, or session notes, never in module-context. Edit the same `.context/module-context.md` in place; never create a parallel internals file beside it.

Scanner rule: **`public-seam-only`**.

---

## shopping-cart/examples.md

<!-- @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source. -->
<!-- invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->
<!-- invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering -->

<!--
  clean_engineering markdown examples — ShoppingCart domain — unified across all fidelities.
  Structure: H1 = module, H2 = class.
  Interface (I{Type}) and implementation ({Type}) sit together under the same module H1.
  Language companion and modules overview go as prose before the first H1.
-->

## Language companion                                             <!-- L -->

*ShoppingCart* is a running tally of what a customer intends to buy in a single shopping session.

### shopping_cart                                                  <!-- L -->

- Belongs to exactly one *Customer* whose identity anchors the cart. <!-- L -->
- Collects *CartItems* as the customer browses and keeps the running total current. <!-- L -->
- Accepts an optional *Discount* applied before the total is computed. <!-- L -->
- **Invariant:** Once checked out, the cart may not be modified.  <!-- L -->

### discount                                                       <!-- L -->

- **Invariant:** A discount may not reduce the total below zero.  <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `inventory` → `cart`

---

# cart                                                            <!-- Mu -->

- **Purpose:** Owns the shopping-session tally and checkout gate. <!-- Mu -->
- **Seam (terms):** ShoppingCart, CartItem, Discount              <!-- Mu -->
- **Dependencies (one-way):** inventory                           <!-- Mu -->

## IShoppingCart                                                  <!-- Md -->

IShoppingCart(customer: Customer)
------
customer: Customer
items: list[CartItem]
discount: Discount | None
checked_out: bool
	Invariant: Once true, never reverts to false.
----
add_item(product: str, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
remove_item(product: str): None
	Invariant: Cart may not be modified after checkout.
apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
compute_total(): Decimal
checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
- _find_item(product: str): CartItem | None

## ShoppingCart                                                   <!-- S -->

+ ShoppingCart(customer: Customer)
------
+ << association >> customer: Customer
+ << composition >> items: list[CartItem]
+ << association >> discount: Discount | None
+ checked_out: bool
	Invariant: Once true, never reverts to false.
----
+ add_item(product: str, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
	Interaction:
		existing: CartItem | None = _find_item(product)
		if existing: existing.update_quantity(quantity)
		else: items.append(CartItem(product, quantity, unit_price))
+ remove_item(product: str): None
	Invariant: Cart may not be modified after checkout.
+ apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
+ compute_total(): Decimal
	Interaction:
		subtotal: Decimal = sum(item.line_total() for item in items)
		return discount.compute_reduction(subtotal) if discount else subtotal
+ checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
	Interaction:
		inventory.assert_available(items)
		checked_out = True
- _find_item(product: str): CartItem | None

## ICartItem                                                      <!-- Md -->

CartItem(product: str, quantity: int, unit_price: Decimal)
------
product: str
quantity: int
	Invariant: quantity >= 1.
unit_price: Decimal
	Invariant: unit_price >= 0.
----
line_total(): Decimal
update_quantity(quantity: int): None

## CartItem                                                       <!-- S -->

+ CartItem(product: str, quantity: int, unit_price: Decimal)
------
+ product: str
+ quantity: int
	Invariant: quantity >= 1.
+ unit_price: Decimal
	Invariant: unit_price >= 0.
----
+ line_total(): Decimal
	Interaction:
		return quantity * unit_price
+ update_quantity(quantity: int): None

## IDiscount                                                      <!-- Md -->

Discount(code: str, reduction: Decimal)
------
code: str
reduction: Decimal
	Invariant: reduction > 0.
----
is_valid(cart: ShoppingCart): bool
compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.

## Discount                                                       <!-- S -->

+ Discount(code: str, reduction: Decimal)
------
+ code: str
+ reduction: Decimal
	Invariant: reduction > 0.
----
+ is_valid(cart: ShoppingCart): bool
+ compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.
	Interaction:
		reduced: Decimal = subtotal - reduction
		return max(reduced, Decimal("0"))

---

# inventory                                                       <!-- Mu -->

- **Purpose:** Asserts stock availability at checkout.            <!-- Mu -->
- **Seam (terms):** Inventory                                     <!-- Mu -->
- **Dependencies (one-way):** *(none)*                            <!-- Mu -->

## IInventory                                                     <!-- Md -->

IInventory()
------
----
assert_available(items: list[CartItem]): None

## Inventory                                                      <!-- S -->

+ Inventory()
------
----
+ assert_available(items: list[CartItem]): None


<!--
  clean_engineering markdown template — unified across all fidelities.

  INTERFACES ARE OPTIONAL (see clean_engineering.md § Interfaces). This template shows
  the `I{ClassName}` form because it is the richer case to document. Default to
  skipping `## I{ClassName}` entirely and starting straight at `## {ClassName}` (empty,
  untagged-S members at model) unless the user asked for an interface, or the module
  genuinely has multiple layers/implementations behind one seam. When skipped, the S/C
  tags below still apply to `## {ClassName}` — there is just no separate Md section.

  Fidelity tags on section headings (as HTML comments — informational only):
    L  = language companion (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} — typed compact block — ONLY when an interface is
                         requested; otherwise model is the empty `## {ClassName}` block)
    S  = specification  ({ClassName}: public filled with + prefix, relationship kinds,
                         invariant sentences, interactions)
    C  = code           (fill {ClassName}; drop interactions; keep invariant comments)

  Class member format (model & specification):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — specification fidelity only

  Document structure: H1 = module, H2 = class within that module.
  Interface (I{ClassName}) and implementation ({ClassName}) both sit under the
  same module H1 — interface first, then implementation. No fidelity section
  headers (## Model fidelity / ## Specification fidelity) in the output.
  Language companion and modules overview go as prose BEFORE the first H1.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

**Sources / context:** {source_files}                             <!-- L -->

## Language companion                                             <!-- L -->

*{ClassName}* is {intent — what role it plays, what it holds, what it does.
This paragraph IS the class definition. Identity only.}           <!-- L -->

### {class_name_as_a_concept}                                     <!-- L -->

- {bullet: what it holds, what it does, how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {ChildClass} *is a type of* {ClassName}                       <!-- L -->

- {delta behavior only — what this subtype adds or overrides}     <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `{first}` → `{second}` → `{third}`

---

# {module_path}                                                   <!-- Mu -->

- **Purpose:** {one paragraph}                                    <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, ...                <!-- Mu -->
- **Dependencies (one-way):** {other_module}, ...                 <!-- Mu -->

## I{ClassName}                                                   <!-- Md, optional -->
<!-- Omit this section entirely by default — see note at top of file.
     Include it only when an interface was requested, or the module has
     multiple layers/implementations that need abstracting apart. -->

I{ClassName}({param}: {Type})
------
{owned_property}: {Type}
{plain_property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}
{another_operation}(): {ReturnType}

## {ClassName}                                                    <!-- Md (default, no interface) / S -->

+ {ClassName}({param}: {Type})
------
+ << composition >> {owned_property}: {Type}
	Invariant: {constraint sentence.}
+ << aggregation >> {collected_property}: list[{Type}]
+ << association >> {referenced_property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}
	Invariant: {constraint sentence applicable to this operation.}
	Interaction:
		{variable}: {Type} = {other}.{call}({args})
		return {variable}
- _{private_helper}({param}: {Type}): {Type}

## I{ChildClass}                                                  <!-- Md, optional -->

I{ChildClass}({param}: {Type})
------
----
{delta_operation}({param}: {Type}): {ReturnType}

## {ChildClass}                                                   <!-- Md (default, no interface) / S -->

+ {ChildClass}({param}: {Type})
------
+ {child_specific_property}: {Type}
	Invariant: {constraint sentence.}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {one paragraph}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*

## I{NextClassName}                                               <!-- Md, optional -->

I{NextClassName}({param}: {Type})
------
{property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}

## {NextClassName}                                                <!-- Md (default, no interface) / S -->

+ {NextClassName}({param}: {Type})
------
+ {property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}

---

### Example factory (when Stories-bound) — separate file           <!-- Md/S -->

Write factories in `{type_slug}_example_factory.md` (or code sibling), **not** in the production family file.
Do not sketch Fake{ClassName} / Isolated{ClassName} / Production{ClassName} types.

## I{ClassName}ExampleFactory                                     <!-- Md, optional — same opt-in rule -->

I{ClassName}ExampleFactory()
------
----
load_{example_key}(mode): I{ClassName}

## {ClassName}ExampleFactory                                      <!-- Md (default, no interface) / S -->

+ {ClassName}ExampleFactory()
------
----
+ load_{example_key}(mode): I{ClassName}
	// examples[{example_key}] multi-type bundle
	// Fake: mock/stub framework + feed examples
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)
	// Production: new {ClassName}(real collaborators)


Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: modules
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
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: modules
action: generate
```
.\tools.ps1 run -
