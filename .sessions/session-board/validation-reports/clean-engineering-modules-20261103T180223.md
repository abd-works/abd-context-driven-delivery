# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 18:02:23 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 20

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `domain-nouns-only`

Name modules after domain concepts or paths, never action verbs or generic `*Model` and `*Runtime` suffixes. A technical container name does not tell callers which business knowledge it owns.

Evaluate the current context against this rule (domain-nouns-only):

### `named-seam-and-constraint`

Name **Seam (terms)** and **Constraint** (what callers must or must not do). At modules do not require a Public API heading — that member dump is **model**.

Evaluate the current context against this rule (named-seam-and-constraint):

### `high-cohesion`

Group classes that share one purpose and the same domain concept, or else unrelated work will keep landing in the same module and every feature ends up editing it.

Evaluate the current context against this rule (high-cohesion):

### `no-module-per-class`

A module groups multiple cohesive classes. One folder or package per class is an anti-pattern unless each class is a genuinely independent subsystem. When sketching with DDD, a small bounded context is usually **one module** with several entities inside — not one module per aggregate root.

Evaluate the current context against this rule (no-module-per-class):

### `single-boundary`

Do not let another module hold, mutate, or duplicate this module’s concept. The two modules will drift, and every rule change has to be found and made in both.

Evaluate the current context against this rule (single-boundary):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

Evaluate the current context against this rule (deep-module):

### `abstraction-focus`

Name *what* the module does for callers, not internal steps or storage. A seam named after its implementation has to be renamed, with every caller updated, whenever the implementation changes.

Evaluate the current context against this rule (abstraction-focus):

### `language-opens-the-card`

Language is the first lines under `# {path}`. Do not add `## Language` or `## Modules`. A section above the cards splits the words from the module they name.

Evaluate the current context against this rule (language-opens-the-card):

### `purpose-before-mechanism`

Open each concept, Purpose, and seam term with the job a caller hires it for. A decorator, merge, mark, or storage choice is how — it never leads. Either say what the caller uses each concept for, or omit them.

Evaluate the current context against this rule (purpose-before-mechanism):

### `public-seam-only`

Document only the public seam and dependencies on other modules. The seam is what a caller types (`@agent_instructions`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`) is an internal — leave it out. Do not document tests, scan reports, or session dumps. Do not put **Sources / context** that only lists files inside the module folder — those are the subject, not a source. Documented internals are misunderstood as public promises, and callers start writing code against them.

Evaluate the current context against this rule (public-seam-only):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

Evaluate the current context against this rule (use-typed-signatures):

### `general-purpose-surface`

Do not shape the seam for one caller’s UI or workflow. The second caller then either needs a near-duplicate operation or has to reshape its data to look like the first caller’s.

Evaluate the current context against this rule (general-purpose-surface):

### `temporal-independence`

Leave the module valid after every public operation. Do not require a call order unless you document it, because an undocumented order fails on the first untested path.

Evaluate the current context against this rule (temporal-independence):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

Evaluate the current context against this rule (one-way-deps):

### `extensions-live-with-the-domain`

Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package. `GraphEpic` lives with Stories, not in Knowledge Graph; otherwise the framework depends on every practice and cannot stay generic.

Evaluate the current context against this rule (extensions-live-with-the-domain):

### `low-coupling`

Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.

Evaluate the current context against this rule (low-coupling):

### `layer-separation`

keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.

Evaluate the current context against this rule (layer-separation):

## AI judgment

Artifacts: `harness/kanban/.context/module-context.md`, `harness/kanban/app/.context/module-context.md`, `harness/kanban/chat-mod/.context/module-context.md`.

| Rule | Result | Evidence |
|---|---|---|
| vocabulary-traces-to-source | pass | Board, Column, Stage, Ticket, FidelityProgress, BacklogItem match the Python classes; the app card's adapter and client names match the generated classes |
| do-not-invent-terms | pass | No second noun for a ticket, an item, or a stage |
| do-not-invent-parallel-object-models | pass | The app card says it holds no copy of the board and reaches it through the generated adapter |
| domain-nouns-only | pass | Paths only |
| named-seam-and-constraint | pass | Each card has Seam (terms) and a Constraint section |
| high-cohesion | pass | Domain, web page, and chat plugin each keep one job |
| no-module-per-class | pass | The app's object folders stay inside one app module |
| single-boundary | pass | Rules and state stay in harness/kanban; the app and mod hold none |
| deep-module | not judged | A class count needs the code graph |
| abstraction-focus | pass | Purposes say what a person gets |
| language-opens-the-card | pass | Language sits directly under each heading |
| purpose-before-mechanism | pass | The new backlog sentence leads with opening the ticket, then where the idea is kept |
| public-seam-only | pass | Only tools, commands, settings, and routes a caller uses |
| use-typed-signatures | pass | No untyped shapes named |
| general-purpose-surface | pass | Starting an item keeps its file for the agent and the board alike |
| temporal-independence | pass | Install before build is stated |
| one-way-deps | pass | chat-mod -> app -> kanban |
| extensions-live-with-the-domain | pass | The adapter mark sits on the domain toolsets |
| low-coupling | pass | The mod reaches the app only through `/api/chats` |
| layer-separation | pass | No pass-through module |

No failures.
