# Context-Driven Delivery

Explore informal context into an agreed design, an implementation-ready specification, and working software. You work through **context tools** (`/stories`, `/clean-engineering`, `/ux`, `/bdd`, `/ddd`) and shared **actions** (`/generate`, `/render`, `/validate`, …).

The staged catalog of tools and actions is in `[catalog/workflow.md](catalog/workflow.md)`.

## What you need


| Need                                      | Why                                                                                        |
| ----------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Windows** + PowerShell                  | `setup.ps1` is the bootstrap.                                                              |
| **Python 3.12+**                          | Runtime for the venv and the MCP server.                                                   |
| **Cursor**                                | Setup deploys skills, rules, agents, hooks, and MCP here.                                  |
| **Python extension** (`ms-python.python`) | Language support for generated `.py` and specs.                                            |
| **Draw.io** (`hediet.vscode-drawio`)      | Open and edit `.drawio` story maps and models in the editor.                               |
| **Miro MCP**                              | Required only when you render a map onto a Miro board. Enable the Miro server and sign in. |
| **Git**                                   | Work sessions isolate on a session branch / sibling worktree.                              |


After setup, **approve the project MCP server** when Cursor offers it. That is the CDD tool host written to `.cursor/mcp.json`.

## Get started

From this repository root:

```powershell
.\setup.ps1
```

That run does three things:

1. **Creates or repairs `.venv`** with a system Python 3.12+ interpreter.
2. **Installs Python packages** from `requirements.txt` when they are missing. If that file is absent, setup writes one that matches this checkout (runtime deps plus `mamba` for specs).
3. **Deploys the harness into this checkout** — `install` for Cursor, MCP on, Python templates.

The deploy walk can take a few minutes the first time.

After that, you work in chat. Slash skills (`/stories`, `/generate`, …) carry the matching context tool in their instructions; the agent calls those tools through MCP.

## What setup deploys (and where)

Everything lands under **this repo’s `.cursor/`**, not a second project folder.


| Path                 | What it is                                                                                                           |
| -------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `.cursor/skills/`    | Slash skills: actions, context tools and fidelities, format prompts, tools, `/install`, `/clean-harness`. |
| `.cursor/rules/`     | Repo rules plus per-tool `.mdc` guidance.                                                                            |
| `.cursor/agents/`    | Role agents (Partitioner, Scaffolder, Discoverer, Specifier, Implementer, …).                                        |
| `.cursor/mcp.json`   | Project MCP server that exposes the toolsets.                                                                        |
| `.cursor/hooks.json` | Cursor hooks (dispatch into this repo’s Python).                                                                     |


Source of those files is this repo (`practices/`, `tools/`, `harness/`, `rules/`). Re-run `.\setup.ps1` or `/install` after you change a skill source and want the editor copy refreshed.

VS Code Copilot agents, when you deploy that IDE, live under `.github/agents/`.

## Where work is saved

All defaults can be overridden.

`/start-work-session` names the sprint and records it at the **repository root** under `.sessions/{name}/`. For a non-`main` session it also creates a **sibling git worktree and branch**. It does not create a folder to hold `.context`.

`.context` lives **next to the work** — story maps, scenarios, sketches, and grill answers sit in `{working path}/.context/` wherever that product or slice actually is.

| Place | Holds |
| --- | --- |
| `{working path}/` | Product code and generated language trees. |
| `{working path}/.context/` | Durable artifacts beside that work: `story-map.md`, `story-map.drawio`, scenarios, sketches, `grill-answers.md`, models. |
| `{repo}/.sessions/{name}/` | Session temps at the clone root: `session.md`, model, logs. |
| `{repo}/.sessions/closed/{name}/` | Archived session after `/finish-work-session`. |
| Sibling worktree | Isolated checkout for the session branch (`{abbrev}-{name}` next to the primary clone). |
| `{workspace}/.context/context-index.md` | Which tool owns which durable root. |

Close the session with `/finish-work-session` — that commits the whole worktree.

**Commits.** Call **`/turn`** whenever you want a checkpoint — preferably after each step. Call **`/finish-turn`** when that turn is done. Then **`/finish-work-session`** when the sprint itself is done.

## Context tools

A **context tool** lets you explore, refine, specify, and implement a body of context from one perspective. Each perspective surfaces different decisions: interactions, software structure, observable behavior, domain meaning, or user experience.

Each tool runs at a **fidelity**. Fidelity is the depth of the work: a cheap wide view, then a specification, then working software. Stay at the depth that matches what is known now.

Context tools are **skills**. The umbrella skill is the shared language and rules; a fidelity skill is one depth. Name a CDD agent and let it pick skills, or invoke a tool yourself with the action, fidelity, format, source, and scope.

### /stories

Who does what, in what sequence, and what an actor can observe. Trace delivery from business outcomes to executable acceptance behavior.


| Fidelity           | Skill                       | What it does                                                                                                       |
| ------------------ | --------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `story-map`        | `/stories-story-map`        | Maps Epics, Sub-Epics, Stories, actors, and the walking skeleton while changes are still cheap.                    |
| `scenarios`        | `/stories-scenarios`        | Refines selected Stories into concrete Given-When-Then examples, variations, and observable outcomes.              |
| `acceptance-tests` | `/stories-acceptance-tests` | Turns agreed scenarios into executable acceptance specifications and the production behavior that makes them pass. |


### /clean-engineering

Deep independent modules behind small public seams. Progress from module boundaries through an object model to production code.


| Fidelity  | Skill                        | What it does                                                                                                                 |
| --------- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `modules` | `/clean-engineering-modules` | Defines cohesive module boundaries, narrow public seams, and explicit one-way dependencies.                                  |
| `model`   | `/clean-engineering-model`   | Designs typed classes, responsibilities, operations, invariants, collaborators, and relationships without production bodies. |
| `code`    | `/clean-engineering-code`    | Implements the model as working production code while preserving seams, ownership, and dependency direction.                 |


### /bdd

Domain vocabulary as observable behavior trees and passing tests. Make expected behavior explicit and drive implementation through red-green-refactor.


| Fidelity      | Skill              | What it does                                                                                                    |
| ------------- | ------------------ | --------------------------------------------------------------------------------------------------------------- |
| `behavior`    | `/bdd-behavior`    | Locks the describe/that/with/it hierarchy as test signatures without assertions or production implementation.   |
| `development` | `/bdd-development` | Implements one behavior at a time: write the test, see the correct failure, make it green, and refactor safely. |


### /ddd

Software around business language, boundaries, and rules. Find bounded contexts and aggregates before tactical patterns and integrations.


| Fidelity          | Skill                  | What it does                                                                                                        |
| ----------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `bounded-context` | `/ddd-bounded-context` | Maps where language changes, which aggregates protect invariants, and how contexts depend on one another.           |
| `building-blocks` | `/ddd-building-blocks` | Classifies aggregate roots, entities, value objects, repositories, events, factories, services, and specifications. |
| `tactics`         | `/ddd-tactics`         | Implements the domain model, repositories, events, factories, services, and infrastructure adapters.                |


### /ux

How users navigate, understand, and act. Progress from information architecture through runnable mockups to a production frontend.


| Fidelity         | Skill                | What it does                                                                                             |
| ---------------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| `ia`             | `/ux-ia`             | Maps screens, named regions, navigation, and transitions without prematurely choosing detailed controls. |
| `mockup`         | `/ux-mockup`         | Produces wired greybox screens with concrete controls, states, interactions, and explicit stubs.         |
| `front-end-code` | `/ux-front-end-code` | Builds the real frontend and connects it to production services while preserving agreed UX decisions.    |


## Generate vs render

- `**/generate**` writes the **formal artifact** from source, rules, and examples (story map, scenarios, model, code). Use it when the content does not exist yet, or you are deepening fidelity.
- `**/render**` **re-expresses an artifact you already have** in another format — same meaning, different channel (`markdown` → `drawio` / `miro` / `python` / …). Use it when the map or spec is already on disk and you want a board or a language tree.

`/validate` only reports. `/satisfy` validates, fixes the artifact, and validates again.

## Running skills

```text
/{context-tool} /{action} [format {format}] - {source and scope}
```

The format is optional. If omitted, the tool uses the default for that action.

### Actions

- `**/grill**` — Context-grounded questions; answers go to `grill-answers.md`. Use it when decisions must settle before an artifact can be shaped.
- `**/sketch**` — Grill, draft, persist, and review a rough shape. Cheap exploration, not the formal artifact.
- `**/iterate**` — Grill, generate one small slice, validate, one fix pass. Use it instead of dumping a whole artifact in one shot.
- `**/generate**` — Produce the formal artifact at the selected fidelity.
- `**/render**` — Convert an existing artifact to another format.
- `**/document**` — Neutrally describe an existing system. Reports violations without redesigning them.
- `**/validate**` — Scan and report pass/fail without editing.
- `**/satisfy**` — Validate, fix gaps in the artifact, validate again until clean.
- `**/repair**` — Fix why the context tool produced the violation (context, example, template, or scanner), not only the asset.

Examples:

```text
/stories-story-map /markdown - map the customer onboarding journey from docs/product-notes/

/clean-engineering-model - model the Checkout module from the agreed scenarios

/ddd-building-blocks /markdown - refine the Ordering context and Payment aggregate only

/ux-mockup - create a wired greybox for the Place Order user goal

/bdd-development /code - implement the next Checkout behavior and stop when it is green
```

### Formats

- `**markdown**` — Human-readable maps, specifications, and context documents.
- `**drawio**` — Diagrams opened with the Draw.io extension.
- `**miro**` — Live Miro boards (Miro MCP).
- `**json**` — Structured output for interchange or automation.
- `**html**` — UX mockups and frontend output.
- `**python**`, `**typescript**`, `**javascript**`, `**java**` — Executable models, tests, and implementation.

Supported formats vary by tool:


| Tool              | Formats                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| Stories           | `markdown`, `json`, `drawio`, `miro`, `python`, `typescript`, `javascript`, `java` |
| Clean Engineering | `markdown`, `json`, `drawio`, `miro`, `python`, `typescript`, `javascript`, `java` |
| BDD               | `markdown`, `python`, `typescript`, `java`                                         |
| DDD               | `markdown`, `json`, `python`, `typescript`, `javascript`, `java`                   |
| UX                | `html`, `markdown`, `json`, `drawio`                                               |


## CDD agents

Use an agent when you want it to coordinate the relevant context tools. Name the lenses, or let it choose the smallest useful set from Stories, DDD, UX, Clean Engineering, and BDD.

In Cursor, pick the agent from the chat agent selector (files in `.cursor/agents/`). In GitHub Copilot Chat:

1. **Mention it** — `@Partitioner`, `@Scaffolder`, `@Discoverer`, `@Specifier`, or `@Implementer`, then describe the work.
2. **Select it** in the chat box agent picker. Workspace agents for VS Code are under `.github/agents/`; type `/agents` if they are missing from the selector.

Agents set the role. Skills such as `/stories` or `/ux` are what you invoke inside that role. Add `/bdd` or `/clean-engineering` when tests or implementation constraints are part of the ask.

1. **Partitioner** — Indexes existing content through one or more lenses and extracts source passages without designing. Use it first when knowledge is scattered across documents, code, or tests.
2. **Scaffolder** — Names-only outlines: journeys, boundaries, screens, modules, pending questions. Use it when the overall shape is not yet clear.
3. **Discoverer** — Deepens the scaffold into a coherent whole-solution design without writing detailed specifications.
4. **Specifier** — Turns one increment or sub-epic into scenarios, models, mockups, and test signatures, without production code.
5. **Implementer** — Turns the agreed specification into tested production software for one handed-off slice.

Example prompts:

```text
Index docs/, src/, and tests/ using Stories, DDD, and Clean Engineering. Preserve source passages verbatim and prepare the result for the next stage.

Resolve the whole-solution shape for this product area using Stories, DDD, UX, and Clean Engineering. Omit BDD for now, and hand off one sub-epic to the next stage.

For Checkout, decide which context tools are needed, then produce concrete scenarios, a domain model, a greybox mockup, and BDD signatures without production code.
```

## A short first workflow

1. **`/start-work-session`** — name the session. That creates `.sessions/{name}/` at the repo root and a sibling worktree/branch (unless you stay on `main`).
2. **`/stories /generate story_map`** — walking-skeleton map in markdown as `{working path}/.context/story-map.md`, next to the work itself. **`/turn`**.
3. **`/render drawio`** and/or **`/render miro`** — same map as `.drawio` or a Miro board. **`/turn`**.
4. **`/stories /generate scenarios`** — Given / When / Then on the stories you are specifying. **`/turn`**.
5. **Turn that spec into code**
   - **`/render python`** (or `typescript`, …) when you already have the map/scenarios and want the language channel.
   - **`/stories /generate acceptance_tests`** or **`/bdd /generate development`** when you are producing the executable spec / tests as new work.
   Then **`/turn`**.
6. **`/validate`** the slice you just wrote. **`/satisfy`** if you want the artifact driven to green. **`/turn`**.
7. **`/finish-turn`**, then **`/finish-work-session`**.

Partition source first when you are starting from existing docs. Use `/cdd` when you want every lens at one stage.