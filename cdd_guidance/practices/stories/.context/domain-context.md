# Stories domain

A **story map** describes what a system does for the people and systems that use it, as a hierarchy everyone can read: epics, the sub-epics nested under them, and the stories in each. Each story is then specified by **scenarios** written as Given / When / Then **steps**, with **examples** holding the concrete values. **Increments** (thin slices) cut across the map and say which stories ship together. The classes, their fields, and their operations are in `practices/stories/model/.context/story-model.md`; this document explains the domain terms and the decisions behind them.

## Terms

- **Story map** — the whole hierarchy for one product or system. It holds epics, increments, and the examples shared by every story. Code: *StoryModel*.
- **Epic** — a named area of behaviour, in verb-noun form. An epic nested under another epic is a **sub-epic**; it is the same concept at a deeper level, so there is one *Epic* type and depth is its parentage. An epic can carry an **estimate** for stories not yet mapped ("approx 2-3 more stories").
- **Story** — one thing an actor does or the system does in response, in verb-noun form. A story is a **user** story, a **system** story, or a **technical** story (*StoryType*). It names its actors, the domain terms it uses, and the evidence it was taken from.
- **Background** — the Given steps every scenario of a story (or of one scenario) starts from.
- **Scenario** — one concrete path through a story: preconditions, the trigger, and the observable outcome. A scenario with an examples table is an outline, run once per example. A When after a Then starts the next run of the same scenario.
- **Step** — one Given, When, or Then line. An And or But continues the step before it and keeps its step type. A step names the domain concepts and values it uses; the capitalised concepts are the domain classes it reaches.
- **Example** — a named set of values a step uses, shared at the scope that owns it: a background, a scenario, an epic or sub-epic, or the whole story map.
- **Increment** — a thin slice: a name, the outcome it delivers, slicing notes, the decision it asks for, and the stories in it. A story still belongs to its epic and records the increment it ships in.

## Where a story map lives

- `story-map.md` is the map as a markdown outline. Scenario markdown sits beside it (`scenarios/*.md`, `*_story.test.md`, and similar), and increments are in `thin-slicing.md` (or `thin-slice.md`, `thin-slices.md`, `increments.md`). `StoryModel.load(folder)` reads all three, and `story-graph.json` instead when no `story-map.md` sits in the folder or above it.
- Story tests are the map written as code: one folder per epic, one story file per sub-epic that has no sub-epics of its own (`{sub_epic}_story.test.ts`, `.test.js`, `.test.py`, or `{SubEpic}Story.java`), each story a `story(...)` block holding its `scenario(...)` blocks; Java writes each story as a doc comment. Shared examples sit in an `examples/` folder at the lowest folder that shares them.
- Draw.io and Miro diagrams show the map down to stories, with increments as thin-slice lanes (draw.io) or a table (Miro).

## Decisions

- **One model, many formats.** Every format is a subclass of the same story map, so a diagram, a markdown map, and a test tree are always the same hierarchy. A format converts by copying another map into its own node types, then writing it. Diagrams stop at stories; markdown, JSON, and code carry scenarios, steps, and examples.
- **Story tests keep their code.** When a story map is read from code, each story, background, scenario, and step keeps the code it was written with. Rendering back into the same language writes an unchanged node exactly as it was read; rendering with the previous tree gives each node without code in this language the code of the node with the same name. A regenerated test tree therefore never loses the step bodies someone wrote.
- **The story map is part of the knowledge graph.** Every node is a graph node. The graph reads the TypeScript story tests in a project, or its story maps when there are none, and records each step's links to the operations it calls and each example's links to the classes and properties it shows (`stories-cross-practice-relationships.md`). UX screens record which stories, scenarios, and steps they show.
- **Rules run on the model, not on a file format.** The story-map, scenario, and acceptance-test rules in `practices/stories/rules/` read the nodes on the graph, so one rule covers every format and language.
