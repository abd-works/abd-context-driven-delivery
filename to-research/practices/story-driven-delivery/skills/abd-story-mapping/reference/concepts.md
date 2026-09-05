# Story Mapping — Core Concepts

## What is a story map?

A **story map** is a visual, hierarchical model of how users and systems interact with a product or service. It was popularized by Jeff Patton and is central to the abd.works approach to discovery.

A story map answers three questions:
1. **Who** uses the system? (Actors)
2. **What** are the major capability areas? (Top Level Epics)
3. **How** do users move through those areas, step by step? (Lower Level Epics and Stories)

Story maps are intentionally **not implementation plans**. They describe *outcomes and behaviors*, not tasks, tickets, or technical steps. A good story map can be understood by a product owner, a developer, and a domain expert — all at once.

### Why story map?

A story map is a **collaborative method** to break work down. It provides a structure to guide collaborative thought in order to achieve **shared understanding** — alignment from more than one perspective: the engineering team, the product, and the stakeholders affected by the product. Story maps are useful when a project, initiative, or product is in discovery and the scope of functions, features, and goals needs to be fleshed out.

---

## Actors

An **actor** is anyone (or anything) that interacts with the system. Actors are the *who* behind every story.

| Actor type | Description | Examples |
|---|---|---|
| **User** | A human who uses the system directly | Customer, Administrator, Agent |
| **System** | An external system or automated process | Payment gateway, Email service, Scheduler |


User **actors** are representative description of a segment of customers or users. Before building the map, identify the personas from the available context. For each actor determine their goals and the activities they need to meet those goals — these drive the epics and stories below.

In the story map, actors sit at the **top layer** — each actor's goals drive the epics below them.

---

## Epics

An **epic** is a major **capability area** of the system — a broad theme that groups related user journeys together.

Epics answer: *"What is this area of the product responsible for?"*

- They are not **user stories** — they are containers for flows
- A medium-sized system typically has 3–8 top level epics
- Named in **verb-noun format**: `Manage Customer Orders`, `Track Fleet Vehicles`, `Process Payments`

**Good:** Manage Customer Orders, Process Online Payments. **Weak:** Orders, Backend, Admin.

---

## Epic Hierarchy

Top level epics often have one or more layers of children epics, often called **sub-epics**. Each sub-epic is a **flow or feature area** within that epic — a coherent sequence of interactions that achieves a meaningful outcome.

Sub-epics answer: *"What are the distinct flows or phases within this capability area?"*

- Also named in **verb-noun format**: `Place New Order`, `Review Order History`, `Cancel Order`
- Sub-epics can nest, but depth will likely be shallow — 1–2 levels usually enough.

**Good:** Place New Order, Review Order History. **Weak:** Order flow, Checkout stuff.

---

## Stories

A **story** is a **discrete, observable behavior** — a single thing a user or system does within a flow.

Stories answer: *"What is the specific action or interaction happening here?"*

- Stories are the leaves of the story map
- Each story should be independently testable in principle
- **Verb + noun** (e.g. Place Order, Validate Payment). Put the actor in `story_type`, not in the title.
- Stories are behaviors, not tasks — "call the payments API" is a task; "process payment" is a story.

**Good:** Place Order, Select Delivery Address, Validate Payment. **Weak:** Customer Places Order; Payment Processing.

Prefer what happens over how it is shown — **Show order confirmation** beats **Displaying order confirmation**.

### Story types

| `story_type` | Meaning | Style in diagram |
|---|---|---|
| `user` | Human user | Yellow |
| `system` | External or automated system | Dark blue |
| `technical` | Infra, background jobs, non-visible | Black |

Use **user** and **system** for normal product behavior. **technical** sparingly — only when someone explicitly wants that on the map.

---

## Notes on context capture

If useful detail does not fit a node name, put it in that node's `notes` and cite the source (file, page, section, or `"type": "chat"`). Check `notes` before re-reading raw sources when you continue work on the same map.

---

## Pitfalls for agents

**Assess context coverage and don't fabricate to fill gaps.** See [`../../../reference/handling-incomplete-context.md`](../../../reference/handling-incomplete-context.md) for the shared discipline on checking context coverage across dimensions and surfacing gaps honestly instead of inventing stories or structure.

**Determine new system vs existing system before mapping.** If mapping an existing system, you MUST read the extracted context (ARIA snapshots, screenshots, extraction overview) before writing stories. Use the vocabulary and structure the system already has — page titles, button labels, domain terms from the extraction. Do not invent stories for behaviour that doesn't exist. See [`../../../reference/new-vs-existing-system.md`](../../../reference/new-vs-existing-system.md) for the shared discipline.

**Don't defer analysis the source material supports.** If the source describes how a workflow or entity type works, map it now — gaps are for missing information, not unfinished work.

**Don't add scope the user didn't ask for.** If the user describes one path (e.g., manual onboarding), don't add a second without asking.

---

## Recording context gaps in the story map

Context gaps must be captured **inside the story map output file** (`story-map.md`) so they travel with the map.

**Inline gaps** — when a gap applies to a specific epic, sub-epic, or story, place a `* Gap:` line indented under that node:

```
(E) Direct Mob Combat
    (E) Assign Mob Strategy
        (S) GM --> Select Mob Strategy
        * Gap: Is the strategy list extensible by the GM, or fixed?
    (E) Execute Mob Attack
        (S) System --> Resolve Melee Attack
```

**Map-level gaps** — when a gap applies to the whole map or cuts across multiple areas, place a `## Context Gaps` section at the bottom of the file:

```
## Context Gaps
- No technical input on Foundry VTT module API constraints.
- Single perspective (GM only); no QA or dev viewpoint yet.
```

---

## Iterating the map

Do not treat the map as a one-shot deliverable. Deeper analysis will surface information that invalidates earlier structure — stories split, epics merge, flows reorder. This is expected.

When new context arrives or downstream work (AC, scenarios, tests) exposes gaps, revise the map rather than working around stale structure.

### Depth levels

**Story Map Outline — Breadth pass (Idea Shaping)**

Go wide, not deep. Produce **epics** and **confirming stories** — enough to prove each epic is real and the scope is right.

A confirming story is a short verb-noun name that exercises the epic's key domain nouns. Each epic needs at least two confirming stories.

What you produce: top-level epics; 2+ confirming stories per epic; actors identified per epic; context gaps.

What you do **not** produce: detailed flows, scenarios, or steps; full story decomposition.

When to use: first contact with new context, early discovery, scope alignment, or when the user asks for "just the epics", "breadth pass", "outline", or "idea shaping."

**Level 2 — Increment discovery**

Deepen selected epics into sub-epics and fully decomposed stories. Apply the full rule set. Leave epics the team will not build soon at outline depth.

**Level 3 — Story refinement**

Detail stories for the next delivery increment: acceptance-criteria hooks, failure modes, consolidation notes. Later increments stay at outline or Level 2.
