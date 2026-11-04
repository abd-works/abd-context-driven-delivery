# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 21:13:30 UTC
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

---

# AI judgment

**Artifact:** `harness/kanban/app/.context/module-context.md`, checked against `harness/kanban/app/src/`, `packages/session-board/`, and the installed adapters in `.claude/language-adapters/typescript/`. (The Python module `harness/kanban` was judged in `clean-engineering-modules-20261103T210844.md`.)

| Rule | Verdict | Evidence |
|---|---|---|
| `vocabulary-traces-to-source` | **FAIL** | The card names `BoardNodeAdapter`, `TicketNodeAdapter`, and `BacklogItemNodeAdapter`. No class by those names exists anywhere in the repository; the server side is one generic `cddRoutes` in `src/session-board/cdd-routes.ts` that runs each `CddRoute` from `@cdd/cdd-shared`. `BoardClient`, `TicketClient`, and `BacklogItemClient` do exist. |
| `do-not-invent-terms` | **FAIL** | Same three names: a reader will look for classes that are not there. "/chats/..." routes are named in the Seam, but no `/chats` route exists in `src` or `packages`; chats are read through the `chat` tools (board-client.spec "because the chats are read through cdd"). |
| `do-not-invent-parallel-object-models` | PASS | Clients extend the adapter's objects (`TicketClient extends Ticket`); `board-store.ts` holds page state, not a second board. |
| `domain-nouns-only` | PASS | `app` is a path; the language names the Session Board. |
| `named-seam-and-constraint` | **FAIL** | Seam and Constraint are present, but **Dependencies** leaves out `tools/chat`: the page imports `@cdd/tools/chat/chat` in 3 files. |
| `high-cohesion` | PASS | Every folder serves the one page: board, ticket, backlog-item, chat. |
| `no-module-per-class` | PASS | One module with object folders inside. |
| `single-boundary` | PASS | The Constraint says the app holds no rule and no copy of the board, and the page reads the board again after every action. |
| `deep-module` | PASS (graph agrees) | The seam is a command, two environment variables, and an HTTP API. The page's classes are not imported from outside the app. |
| `abstraction-focus` | WARN | The second paragraph walks the call chain (page client → generated client → route → server adapter → tools), and the Constraint repeats it. Callers of the app need the API and the rule that it holds no state, not the chain. |
| `language-opens-the-card` | PASS | Language is the first two paragraphs. |
| `purpose-before-mechanism` | WARN | The second paragraph leads with "The installer generates each domain object's server adapter", which is how, before saying what a Client is for. |
| `public-seam-only` | WARN | `BoardClient`, `TicketClient`, `BacklogItemClient` are page internals; nothing outside the app types them. |
| `use-typed-signatures` | PASS | Routes take and return the adapter's typed `*Data` shapes, and requests are parsed with Zod. |
| `general-purpose-surface` | PASS | The HTTP API is one POST per tool, the same shape for every object. |
| `temporal-independence` | PASS with note | The Constraint documents the one required order: install, then `npm install`, `npm run build`, `npm start`. |
| `one-way-deps` | PASS | The app depends on the language adapter; nothing in Python imports the app. |
| `extensions-live-with-the-domain` | PASS | The app's own code lives in the app; generated code lives in the install. |
| `low-coupling` | PASS | Imports from Python reach only the adapter (`@cdd/harness/kanban/*`, `@cdd/tools/chat/chat`, `@cdd/cdd-connection`, `@cdd/cdd-shared`). |
| `layer-separation` | PASS | `cddRoutes` is a small mount over generated routes, not a forwarding layer with its own signatures. |

## Failures to fix

1. Replace `BoardNodeAdapter` / `TicketNodeAdapter` / `BacklogItemNodeAdapter` with what exists: the installer-generated routes (`CddRoute` in `@cdd/cdd-shared`) that `cddRoutes` mounts.
2. Remove `/chats/...` from the Seam, or name the chat tools the page actually calls.
3. Add `tools/chat` (through the language adapter) to Dependencies.
4. Warnings: cut the call-chain walk to one sentence on what callers rely on, and drop the page Client class names from the card.
