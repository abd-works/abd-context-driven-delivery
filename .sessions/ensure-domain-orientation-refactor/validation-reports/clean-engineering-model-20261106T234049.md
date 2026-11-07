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


Judge only the checked format's files (python: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-06 23:40:49 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 68
**Rules with graph hits:** 12
**AI rules in scope:** 27

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

### `model-modules-follow-the-partition`

Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.

Evaluate the current context against this rule (model-modules-follow-the-partition):

### `class-not-property-instance-or-subtype`

Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.

Evaluate the current context against this rule (class-not-property-instance-or-subtype):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/prompt_notify.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\prompt_notify.py#L69): OoadClass `PromptNotify`: Class 'PromptNotify' exposes 10 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `shape-classes-around-resources`

Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.

Evaluate the current context against this rule (shape-classes-around-resources):

### `put-logic-on-the-owning-resource`

Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.

Evaluate the current context against this rule (put-logic-on-the-owning-resource):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.

Evaluate the current context against this rule (hide-inner-details):

### `use-property-not-accessor`

Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (use-property-not-accessor):

### `prefer-class-operations`

Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.

Evaluate the current context against this rule (prefer-class-operations):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/file_manager/file_manager.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\file_manager\file_manager.py#L132): OoadClass `FileManager`: Class 'FileManager' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L23): OoadClass `Granola`: Class 'Granola' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L88): Operation `extensionActivateReachesShowInformationMessage`: Operation 'extensionActivateReachesShowInformationMessage' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [tools/granola/granola.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\granola\granola.py#L85): Operation `write_note_context`: Operation 'write_note_context' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

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

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

Evaluate the current context against this rule (domain-exception-carries-context):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `write-invariants`

Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.

Evaluate the current context against this rule (write-invariants):

### `write-interactions`

Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

Evaluate the current context against this rule (write-interactions):

### `no-redundant-relationship-paths`

Before you add an association, walk the paths already in the cluster. Each real participant gets one canonical link — not parallel wires through types that collapse to the same thing (`Client` and `ClientIdentity`, or `OfferChannel` on **Offer** and again on an event the offer just emitted). In-process payloads reach a participant through the aggregate that owns the act; outbound events carry the identity or routing fact downstream systems need, not a duplicate of context the publisher already holds.

Evaluate the current context against this rule (no-redundant-relationship-paths):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice.js#L20): Parameter `io`: Parameter 'io' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_notify/ide_toast/watch_notice_spec.js](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\tools\prompt_notify\ide_toast\watch_notice_spec.js#L7): Parameter `ms`: Parameter 'ms' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `one-canonical-model-document`

Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

Evaluate the current context against this rule (one-canonical-model-document):

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


---

Model-fidelity judgment by the model validation agent, against the model rules and the code at d6c41b23.

## Judgment — `tools/prompt_notify/.context/prompt-notify-model.md`

### `do-not-invent-parallel-object-models` — Fail
- prompt-notify-model.md:88 `GuidanceAction`, `Generate`, `Sketch`, `PracticeGuidance`, `FidelityGuidance` are redeclared with members harness owns, and the copy has drifted (`open_workspace` no longer exists).

### `hold-state-on-the-object-not-in-parameters` — Fail
- prompt-notify-model.md:95 `GuidanceAction.run(guidance, operation, action)` and `begin(guidance, action)` hand the action its guidance on every call; P-1 made actions read their guidance from the call (`start_call`, `call_session`).

### `model-mirrors-code` — Fail
- prompt-notify-model.md:73 `show_ide_toast(echo, repo)`, but the code is `show_ide_toast(echo)`; `catalog` and `chat_edit_source` are in code but not modelled.

### `write-interactions` — Fail
- prompt-notify-model.md:86 `harness/guidance_actions` is drawn depending on `tools/prompt_notify`, while prompt_notify depends on `harness/agent_tools`, `harness/hooks`, and `harness/installation` (line 32); the model draws a cycle, and the code has it (guidance_actions.py:14 and rule.py:138 import PromptNotify).


### `use-typed-signatures` — Fail
- prompt-notify-model.md:56 the model types `on_pre_tool_use(hook_payload: HookPayload): HookResult`, but prompt_notify.py:110, :118, :132, :147 take and return `dict`; harness/hooks owns `HookPayload` and `HookResult`, so the code keeps an untyped copy of the payload beside the class that owns it.

### Graph hits: confirmed and dismissed

Confirmed: `use-typed-signatures` on `PromptNotify.on_pre_tool_use`, `handle`, `detect_echo`, `detect` (dict in place of `HookPayload`) and on `PromptLog` hook handlers taking `payload: dict`; `limit-operation-parameters` on `Granola.write_note_context` (6 parameters, finding N1 still open); `missing-module-context` on `tools/chat`, `tools/echo`, `tools/file_manager`, `tools/granola`, which have no module-context.md; `keep-classes-single-responsibility` on `PromptNotify`, which also keeps its own catalog of skills and rules scraped from the install folders (finding TL-1, still open).

Dismissed: every hit in `ide_toast/*_spec.js` and `_examples/`; `use-explicit-dependencies` for constructing `Path`; `Chat.list` as a classmethod, which is a lookup factory over saved chats. The code-fidelity rules on `watch_notice.js` (`keep-operations-small-focused`, `provide-meaningful-context`, missing type annotations in plain JavaScript) are left to the code judge.
