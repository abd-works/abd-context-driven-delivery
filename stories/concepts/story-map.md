---
fidelity: [shaping, discovery]
---

# Story Map — Core Concepts

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
- **Aim for 4–7 top level epics.** Fewer than 4 usually means an epic is hiding two unrelated capability areas; more than 7 usually means a "capability area" has been split into activities that belong as sub-epics.
- Named in **verb-noun format**: `Manage Customer Orders`, `Track Fleet Vehicles`, `Process Payments`

**Good:** Manage Customer Orders, Process Online Payments. **Weak:** Orders, Backend, Admin.

---

## Epic Hierarchy

Top level epics often have one or more layers of children epics, often called **sub-epics**. Each sub-epic is a **flow or feature area** within that epic — a coherent sequence of interactions that achieves a meaningful outcome.

Sub-epics answer: *"What are the distinct flows or phases within this capability area?"*

- Also named in **verb-noun format**: `Place New Order`, `Review Order History`, `Cancel Order`
- **Aim for 4–7 sub-epics per epic.** Fewer means the epic may be too small to warrant an epic at all; more means the epic is trying to be two epics.
- Sub-epics can nest, but depth will likely be shallow — 1–2 levels usually enough for anything but really large systems.

**Good:** Place New Order, Review Order History. **Weak:** Order flow, Checkout stuff.

---

## Stories

A **story** is a **discrete, observable behavior** — a single thing a user or system does within a flow.

Stories answer: *"What is the specific action or interaction happening here?"*

- Stories are the leaves of the story map
- Each story should be independently testable in principle
- **Verb + noun** (e.g. Place Order, Validate Payment). Put the actor in `story_type`, not in the title.
- Stories are behaviors, not tasks — "call the payments API" is a task; "process payment" is a story.
- **Aim for 4–7 stories per sub-epic.** Fewer means the sub-epic is likely a story in disguise; more means the sub-epic is a mini-epic that should split.

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

**Assess context coverage and don't fabricate to fill gaps.** See handling-incomplete-context reference for the shared discipline on checking context coverage across dimensions and surfacing gaps honestly instead of inventing stories or structure.

**Determine new system vs existing system before mapping.** If mapping an existing system, you MUST read the extracted context (ARIA snapshots, screenshots, extraction overview) before writing stories. Use the vocabulary and structure the system already has — page titles, button labels, domain terms from the extraction. Do not invent stories for behaviour that doesn't exist.

**Don't defer analysis the source material supports.** If the source describes how a workflow or entity type works, map it now — gaps are for missing information, not unfinished work.

**Don't add scope the user didn't ask for.** If the user describes one path (e.g., manual onboarding), don't add a second without asking.

---

### Modes

Story mapping has **two modes**. Pick one; both are legitimate.

**Outline mode — breadth first**

Go wide, not deep. Produce **epics**, **sub-epics** (where obvious), and **confirming stories** — enough to prove each epic is real and the scope is right.

**Formatting:** epic, sub-epic, story, and actor names are plain text — never wrap them in backticks.

A confirming story is a short verb-noun name that exercises the epic's key domain nouns. Each epic needs at least two confirming stories.

Drill deeper **only** on ambiguities surfaced by a grill-me session — do not proactively decompose everything. Unresolved ambiguities become recorded gaps.

For each epic and each sub-epic, also produce an **approximate total story count** — an estimate of how many stories the unmapped work is likely to yield, based on the complexity signals available (breadth of behaviour, number of actors, integrations, edge cases hinted at). This is a rough sizing signal, not a commitment.

**Estimate syntax** (markdown outline):

```
(E) Move money
    * approx 22-27 total stories
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        * approx 2-3 more stories (various transfer detail entry and validation)
```

- Epic line: `* approx <range> total stories`
- Sub-epic line: `* approx <range> more stories (<brief notes>)`
- Estimates are stored on the epic/sub-epic node as `estimate` in the model and optional `estimate` in JSON.

What you produce: epics; sub-epics where obvious; 2+ confirming stories per epic; approximate total story count per epic and per sub-epic; actors on confirming stories; scope boundary; context gaps.

What you do **not** produce: full decomposition of every branch; detailed flows or scenarios.

When to use: first contact with new context, scope alignment, or when the user asks for "outline", "breadth pass", or "idea shaping".

**Complete mode — every story decomposed**

Decompose the map fully: every epic → sub-epics → stories, with the full rule set applied to every branch. No branch left at outline depth.

When to use: the map will drive downstream work (discovery, exploration, specification) and every branch must be usable.

**Discovery mode is often scoped.** Instead of running across the whole map, restrict the run to a subset — most commonly the **next thin slice or increment**.
