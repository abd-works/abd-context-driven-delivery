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

**Generated:** 2026-11-07 09:00:34 UTC
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

Judged the eight cards against this branch's modules rules (`cdd_guidance/practices/clean_engineering/clean_engineering.md`, including `seam-names-current-code`). Every backticked class, operation, and MCP operation on these cards was searched in the live code; every listed dependency was compared with the imports the production files actually make (specs, `_examples`, and `*.story.shared.py` left out). The graph scanner reported no hits (it runs main's older rules).

## Judgment — `.context/module-context.md`

### `one-way-deps` — Fail
- module-context.md:33 **new** — the `cdd_guidance` card says "nothing here imports space back", but `cdd_guidance/practices/agent_bdd/agent_bdd_common.py:542` imports `space.session.session` and `space.session.sessions` (`_session_named`), while `space/session` imports `cdd_guidance/actions`. At the level of these area cards, space and cdd_guidance now depend on each other, and the card hides it.

### `seam-names-current-code` — Fail
- module-context.md:20 **new** — the `tools` dependencies leave out `harness/guidance` (`tools/prompt_notify/prompt_notify.py:71, :83`), `harness/installer` (`prompt_notify.py:311`), and `harness/name` (`prompt_notify.py:25`, `tools/granola`). A card that lists fewer dependencies than the imports make tells the reader the module can change more freely than it can.

### `public-seam-only` — Fail
- module-context.md:29 **new** — `cdd_guidance/patterns` (21 production files: LERN, MERN, CDD web domain access, Claude Code mod graph overlays and rules) has no card and rolls up into a card kept in the repository root's file. The modules guidance keeps a parent's card file only for a folder that only groups modules; `cdd_guidance` holds the patterns' classes directly, so it needs its own `cdd_guidance/.context/module-context.md` (or the patterns one), or the rollup point is a file nobody opens when working in `cdd_guidance/`.

## Judgment — `space/.context/module-context.md`

### `do-not-invent-terms` — Fail
- module-context.md:4 **left from rounds 1–2 (§9)** — "release" (`.sessions/{release}/`, `WorkState.release`, `release_folder`) is still a third name for the session folder beside *session* and *workpath*.

## Judgment — `space/session/.context/module-context.md`

### `use-typed-signatures` — Fail
- module-context.md:20 **new** — the published `session.files` (`space/session/session.py:321`) returns `dict[str, dict[str, dict[str, list[FileEntry]]]]`, keyed by practice, fidelity, and format names. That is the copy `do-not-invent-parallel-object-models` names (a dict holding one field from each member) on a published seam; the caller has to know the three key spaces. Hand back the practices (`session.practices[...]`), whose *FidelitySessionOutput* already holds the declared files.

### `seam-names-current-code` — Fail
- module-context.md:24 **new** — dependencies leave out `harness/installer` (`space/session/session_diagnostics.py:35`).

## Judgment — `space/repo/.context/module-context.md`

### `deep-module` — Fail
- module-context.md:11 **left from rounds 1–2 (§6)** — 5 of 12 production classes are named by other modules (Repo, Branch, Commit, Git, Worktree), 42%, over the 40% limit.

## Judgment — `tools/file_manager/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:2 **new** — "`session.file_manager` is the same object": *Session* has no `file_manager`; the file manager is `session.session_files.file_manager` (`space/session/session_files.py:23`).

### `deep-module` — Fail
- module-context.md:9 **left from rounds 1–2 (§6)** — 5 of 7 classes are public (FileManager, Folder, FileEntry, FileText, PathOutsideRootsError), 71%.

## Passes

`space/kanban`, `tools/echo`, `tools/granola`: every named operation exists with `@mcp`/`@skill`, dependencies match the imports, and the cards open with language and job. `space/kanban` has 7 of 48 classes public (15%). Every MCP operation named on these eight cards exists and carries the mark that publishes it.
