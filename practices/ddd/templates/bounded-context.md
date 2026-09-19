<!--

  Bounded Context Map — tree format



  BC → Aggregate → concept. Links on any level:

  → BC · Aggregate · Entity   (another context; omit leading segments when same BC/aggregate)

  → System · Entity           (external vendor / system of record)



  building_blocks fidelity adds CE compact classes under each aggregate (not shown here).

-->



# Bounded Context Map — {{project_name}}



## Map format

Three levels on the **bounded_context** card: **BC** → **Aggregate** → **concept**.

No `Root`, boundary-member lists, protected-invariant blocks, or `#### Dependencies` sections at this fidelity — those deepen at **building_blocks**.

### Layout

Every context is a top-level `##` section — peers, never nested inside one another. A Shared Kernel is a dependency arc between two contexts, not a section that contains them.

Order the contexts with the system you are building first, then systems of record and vendor systems after it.

### Links

`→ BC · Aggregate · Entity` — cross-context (omit leading `BC` / `Aggregate` when the target shares the same context or aggregate; e.g. `→ · Voucher` inside Customer).

`→ System · Entity` — external system (e.g. `→ Mavenir DEP · engagedParty`).

Put each link on the **concept or aggregate that has the dependency** — not in a global `## Dependencies` section.

### Dependency arcs

For every arc between contexts, record:

| Field | Content |
|---|---|
| **Direction** | Upstream / downstream / mutual — name both sides |
| **What crosses** | Concepts and how they translate at the boundary |
| **Integration** | Concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). "In-process" or "module seam" alone is not enough. |
| **Pattern** | One from the catalogue below — or owner + target date if undecided |

**Relationship patterns (use these names — no ad hoc labels like "loose coupling"):**

- **Shared Kernel** — shared subset; both sides consult on change
- **Customer/Supplier** — one-way; joint acceptance tests at the boundary
- **Conformist** — downstream adopts upstream model
- **Anticorruption Layer** — translate / isolate legacy or foreign model
- **Open Host / Published Language** — published protocol for many consumers
- **Separate Ways** — no integration

External systems of record usually **Separate Ways**, **Conformist**, or **ACL**. Formalize informal internal sharing instead of leaving it unnamed.

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

