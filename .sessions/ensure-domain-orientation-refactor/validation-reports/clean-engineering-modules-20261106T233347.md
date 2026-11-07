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

**Generated:** 2026-11-06 23:33:47 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 68
**Rules with graph hits:** 12
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

**Graph violations:** 21

- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L185): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L189): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L193): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L197): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L201): Parameter `payload`: Parameter 'payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/extension.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\extension.js#L6): Parameter `context`: Parameter 'context' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L6): Parameter `raw`: Parameter 'raw' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L16): Parameter `folder`: Parameter 'folder' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L20): Parameter `io`: Parameter 'io' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L20): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L20): Parameter `seen`: Parameter 'seen' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L34): Parameter `options`: Parameter 'options' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L48): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L48): Parameter `raw`: Parameter 'raw' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L7): Parameter `ms`: Parameter 'ms' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L11): Parameter `file`: Parameter 'file' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L11): Parameter `message`: Parameter 'message' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L110): Parameter `hook_payload`: Parameter 'hook_payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L118): Parameter `hook_payload`: Parameter 'hook_payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L132): Parameter `hook_payload`: Parameter 'hook_payload' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L147): Parameter `hook_payload`: Parameter 'hook_payload' needs a domain-specific type, not a generic container.

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

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L185): Operation `before_submit_prompt`: Parameter 'payload' in 'before_submit_prompt' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L185): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L189): Operation `before_read_file`: Parameter 'payload' in 'before_read_file' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L189): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L193): Operation `pre_tool_use`: Parameter 'payload' in 'pre_tool_use' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L193): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L197): Operation `subagent_start`: Parameter 'payload' in 'subagent_start' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L197): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L201): Operation `after_agent_response`: Parameter 'payload' in 'after_agent_response' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L201): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L34): Operation `createNoticeWatcher`: Parameter 'options' in 'createNoticeWatcher' is vague.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L34): Parameter `options`: Parameter 'options' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L69): OoadClass `PromptNotify`: Class 'PromptNotify' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L88): Operation `extensionActivateReachesShowInformationMessage`: Operation 'extensionActivateReachesShowInformationMessage' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L48): Operation `format_filing_plan`: Operation 'format_filing_plan' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L34): Operation `createNoticeWatcher`: Operation 'createNoticeWatcher' is 59 lines (max 20).
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L20): Operation `rewriteWhileSlowWatcherOwnsThePath`: Operation 'rewriteWhileSlowWatcherOwnsThePath' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L88): Operation `extensionActivateReachesShowInformationMessage`: Operation 'extensionActivateReachesShowInformationMessage' is 41 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `language-modules-one-section`

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_log/prompt_log.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_log\prompt_log.py#L181): OoadClass `PromptLog`: Module 'prompt_log' module-context has a 'Modules' heading. Language is the opening lines of each # path card — drop ## Modules and do not add ## Language.

Evaluate the current context against this rule (language-modules-one-section):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L85): Operation `write_note_context`: Operation 'write_note_context' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 17

- [X] **ERROR** **[graph rule]** - [tools/chat/chat.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat.py#L42): OoadClass `ChatCommand`: Module folder 'chat' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/chat/chat.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat.py#L66): OoadClass `ChatMessage`: Module folder 'chat' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/chat/chat.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat.py#L91): OoadClass `ChatNotConnectedError`: Module folder 'chat' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/chat/chat.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat.py#L108): OoadClass `Chat`: Module folder 'chat' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/chat/chat_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat_spec.py#L1): OoadClass `_module`: Module folder 'chat' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/echo/_examples/action_inspector/action_inspector.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\echo\_examples\action_inspector\action_inspector.py#L7): OoadClass `ActionInspector`: Module folder 'action_inspector' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/echo/echo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\echo\echo.py#L25): OoadClass `Echo`: Module folder 'echo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/echo/echo_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\echo\echo_spec.py#L1): OoadClass `_module`: Module folder 'echo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L26): OoadClass `PathOutsideRootsError`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L33): OoadClass `SessionFileNotFoundError`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L40): OoadClass `FolderEntry`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L70): OoadClass `Folder`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L94): OoadClass `FileEntry`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L112): OoadClass `FileText`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L132): OoadClass `FileManager`: Module folder 'file_manager' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L23): OoadClass `Granola`: Module folder 'granola' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [tools/granola/granola_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola_spec.py#L1): OoadClass `_module`: Module folder 'granola' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/chat/chat.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\chat\chat.py#L130): Operation `list`: Operation 'list' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L34): Operation `createNoticeWatcher`: Operation 'createNoticeWatcher' uses the unnamed number 300.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L20): Operation `rewriteWhileSlowWatcherOwnsThePath`: Operation 'rewriteWhileSlowWatcherOwnsThePath' uses the unnamed number 5007.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L44): Operation `secondRewriteShowsAndDuplicateDoesNot`: Operation 'secondRewriteShowsAndDuplicateDoesNot' uses the unnamed number 50.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L67): Operation `everyWorkspaceFolderReachesShow`: Operation 'everyWorkspaceFolderReachesShow' uses the unnamed number 50.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L88): Operation `extensionActivateReachesShowInformationMessage`: Operation 'extensionActivateReachesShowInformationMessage' uses the unnamed number 80.

Evaluate the current context against this rule (provide-meaningful-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L132): OoadClass `FileManager`: Class 'FileManager' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L23): OoadClass `Granola`: Class 'Granola' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L20): Parameter `io`: Parameter 'io' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L7): Parameter `ms`: Parameter 'ms' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):


---

# Judgment (modules fidelity) — tools

Judged: tools/prompt_log and tools/prompt_notify `module-context.md`, and the four tools packages with no card.

Graph hits: `missing-module-context` confirmed for tools/chat, tools/echo, tools/file_manager and tools/granola (the `echo/_examples` and spec `_module` entries dismissed). tools/file_manager matters most: space/session (session.py:21), space/repo (repo.py:28) and harness/kanban (ticket.py:30) all import it and file_manager imports space.session back, a cycle no card records. `language-modules-one-section` on prompt_log confirmed. The remaining hits (`use-typed-signatures`, `avoid-vague-parameter-names`, `keep-*`, `limit-operation-parameters`, `prefer-instance-operations`, `provide-meaningful-context`, `use-explicit-dependencies`, `use-intention-revealing-names`) are code-level and outside this fidelity; the `ide_toast/*.js` ones are also untyped JavaScript by design.

## Judgment — `tools/prompt_log/.context/module-context.md`

### `language-opens-the-card` — Fail
- module-context.md:1 `# Modules` heading with a `## tools.prompt_log` / `### Public Seam` / `#### PromptLog` outline instead of a `# tools/prompt_log` card (graph hit confirmed).

### `named-seam-and-constraint` — Fail
- module-context.md:5 no Purpose bullet and no Seam (terms) line; the seam is a heading tree.

## Judgment — `tools/prompt_notify/.context/module-context.md`

### `language-opens-the-card` — Fail
- module-context.md:1 `## Language` section above the `# tools/prompt_notify` card.

### `one-way-deps` — Fail
- module-context.md:25 dependency `installation` is not a module path (harness/installation).

### `public-seam-only` — Fail
- module-context.md:10 documents `GuidanceAction.begin` and module-context.md:16 `show_ide_toast`, internals of other modules and of this one.

