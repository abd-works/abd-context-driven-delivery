# ddd-building_blocks

Use ddd guidance at `building_blocks` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@ddd-bounded_context
@ddd-scaffold

# Contexts

## building_blocks

**Default format:** markdown

**Goal:** Deepen the same context map — under each owning context, add CE compact class detail with DDD stereotypes. Not a separate BB document; added detail on the aggregates already placed in the BC.

| Stereotype | Business question |
|---|---|

| **Entity** | An object defined by its unique identity rather than its attributes, maintaining continuity across state changes over time.|
| **Aggregate** | A cluster of associated domain objects (entities and value objects) grouped together to maintain consistent business rules as a single unit. |
| **Aggregate Root** | The main entity inside an aggregate that acts as the sole gateway, controlling all external access and enforcing consistency rules for the entire cluster. |
| **Value Object** | Fully described by values — interchangeable, replaceable, immutable? Prefer VO unless tracked identity is required. |
| **Repository** | A design pattern that hides database operations, allowing your code to load, save, and query entire aggregates as if they lived in a simple memory collection. How does the business find, store, and retire this aggregate? Collection-style seam only (`add` / `remove` / `update` / `find_by_*`). No repository if there is no independent collection lifecycle. |
| **Factory** | Complex birth / invariants at creation / subtype choice? |
| **Service** | Rare **doer** — only when the operation cannot sit cleanly on a single domain object. Not SOA / application `FooService`. `CheckoutService.placeOrder` is `Cart.checkout`. |
| **Domain Event** | Significant past-tense moment — trigger and consumers as invariants; payload as properties. Facts, not commands. |
| **Specification** | Named, reusable true/false business rule (query / validate / construct)? |

Honour aggregate boundaries from bounded_context; do not redraw by relatedness. Same class shape as clean_engineering — stereotypes layered on. Every source concept classified (or Unresolved) with supporting model content.

**Input traps:** identity by habit; aggregate redrawn by relatedness; VO as Entity; `*Service` as a verb bag (SOA); silent consistency.

**Produce:** Update `bounded-context-map.md` — CE compact blocks + stereotypes under each owning context (`templates/bounded-context-template.md`); keep `#### Dependencies` on each aggregate from bounded_context. Call clean_engineering at **specification**. No tables, brokers, frameworks, or REST endpoints here — infrastructure at **tactics**.

**Rules:**

- **`identity-test-entity-vs-vo`** — Entity vs VO by identity that transcends attributes; prefer Value Object. A type that holds collection state and is the access boundary for that cluster is **Aggregate Root + Entity**, not a Domain Service (`Catalog` is not `<<Service>>` because it "does" selection). Invoice you chase over time is an Entity; an immutable money amount is a Value Object.
- **`every-concept-classified`** — Every source concept classified with supporting model content (or Unresolved); multiple stereotypes per concept are fine. When harvesting from a sketch, every named type in the sketch appears in the model — do not render a handful of classes from a large map.
- **`service-is-homeless`** — DDD Service = a **doer**, and they are **rare**. Use one only when the operation cannot sit cleanly on a single domain object. Not SOA: do not invent `FooService` to park verbs. If `Customer` signs in, that is `Customer.signIn`. `CheckoutService.placeOrder` is `Cart.checkout` (or `Order` born from that). `AuthenticationService.fillEmail` is a screen driver (`screen-interface-not-a-domain-object`). Credentials does not grow `signIn`.
- **`repository-is-collection-lifecycle`** — A Repository exists only when the business finds, stores, and retires that aggregate independently. Do not mint `FooRepository` because every aggregate "should have one." Cart created by checkout and never retrieved as a collection has no CartRepository. Subscription that is an invariant of Subscriber is not a top-level SubscriptionRepository.
- **`shared-identity-is-generalisation`** — When two types share identity and the same core attributes over time (Prospect and Subscriber both *are* a Customer), model a base type and generalisation arrows. Do not flatten them as unrelated entities.
- **`domain-events-past-tense`** — Past-tense domain name; trigger and consumers as invariants; not commands or infra names.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.
- **`hang-deps-on-owning-bc`** — Keep `→` links on the concept or aggregate from bounded_context when deepening **building_blocks**. No global `## Dependencies` parking lot.
- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name at building_blocks carries a tactical tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, `<<Factory>>`, `<<Service>>`, `<<Domain Event>>`, `<<Specification>>`). Bare names are incomplete.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work. Select / port / checkout live on the aggregate that does them, not on a repository. Do not hang someone else’s verbs on a value so it “has behavior” (credentials does not grow `signIn`).
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain objects. The user action is an operation on the aggregate that owns it.
- **`private-method-naming`** — Public operations use `+` and no leading `_`. Private helpers use `-` and a `_` prefix (e.g. `- _deriveOnboardingStep`). `derive*` helpers are private.
- **`no-orphaned-objects`** — Every domain object has at least one relationship (dependency, composition, or association). Unconnected Credentials/Session-style boxes are incomplete. Value objects that are attributes (Money, Usage) sit on their owner — they are not unconnected cards. OnboardingStep connects to Prospect; Billing to the subscriber/subscription that pays.

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