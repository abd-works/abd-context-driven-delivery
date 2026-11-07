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

**Generated:** 2026-11-07 09:00:46 UTC
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

Judged the eight cards against this branch's modules rules. Every backticked name was searched in the live code and every dependency compared with the production imports. The graph scanner reported no hits (main's older rules). `harness/name` and `harness/installer` each hold one class; they were made separate on purpose (decision 22, harness layering), so `no-module-per-class` is not re-reported for them.

## Judgment — `tools/prompt_notify/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:8 **new** — the dependencies name "`harness/installation` (*Destination*, *Installer*, *Skill*)": *Destination* is in `harness/marks`, *Installer* in `harness/installer` (`prompt_notify.py:311`), and `prompt_notify.py` imports no *Skill*; from `harness/installation` it imports only `noCatalog`. The line also lists `harness/hooks` twice and leaves out `harness/name` (`prompt_notify.py:25`). A reader looking for the Installer in `harness/installation` finds nothing.

## Judgment — `tools/prompt_log/.context/module-context.md`

### `seam-names-current-code` — Fail
- module-context.md:6 **new** — dependencies leave out `harness/installation`, which `tools/prompt_log/prompt_log.py` imports.

## Judgment — `tools/chat/.context/module-context.md`

### `deep-module` — Fail
- module-context.md:9 **left from rounds 1–2 (§6)** — 2 of 4 classes (Chat, ChatNotConnectedError) are named by other modules, 50%.

## Judgment — `harness/marks/.context/module-context.md`

### `purpose-before-mechanism` — Fail
- module-context.md:2 **new** — *Mark* opens with "a decorator that marks the operation or class it decorates by setting its flag on it"; the job (install and discovery find what it marks) comes only after the mechanism, which is the order the rule forbids.

### `deep-module` — Fail
- module-context.md:6 **new** — all 5 classes (Mark, OmissionMark, Destination, NamedDestination, Toast) are named by other modules, 100%. The module was cut out in this refactor (decision 22) and is all seam; the measure fails as written. Either hide the base classes behind the marks authors type or record the exception for a module of marks.

## Judgment — `harness/process/.context/module-context.md`

### `deep-module` — Fail
- module-context.md:5 **new** — all 3 classes (RunningProcess, StoppableProcess, ProcessNotStopped) are public, and the seam adds four free functions (`windowless_python_executable`, `console_python_executable`, `detached_creationflags`, `hidden_process_startupinfo`); nothing in the module is hidden.

## Passes

`harness/name`, `harness/installer`, `harness/sub_agent`: names, operations, and dependencies match the code; the cards open with the job a caller hires them for. `harness/installer`'s statement that none of its dependencies imports it holds.
