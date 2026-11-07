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

**Generated:** 2026-11-06 23:25:39 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 109
**Rules with graph hits:** 14
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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo#L1): Module `repo`: Module 'repo' splits into many tiny classes (18); prefer a deep module with a small public surface.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo#L1): Module `repo`: Circular import between 'repo' and 'space' breaks one-way dependencies.

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

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [space/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\context_config.py#L47): Operation `save`: Parameter 'data' in 'save' is vague.
- [X] **ERROR** **[graph rule]** - [space/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\context_config.py#L47): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Operation `note`: Parameter 'payload' in 'note' is vague.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2044): Operation `close_worktree`: Operation 'close_worktree' raises NoOpenWorktreeError without context; name the rejected rule.

Evaluate the current context against this rule (domain-exception-carries-context):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L248): Operation `close`: Operation 'close' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L347): Operation `project_item_id`: Operation 'project_item_id' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L369): Operation `set_status`: Operation 'set_status' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L383): Operation `from_number`: Operation 'from_number' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L915): Operation `open`: Operation 'open' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1200): Operation `write_annotated_tag`: Operation 'write_annotated_tag' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1377): Operation `commit`: Operation 'commit' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2044): Operation `close_worktree`: Operation 'close_worktree' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2098): Operation `push_commit`: Operation 'push_commit' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2180): Operation `open`: Operation 'open' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2188): Operation `cursor_path`: Operation 'cursor_path' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L863): Operation `read_loop`: Operation 'read_loop' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [space/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\context_config.py#L13): OoadClass `ContextConfig`: Class 'ContextConfig' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L218): OoadClass `ProjectTicket`: Class 'ProjectTicket' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' exposes 65 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L204): OoadClass `PracticeSessionOutput`: Class 'PracticeSessionOutput' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' exposes 44 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 15

- [X] **ERROR** **[graph rule]** - [space/handoff/handoff.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\handoff\handoff.py#L60): Operation `handoff_session`: Operation 'handoff_session' is 52 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' is 42 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1269): Operation `ensure_issue_type`: Operation 'ensure_issue_type' is 45 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1377): Operation `commit`: Operation 'commit' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1698): Operation `merge_branch`: Operation 'merge_branch' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Operation `note`: Operation 'note' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1825): Operation `create_ticket`: Operation 'create_ticket' is 35 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1992): Operation `close_branch`: Operation 'close_branch' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2020): Operation `switch_worktree`: Operation 'switch_worktree' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2270): Operation `open_in_worktree`: Operation 'open_in_worktree' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L101): Operation `in_chat_file`: Operation 'in_chat_file' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1187): Operation `record_failure`: Operation 'record_failure' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1219): Operation `keep_log`: Operation 'keep_log' is 40 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1861): Operation `workflow_commit_message`: Operation 'workflow_commit_message' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L588): Operation `new`: Operation 'new' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L797): Operation `switch`: Operation 'switch' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `missing-module-context`

**Graph violations:** 17

- [X] **ERROR** **[graph rule]** - [space/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\context_config.py#L13): OoadClass `ContextConfig`: Module folder 'space' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L26): OoadClass `ChatPointer`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/current_session_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\current_session_spec.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L73): OoadClass `PracticeRootInContextError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L88): OoadClass `SessionNameRequiredError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L98): OoadClass `Loop`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L148): OoadClass `SessionNotFoundError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L156): OoadClass `UnknownPracticeError`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L165): OoadClass `LogEntry`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L204): OoadClass `PracticeSessionOutput`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_diagnostics.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_diagnostics.py#L22): OoadClass `SessionDiagnostics`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_probe.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_probe.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/session_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session_spec.py#L1): OoadClass `_module`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L14): OoadClass `ThrowawayProject`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L46): OoadClass `ProjectCall`: Module folder 'session' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [space/work_state.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\work_state.py#L70): OoadClass `WorkState`: Module folder 'space' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2270): Operation `open_in_worktree`: Operation 'open_in_worktree' swallows a caught failure.

Evaluate the current context against this rule (never-swallow-exceptions):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 33

- [X] **ERROR** **[graph rule]** - [space/handoff/handoff.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\handoff\handoff.py#L31): Operation `for_session`: Operation 'for_session' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/record_decisions/record_decisions.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\record_decisions\record_decisions.py#L30): Operation `for_session`: Operation 'for_session' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L143): Operation `format`: Operation 'format' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L187): Operation `note_text`: Operation 'note_text' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L205): Operation `backlog`: Operation 'backlog' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L209): Operation `in_progress`: Operation 'in_progress' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L213): Operation `done`: Operation 'done' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L404): Operation `github_ref`: Operation 'github_ref' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L556): Operation `github_status_option`: Operation 'github_status_option' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L571): Operation `github_theme_option`: Operation 'github_theme_option' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L915): Operation `open`: Operation 'open' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L922): Operation `memory`: Operation 'memory' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2180): Operation `open`: Operation 'open' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2188): Operation `cursor_path`: Operation 'cursor_path' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2196): Operation `abbrev_repo_name`: Operation 'abbrev_repo_name' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2205): Operation `dirname`: Operation 'dirname' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L42): Operation `of`: Operation 'of' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L53): Operation `taken_from`: Operation 'taken_from' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L78): Operation `serving`: Operation 'serving' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L88): Operation `in_log_line`: Operation 'in_log_line' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L101): Operation `in_chat_file`: Operation 'in_chat_file' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L525): Operation `forget_current`: Operation 'forget_current' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L534): Operation `refresh_current_from_repo`: Operation 'refresh_current_from_repo' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L588): Operation `new`: Operation 'new' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L635): Operation `timestamp`: Operation 'timestamp' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L797): Operation `switch`: Operation 'switch' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L843): Operation `mark_loop`: Operation 'mark_loop' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L863): Operation `read_loop`: Operation 'read_loop' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L30): Operation `close_all`: Operation 'close_all' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L58): Operation `close_all`: Operation 'close_all' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2205): Operation `dirname`: Operation 'dirname' uses the unnamed number 24.

Evaluate the current context against this rule (provide-meaningful-context):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [space/context_config.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\context_config.py#L13): OoadClass `ContextConfig`: Class 'ContextConfig' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' constructs 'ProjectTicketState' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2138): OoadClass `Worktree`: Class 'Worktree' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L26): OoadClass `ChatPointer`: Class 'ChatPointer' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L14): OoadClass `ThrowawayProject`: Class 'ThrowawayProject' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/work_state.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\work_state.py#L70): OoadClass `WorkState`: Class 'WorkState' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L587): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L505): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):


---

# Judgment (modules fidelity) — space

Judged: space/repo, space/handoff, space/record_decisions `module-context.md`, and the missing cards for space/session and the space root (work_state.py, context_config.py).

Graph hits: `one-way-deps` repo↔space is confirmed (repo.py:21 imports space.work_state, repo.py:27 space.session.session; session.py:22 imports space.repo.repo). `deep-module` on space/repo is confirmed by ratio (below), not by the class count it quotes. `missing-module-context` (17) is confirmed for the space root and space/session: Session, ChatPointer and PracticeSessionOutput — the most used concepts in the repository — have no card (space/session/.context holds only session-context.md, a design note). The code-level hits (`errors-out-of-existence`, `prefer-instance-operations`, `keep-*`, `limit-operation-parameters`, `use-explicit-dependencies`, ...) are outside the modules fidelity and left to the code judgment.

## Judgment — `space/repo/.context/module-context.md`

### `named-seam-and-constraint` — Fail
- module-context.md:1 not a `# space/repo` path card ("repo — module context"), with Primary use case, Public API, Mechanism and Rationale sections the template does not have.

### `public-seam-only` — Fail
- module-context.md:39 `## Public API` dumps about sixty members including internals (`find_root`, `checkout_folder`, `primary_root`, `path_from_top`), and module-context.md:73 `## Mechanism` describes `Repo.git`/`Repo.gh` and memory-mode dicts.
- module-context.md:61 documents `space.work_state.WorkState` and module-context.md:63 `space.repo.latest_release.LatestRelease` from another module and a private file.

### `deep-module` — Fail
- module-context.md:25 eight seam terms of 17 classes (47%).

### `one-way-deps` — Fail
- module-context.md:65 Dependencies omit space/session and tools/file_manager although repo.py:27 imports space.session.session and repo.py:28 tools.file_manager; space/session imports space.repo back (session.py:22), and module-context.md:71 lists space/session as a consumer, so the card documents only half of a cycle.

### `do-not-invent-parallel-object-models` — Fail
- module-context.md:7 `ProjectTicket` / `ProjectTicketState` beside harness/kanban's `Ticket` keep a second ticket model; repo.py:1110 `Repo.current_session` returns a Session, so Repo also answers for the session module (1.11 / K-F13 still open).

### `do-not-invent-terms` — Fail
- module-context.md:25 seam term `CliAgentBinding` carries a banned word (binding); the class is a doer/judge CLI record on a tag and should be named for that.

Passes: `Repo.current()` is the `@tool_subject` loader (repo.py:879) and the five repo tools take no repo path (repo.py:1974-2098), as the card says.

## Judgment — `space/handoff/.context/module-context.md`

### `named-seam-and-constraint` — Fail
- module-context.md:1 "handoff — module context" with Purpose/Seam/Dependencies/Mechanism headings instead of a `# space/handoff` card.

### `public-seam-only` — Fail
- module-context.md:16 `## Mechanism` describes how `handoff_session` expands and how `write_handoff` copies the file — internals.

### `one-way-deps` — Fail
- module-context.md:13 omits harness/installation and harness/mcp (handoff.py:13-15) and depends on `harness.guidance_actions.load_document`, a free function reached past that module's seam.

### `no-module-per-class` — Fail
- module-context.md:7 one class, one toolset, 100% public; handoff writes into the session folder through `Session.new_handoff_path`, so it is session behaviour kept in its own package.

## Judgment — `space/record_decisions/.context/module-context.md`

### `named-seam-and-constraint` — Fail
- module-context.md:1 "record_decisions — module context", not a path card; module-context.md:15 `## Mechanism` section.

### `one-way-deps` — Fail
- module-context.md:13 omits harness/installation and harness/mcp and reaches `harness.guidance_actions.load_document` past its seam.

### `no-module-per-class` — Fail
- module-context.md:7 one class, 100% public.
