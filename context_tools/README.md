# ABD CDD Quick How-To

Navigate context-driven delivery by exploring and refining scattered, informal context into an agreed design, an implementation-ready specification, and working software.

## CDD Is based on the concept of a Context Tool

A **context tool** lets you explore, refine, specify, and implement a body of context from one particular perspective. Each perspective reveals different decisions: interactions, software structure, observable behavior, domain meaning, or user experience.

Each context tool can be run at a specific **fidelity**. Fidelity controls the depth of the work, progressing from a broad and inexpensive view, through a detailed specification, to working software. Select the fidelity that matches what is known now rather than inventing decisions from a later stage.

Context tools are implemented as **skills**. The umbrella skill supplies the perspective's shared language and rules; a fidelity skill supplies the guidance for one depth of work. You can let a CDD agent select these skills, or invoke a context tool directly and state the action, fidelity, format, source, and scope.

### /stories

Defines who does what, in what sequence, and what result an actor can observe. Use it to trace delivery from business outcomes to executable acceptance behavior.

| Fidelity | Skill | What it does |
|---|---|---|
| `story-map` | `/stories-story-map` | Maps Epics, Sub-Epics, Stories, actors, and the walking skeleton while changes are still cheap. |
| `scenarios` | `/stories-scenarios` | Refines selected Stories into concrete Given-When-Then examples, variations, and observable outcomes. |
| `acceptance-tests` | `/stories-acceptance-tests` | Turns agreed scenarios into executable acceptance specifications and the production behavior that makes them pass. |

### /clean-engineering

Structures the solution as deep, independent modules behind small public seams. Use it to progress from module boundaries through an object model to clean production code.

| Fidelity | Skill | What it does |
|---|---|---|
| `modules` | `/clean-engineering-modules` | Defines cohesive module boundaries, narrow public seams, and explicit one-way dependencies. |
| `model` | `/clean-engineering-model` | Designs typed classes, responsibilities, operations, invariants, collaborators, and relationships without production bodies. |
| `code` | `/clean-engineering-code` | Implements the model as working production code while preserving seams, ownership, and dependency direction. |

### /bdd

Turns domain vocabulary into observable behavior trees and passing tests. Use it to make expected behavior explicit and drive implementation through red-green-refactor.

| Fidelity | Skill | What it does |
|---|---|---|
| `behavior` | `/bdd-behavior` | Locks the describe/that/with/it hierarchy as test signatures without assertions or production implementation. |
| `development` | `/bdd-development` | Implements one behavior at a time: write the test, see the correct failure, make it green, and refactor safely. |

### /ddd

Organizes software around business language, boundaries, and rules. Use it to find bounded contexts and aggregates before implementing tactical domain patterns and integrations.

| Fidelity | Skill | What it does |
|---|---|---|
| `bounded-context` | `/ddd-bounded-context` | Maps where language changes, which aggregates protect invariants, and how contexts depend on one another. |
| `building-blocks` | `/ddd-building-blocks` | Classifies aggregate roots, entities, value objects, repositories, events, factories, services, and specifications. |
| `tactics` | `/ddd-tactics` | Implements the domain model, repositories, events, factories, services, and infrastructure adapters. |

### /ux

Examines how users navigate, understand, and act on the solution. Use it to progress from information architecture through runnable mockups to a production frontend.

| Fidelity | Skill | What it does |
|---|---|---|
| `ia` | `/ux-ia` | Maps screens, named regions, navigation, and transitions without prematurely choosing detailed controls. |
| `mockup` | `/ux-mockup` | Produces wired greybox screens with concrete controls, states, interactions, and explicit stubs. |
| `front-end-code` | `/ux-front-end-code` | Builds the real frontend and connects it to production services while preserving agreed UX decisions. |

## Use A CDD Agent

Use one of these agents when you want it to coordinate the relevant context tools for you. Tell the agent which lenses to use, or let it choose the smallest useful set from Stories, DDD, UX, Clean Engineering, and BDD.

### Start An Agent In VS Code

In GitHub Copilot Chat, start a CDD agent in either of two ways:

1. **Mention it in the prompt** - type `@Partitioner`, `@Scaffolder`, `@Discoverer`, `@Specifier`, or `@Implementer`, then describe the work.
2. **Select it in the chat box** - open the agent selector in the GitHub Chat input, choose the agent, then enter the scope and instructions for that role.

Selecting the agent is useful for a sustained session in that role. An `@` mention is useful for directing a specific prompt to a named agent. Workspace agents are deployed under `.github/agents/`; type `/agents` to open the custom-agent configuration menu if they are not visible in the selector.

Skills and agents therefore have different invocation models:

- Mention or select an **agent** to establish the role and working method.
- Invoke or name **skills** such as `/stories`, `/ddd`, or `/ux` within the task given to that agent. Optionally add `/bdd` or `/clean-engineering` when test design or implementation constraints are part of the ask.

1. **Partitioner** - Reads and indexes existing content through one or more context-tool lenses, then extracts the relevant source passages without designing or rewriting them. Use it first when knowledge is scattered across documents, code, tests, or other existing material.
2. **Scaffolder** - Organizes a large or unclear problem into names-only outlines: journeys, boundaries, screens, modules, and pending questions. Use it before detailed design when the overall shape is not yet clear.
3. **Discoverer** - Deepens the scaffold into a coherent whole-solution design. Use it to resolve broad journeys, domain language, information architecture, and module boundaries without writing detailed specifications.
4. **Specifier** - Turns one selected increment or sub-epic into implementation-ready scenarios, domain and object models, UX mockups, and test signatures. Use it when developers need precise contracts but should not write production code yet.
5. **Implementer** - Turns the agreed specification into tested production software using acceptance tests and red-green-refactor. Use it for one handed-off slice after the upstream decisions are settled.

Use prompts such as:

```text
Index docs/, src/, and tests/ using Stories, DDD, and Clean Engineering. Preserve source passages verbatim and prepare the result for the next stage.

Resolve the whole-solution shape for this product area using Stories, DDD, UX, and Clean Engineering. Omit BDD for now, and hand off one sub-epic to the next stage.

For Checkout, decide which context tools are needed, then produce concrete scenarios, a domain model, a greybox mockup, and BDD signatures without production code.
```

## Running Skills With Actions

```text
/{context-tool} /{action} [format {format}] - {source and scope}
```

The format is optional. If omitted, the tool uses the default for that action.

## Choose An Action

- **`/grill`** - Ask context-grounded questions and record the answers. Use it when decisions or contradictions must be resolved before an artifact can be shaped.
- **`/sketch`** - Grill, draft, persist, and review a rough shape before committing to a formal artifact. Use it for cheap, interactive exploration.
- **`/iterate`** - Grill, generate one small slice, validate it, and apply one fix pass. Use it instead of a large one-shot generation.
- **`/generate`** - Produce the formal artifact at the selected action. Use it when the source and decisions are sufficiently settled.
- **`/document`** - Neutrally describe an existing system. It reports violations but does not redesign or fix them.
- **`/validate`** - Scan and report pass/fail without editing.
- **`/satisfy`** - Validate an artifact, fix its gaps, and validate again until clean.
- **`/repair`** - Validate an artifact, fix its gaps, and validate again until clean.

Examples:

```text
/stories-story-map /markdown - map the customer onboarding journey from docs/product-notes/

/clean-engineering-model - model the Checkout module from the agreed scenarios

/ddd-building-blocks /markdown - refine the Ordering context and Payment aggregate only

/ux-mockup - create a wired greybox for the Place Order user goal

/bdd-development /code - implement the next Checkout behavior and stop when it is green
```

## Choose An Output Format

- **`markdown`** - Human-readable maps, specifications, and context documents.
- **`json`** - Structured output for interchange or automation.
- **`html`** - UX mockups and frontend output.
- **`python`**, **`typescript`**, **`javascript`**, **`java`** - Executable models, tests, and implementation in the selected language.

Supported formats vary by tool:

| Tool | Formats |
|---|---|
| Stories | `markdown`, `json`, `python`, `typescript`, `javascript`, `java` |
| Clean Engineering | `markdown`, `json`, `python`, `typescript`, `javascript`, `java` |
| BDD | `markdown`, `python`, `typescript`, `java` |
| DDD | `markdown`, `json`, `python`, `typescript`, `javascript`, `java` |
| UX | `html`, `markdown`, `json` |
