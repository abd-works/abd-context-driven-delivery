Run the action on ddd at bounded_context fidelity through the tools cli

Provide guidance for creating bounded contexts, building blocks, and tactics.
When DDD scaffolding is ready, call guidance on the CE companion and pass that companion to this action as a separate tools run for matching OO artifacts.
Scan the production source for every public method and property; flag any with no corresponding test as a coverage gap. Fix every BDD violation and coverage gap — confirm each failing test is RED for the right reason.
If the same test is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (wrong exception, wrong line, shifting failure mode, or a re-read of the code that does not explain the failure).
When this DDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

Provide guidance from contexts, examples, and templates.

# Contexts

## bounded_context

**Default format:** markdown

**Goal:** Draw context boundaries, dependency arcs, and the aggregates that protect invariants — naming everything in the experts' vocabulary.

A **bounded context** is the boundary of **one model and one ubiquitous language**. Inside it, every term has one meaning. Across it, the same word may mean different things.

An **aggregate** is not a context. It is a **consistency** cluster *inside* a context: one root, a boundary, the invariants that boundary protects. Several aggregates that share the same language live in the **same** context (Catalog can hold Plan, Offer, …). Do **not** mint a bounded context per aggregate — that is a class with a fence around it, not a model boundary.

Failure modes: **duplicate concepts** (same real-world thing modeled twice); **false cognates** (same term, different meaning); **one-aggregate contexts** (every root wrapped as its own BC); **UI-theme contexts** (Onboarding vs Selfcare vs SignIn as BCs, with Customer/Catalog copied under each screen group); **ignoring change-frequency** (parking a fast-changing Subscription inside a slow Customer identity context).

**Context map:** identify contexts → name them → describe contact points with translation. Each context is a **peer card**, not a nested bullet inside another context's box. Shared Kernel is an **arc** between peers, not a parent card containing children.

**What gets tracked on a dependency:** direction (upstream/downstream/mutual, naming both sides); what crosses (concepts + translation); how they integrate — name the concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). Categories like Events / Messaging / REST/API / Batch / Shared DB / File Transfer / Shared Kernel help, but "in-process" or "module seam" alone is not enough; relationship pattern from the catalogue below. Undecided items get owner + target date.

**Patterns:** Shared Kernel (shared subset, consult on change); Customer/Supplier (one-way, joint acceptance tests); Conformist (downstream adopts upstream); Anticorruption Layer (translate/isolate legacy); Open Host / Published Language (published protocol); Separate Ways (no integration). No ad hoc labels like "loose coupling."

**Boundary heuristics:** split a context when language, team, model, **or lifecycle change-frequency** actually diverges — not when you add another aggregate, and not when the UI grows another theme or page. Screens are not contexts. Things that change at different rates (stable identity vs line/service lifecycle vs catalog merchandising) are candidates for different contexts; things that change together stay together (cart, billing, and the subscription they pay for). Size ~ten people upper bound; external systems usually Separate Ways / Conformist / ACL; formalize informal internal sharing; transform boundaries with clear current/end state.

An **Aggregate** is decided **inside** the context already named. Cluster for **one transaction / one invariant set**, not relatedness; keep aggregates small.

**Links:** when a BC, aggregate, or concept depends on another, append `→ BC · Aggregate · Entity` or `→ System · Entity`. Drop leading segments when the target shares the same BC or aggregate (e.g. `→ · Voucher` inside Customer). Integration pattern and call site belong in notes or **building_blocks**, not on the bounded_context card.

**Input traps:** hidden coupling; ownership ambiguity; false cognates; missing unnamed contexts; unclear direction; a new BC for each aggregate.

**Produce:** one `bounded-context-map.md` in **tree format** — `## BC | vendor`, then `### Aggregate`, then bulleted **concepts**. Links on any level: `→ BC · Aggregate · Entity` (cross-context; omit leading segments when same BC/aggregate) or `→ System · Entity` (external vendor). Fill `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

**Rules:**

- **`experts-words-preferred`** — Prefer the words domain experts use; do not invent technical synonyms when a domain word already exists. A ported telephone number is `TelephoneNumber` with `PortingInformation`, not `PortabilityRequest`; the operation is `port()`, not `requestPortability()`.
- **`domain-concepts-not-technical-names`** — Every class/module names a domain concept (or honest boundary collaborator). Reject `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, `*Request`. Do not invent a type for fields that already belong on a concept (`OrderResult` → fields on `Order`). Do not invent a concept the experts and the running system do not name.
- **`bc-by-lifecycle-not-ui-themes`** — Partition bounded contexts by ubiquitous language and by how fast the model changes, not by UI themes, pages, or journey stages. Do not mint Selfcare / Onboarding / Acquisition contexts that duplicate Customer, Catalog, and Subscription. Put purchase, cart, and billing with the faster-changing lifecycle they serve, not under slow-changing identity.
- **`one-meaning-per-context`** — Inside a context, one definition per term; false cognates across contexts are named and translated. The context is that language boundary. Aggregates are consistency clusters inside it — several per context is normal. Do not wrap each aggregate in its own bounded context. On the map, every context is a peer card — not a parent-box bullet.
- **`dependency-fields-tracked`** — Every arc states direction (named sides or mutual), what crosses, how they integrate (concrete mechanism), and catalogue relationship pattern — or a dated follow-up with owner.
- **`no-orphan-contexts`** — Every inventoried context appears in a dependency arc or is declared standalone with rationale.
- **`vendor-not-implementation`** — BC title carries vendor after `|` — `custom`, `bespoke`, or vendor name. No owning team or implementation stack on the card.
- **`context-tree-bc-aggregate-concept`** — Three levels only: BC → Aggregate → concept. No Root, Boundary members, Refs, Protected invariants, or #### Dependencies blocks on the bounded_context card.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading BC/Aggregate segments when the target is in the same context or aggregate.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the **concept or aggregate that has the dependency**, not in a global `## Dependencies` section. External-system links sit on the aggregate that owns the integration (e.g. Inventory → Mavenir DEP).
- **`user-facing-system-first`** — On the context map, the system you are wrapping — the consumer app — sits first (left / upstream). External systems of record sit downstream. Do not start the layout at Mavenir / AWS / a vendor column.

---

## examples.md

# Examples — DDD

---

# Bounded Context Map — Shop

## Catalog | custom

Product identity and pricing — slower-changing than checkout.

### Product

- Product
→ Sales · ShoppingCart · CartItem

## Sales | custom

Shopping carts, checkout, discounts.

### ShoppingCart

- CartItem
- Discount
- unit_price snapshot → Catalog · Product
→ Catalog · Product

#### **ShoppingCart** <<Aggregate Root>> <<Entity>>

+ ShoppingCart(customer: CustomerId)
------
+ << identifier >> customer: CustomerId                 # by ID — cross-aggregate
+ << composition >> items: list[CartItem]
+ << association >> discount: Discount | None
+ checked_out: bool
	Invariant: Once true, never reverts to false.
----
+ add_item(product: ProductId, quantity: int, unit_price: Decimal): None
	Invariant: Cart may not be modified after checkout.
	Invariant: Quantity must be at least 1.
+ remove_item(product: ProductId): None
	Invariant: Cart may not be modified after checkout.
+ apply_discount(discount: Discount): None
	Invariant: Cart may not be modified after checkout.
+ compute_total(): Decimal
+ checkout(inventory: Inventory): None
	Invariant: May not be called when already checked out.
- _find_item(product: ProductId): CartItem | None

#### **CartItem** <<Value Object>>

+ CartItem(product: ProductId, quantity: int, unit_price: Decimal)
------
+ product: ProductId                                    # by ID — snapshot at add time
+ quantity: int
	Invariant: quantity >= 1.
+ unit_price: Decimal
	Invariant: unit_price >= 0. Immutable — replace, do not update in place.
----
+ line_total(): Decimal
+ update_quantity(quantity: int): None

#### **Discount** <<Value Object>> <<Specification>>

+ Discount(code: str, reduction: Decimal)
------
+ code: str
+ reduction: Decimal
	Invariant: reduction > 0.
----
+ is_valid(cart: ShoppingCart): bool
+ compute_reduction(subtotal: Decimal): Decimal
	Invariant: Total may not be reduced below zero.

#### **ShoppingCartRepository** <<Repository>>

+ ShoppingCartRepository()
------
----
+ add(cart: ShoppingCart): None
+ remove(cart: ShoppingCart): None
+ update(cart: ShoppingCart): None
+ find_by_customer(customer: CustomerId): ShoppingCart | None

#### **CartCheckedOut** <<Domain Event>>

+ CartCheckedOut(cart_id: CartId, customer: CustomerId, total: Decimal, checked_out_at: DateTime)
------
+ cart_id: CartId
+ customer: CustomerId
+ total: Decimal
+ checked_out_at: DateTime
	Invariant: Raised when ShoppingCart.checkout succeeds.
	Invariant: Consumers are Inventory (assert/reserve) and Notifications (receipt).
----


## bounded-context-template.md

<!--

  Bounded Context Map — tree format



  BC → Aggregate → concept. Links on any level:

  → BC · Aggregate · Entity   (another context; omit leading segments when same BC/aggregate)

  → System · Entity           (external vendor / system of record)



  building_blocks fidelity adds CE compact classes under each aggregate (not shown here).

-->



# Bounded Context Map — {{project_name}}



## Map format



Three levels: **BC** → **Aggregate** → **concept**.



`→ BC · Aggregate · Entity` — cross-context (drop segments when same BC or aggregate).



`→ System · Entity` — external system (e.g. `→ Mavenir DEP · engagedParty`).



---



## {{ContextName}} | {{custom | bespoke | vendor name}}



{{One-line scope.}}



### {{AggregateRoot}}



- {{concept}}

- {{concept}} → {{BC | System}} · {{Aggregate}} · {{Entity}}

→ {{BC | System}} · {{Aggregate}} · {{Entity}}



### {{AnotherAggregate}}



- {{concept}}

→ {{upstream}}



---



## {{AnotherContext}} | {{vendor}}



{{Scope note.}}



### {{AggregateRoot}}



- {{concept}}

→ {{System}} · {{Entity}}



<!-- building_blocks: under each ### aggregate, add #### CE compact + stereotypes per bounded-context-template-building-blocks.md -->



Separate tools run — toolset: `context_tools.clean_engineering.clean_engineering:CleanEngineering` action: `guidance` context.fidelity: `modules`

Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.ddd.ddd:Ddd
context:
  fidelity: bounded_context
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Before following the suggested flow, display the tools made available to this chat in your user-visible reply — each tool name and what it is for. Do not only follow them silently or rediscover them by remanifesting.

Tools made available:
- guidance

Suggested flow (repeat and reorder as the story needs):

1. tool: guidance

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.ddd.ddd:Ddd
context:
  fidelity: bounded_context
action: generate
```
.\tools.ps1 run -
