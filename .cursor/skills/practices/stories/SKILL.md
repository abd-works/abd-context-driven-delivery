## Overview

Map stakeholder and system interactions as behaviours that deliver a solution. Every later fidelity builds on these behaviours, so the story map must describe operations that named actors perform and results they can observe.

---

## Guidance

**Think hierarchically.** Use **Epics** for business capabilities or end-to-end outcomes, **Sub-Epics** for outcomes within an Epic, and **Stories** for discrete user or system interactions with observable results. Decompose Stories into **Scenarios**, then express each Scenario as **Given**, **When**, and **Then** steps. The hierarchy lets a reader move from the business outcome to the behaviour that implements it without losing traceability.

**Write action-oriented interactions.** At every level, name the actor, action, and subject when the format includes actor metadata; name nodes with a base-form verb and a noun. `Manage Customer Orders` says what the Epic achieves, while `Orders` does not. Keep 4-9 direct children under a node, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because shallow chains and crowded nodes both hide the shape of the work.

---

## Shared rules

- **vocabulary-traces-to-domain-source** — Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.
- **read-all-source-context-in-full** — Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.
- **do-not-invent-requirements** — Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.
- **evidence-distinguishes-observed-inferred-and-intended** — Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

# Stories sketch — match active fidelity

**MUST:** Read all source context in full before drafting or refining. **MUST:** Branch on **mechanical uniqueness** only — split distinct mechanics; do not mint one story per TOC / catalog / requirements row. **MUST:** Do not invent requirements — only behaviours the source describes or the user asks for. See `stories.md`: `read-all-source-context-in-full`, `branch-on-mechanical-uniqueness`, `do-not-invent-requirements`.

Sketch the story hierarchy first, then deepen only as far as the active fidelity needs. Confirm epics and sub-epics (the e2e journey), then drill into exact stories by risk or uncertainty — unique **mechanical** flows first, then scaffold patterns already encountered.

Sketch increments next if there will be more than one.

Then detail groups of related stories together — e.g. stories for a sub-epic in a particular increment. Narrate in e2e flow order.

When detailing stories, start with the main-flow scenario (including domain objects usable for examples); then other scenarios, real example data, etc. Given names only conditions the running system actually checks. When is the domain operation. Then asserts; further outcomes are `And` / `.and()`.

**Unmapped areas** live here as `* approx N–M stories…` lines — not in a separate outline map. Discovery materializes named stories; drop approx lines once those stories are named on the real map.

**Order:** epics → sub-epics → confirming stories + approx gaps → thin-slice order → main-flow scenario → variations / shared setup (`specification`) → tier notes (`engineering` only).

Do **not** tag lines with fidelity markers. Depth is what you fill:

| Fidelity | Fill |
|---|---|
| **discovery** | Epic / SubEpic / named stories + thin-slice; clear approx gaps as you name stories |
| **exploration** | Main-flow Given / When / Then under each confirming story; objects from ExampleFactory fakes; assert public interface. No shared background yet. |
| **specification** | Extra scenarios, shared setup / background; still fake + public interface; values from factories |
| **engineering** | Which tier(s) (`domain` / `client` / `server` / `e2e` / project-specific); not full impl in the sketch |

**Notation:** indent = nesting · `{Actor} --> {Verb Noun}` story · `* approx N–M …` unmapped · `~>` increment · `//` note.

---

## Template

```
{Epic verb-noun}
    * approx N–M total stories
    {Sub-epic verb-noun}
        {Actor} --> {Confirming story verb-noun}
            given {shared setup}                    // specification only
            {main scenario name}
                given {precondition the running system actually checks}
                    and {precondition with object.object.field}
                    and …
                when {the domain operation}
                    and …
                then {observable outcome {object.field=descriptive term}}
                    and {next observable outcome}
            {next scenario name}                    // specification only
                …
        {Actor} --> {Confirming story verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
    {Sub-epic verb-noun}
        * approx N–M more stories (what unmapped work likely includes)
~> Increment 1: {capability outcome}: {Story verb-noun}, {Story verb-noun}, …
```

---

## Example

```
Manage Customer Orders
    * approx 18-22 total stories
    Place New Order
        Customer --> Browse Product Catalog
            browse catalog shows available products
                given a Catalog with published Products
                    and a Customer with an empty Cart
                when the Customer browses the Catalog
                then available Products are listed with price
                    and Product.name and Product.price are shown
        Customer --> Submit Order
            given a Cart with line items and a Payment Method   // specification only
            order accepted for valid cart and payment
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status authorised
                when the Customer submits the Order
                then an Order is created with status placed
                    and an Order.number is returned
            order rejected when payment declined                // specification only
                given a Cart with Items totalling amount.currency
                    and a Payment Method with status declined
                when the Customer submits the Order
                then the Order is rejected with reason payment_declined
                    and the Cart contents are preserved
        * approx 4-5 more stories (cart, address, delivery, review)
    Track Order Status
        * approx 3-4 more stories (pending, shipped, delivered)
    Cancel Order
        Customer --> Request Order Cancellation
        * approx 2-3 more stories (refund, partial cancel, policy)
~> Increment 1: Customer can place a paid order: Browse Product Catalog, Submit Order
```

Use MCP tool: `stories.instructions()`
