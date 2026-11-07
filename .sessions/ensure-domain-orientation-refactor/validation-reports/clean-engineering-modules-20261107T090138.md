# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/.context/module-context.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-07 09:01:38 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

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

# Judgment (round 3, branch 42ab935c)

Judged the nine cards against this branch's modules rules. Every backticked name was searched in the live code, and every dependency compared with the production imports (specs, `_examples`, `*.feature.py`, and `rule_examples.py` left out except where noted). The graph scanner reported no hits (main's older rules). Following every import, the only remaining dependency cycle among carded modules is Clean Engineering's own three cards (practice, model, model/drawio); the cycles the UX and class-model cards still describe through `harness/graph` and Stories are gone.

## Judgment — `cdd_guidance/practices/clean_engineering/.context/module-context.md`

### `one-way-deps` — Fail
- module-context.md:8 **left from rounds 1–2 (§6, task 12 in progress)** — the practice imports `model` and `model/drawio`, and both import back: `model/python/rules/__init__.py:3`, `model/javascript/rules/__init__.py:3`, and `model/javascript/javascript_class_model.py:23` import the practice, `model/base_class_model.py:737` imports `model/drawio`, and `model/drawio/diagram_node.py:10` imports `model`. This card does not name the cycle, and the modules guidance says to name it rather than the intended direction.

## Judgment — `cdd_guidance/practices/clean_engineering/model/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — says `harness/graph` imports the class model back; nothing in `harness/graph` imports any practice now (decision 16). It lists `harness/agent_tools`, which no file under `model/` imports outside `model/drawio`.

### `deep-module` — Fail
- module-context.md:7 **new** — the seam lists 9 classes, but about 40 of the module's 92 classes are named by other modules: the rule classes (`DoNotInventParallelObjectModels`, `PutLogicOnOwningResource`, `HideInnerDetails`, ...) that `cdd_guidance/practices/clean_engineering/rules/__init__.py:5` imports, the per-language models Stories, DDD, and BDD import, and the diagram layout classes (`DiagramCard`, `DiagramArrow`, `ArrowRouter`, `CardPlacement`) `model/drawio` imports. Keeping the practice's rules in the model's card and the model's draw.io format in a third card puts the practice's internals on two seams.

## Judgment — `cdd_guidance/practices/clean_engineering/model/drawio/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — dependencies leave out `harness/graph` (12 imports, e.g. `model/drawio/rules/__init__.py:5`, the scanners) and `harness/installation` (`scanners/_drawio_base.py:15`).

## Judgment — `cdd_guidance/practices/ux/model/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — "`harness/agent_tools` (*Name*)": *Name* is in `harness/name` (`ux/model/nodes.py:12`). The line leaves out `harness/design_canvas` and `cdd_guidance/practices/stories`, which `model/claude_design/story_canvas.py:17-28` imports, and says `harness/graph` and Stories import this module back, which neither does now. The card describes the old dependency graph.

## Judgment — `cdd_guidance/practices/ux/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — lists `harness/design_canvas`, which only `ux/model` imports, and leaves out `harness/graph` (`ux/graph_practice.py:6`, `rules/screen_rules.py:5`).

## Judgment — `cdd_guidance/practices/ddd/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — gives the class model's draw.io format as part of `cdd_guidance/practices/clean_engineering/model`; it is the separately carded `model/drawio` (`ddd/model/drawio/drawio_aggregate_model.py:24`). Also leaves out `harness/name`.

## Judgment — `cdd_guidance/practices/stories/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — dependencies leave out `harness/name` (7 imports, e.g. `stories/model/miro/nodes.py:13`).

## Judgment — `cdd_guidance/practices/bdd/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — dependencies leave out `harness/name`.

## Passes

`cdd_guidance/practices/ux/story-demo` (TypeScript; the named files and exports exist). Every practice card's `{practice}.instructions` and fidelity slugs exist. Stories imports nothing of UX, as its card says.
