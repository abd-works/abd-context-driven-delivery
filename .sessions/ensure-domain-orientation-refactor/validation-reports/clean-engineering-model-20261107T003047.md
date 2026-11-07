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

**Generated:** 2026-11-07 00:30:47 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 45
**Rules with graph hits:** 8
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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L204): OoadClass `PracticeSessionOutput`: Class 'PracticeSessionOutput' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' exposes 44 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L26): OoadClass `ChatPointer`: Class 'ChatPointer' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L477): OoadClass `Session`: Class 'Session' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/session/throwaway_project.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\throwaway_project.py#L14): OoadClass `ThrowawayProject`: Class 'ThrowawayProject' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L588): Operation `new`: Operation 'new' takes 7 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L797): Operation `switch`: Operation 'switch' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' takes 6 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L863): Operation `read_loop`: Operation 'read_loop' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' raises on an empty or missing value; return a quiet result instead.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L505): Parameter `value`: Parameter 'value' does not reveal intent.

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

- [X] **ERROR** **[graph rule]** - [space/session/chat_pointer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\chat_pointer.py#L101): Operation `in_chat_file`: Operation 'in_chat_file' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L885): Operation `append_log`: Operation 'append_log' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1187): Operation `record_failure`: Operation 'record_failure' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/session/session.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\session\session.py#L1219): Operation `keep_log`: Operation 'keep_log' is 40 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 15

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

Evaluate the current context against this rule (missing-module-context):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 15

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

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 13 Python classes of `space/session` in this call's graph (specs left out; `throwaway_project.py` is spec support). The folder-level graph shows no other module, so the module dependencies below were confirmed from the imports. Dismissed graph hits: `missing-module-context` (a modules rule); `Path` constructed in `ChatPointer`, `Session`, and `ThrowawayProject` (values); `value` on the `Session.name` setter; `Session.new`, `load`, `from_file`, `ChatPointer.of`, and `PracticeSessionOutput.load` are factories, which the factory exemption and the parameter exemption cover; `keep-operations-small-focused` is a code rule; `read_loop` raising `ValueError` when a loop is missing is judged under `domain-exception-carries-context` below.

## Judgment — `space/session/session.py`

### `keep-classes-single-responsibility` — Fail
- session.py:477 `Session`: 97 methods, 44 public operations, and 24 properties — the session folder and its moves (`move_to_closed`, `move_to_archive`, `move_to_backlog`, `reopen`), its files (`files`, `folder_files`, `read_file`, `keep_file`), the session log (`log_action`, `log_agent_tool`, `log_tool`, `log_note`, `log_guidance_action`, `log_line`, `record_failure`, `log_error`, `append_chat`, `keep_log`, `record`), loops (`mark_loop`, `read_loop`, `loop_at`, `loop`), the current-session registry, and its practices; the session log and the session folder are missing classes.
- session.py:204 `PracticeSessionOutput`: 13 public operations and 18 properties covering the practice's folders and root, its saved format, its graph, enabling, validation logging, and each fidelity's outputs.

### `prefer-instance-operations` — Fail
- session.py:555 `current`: a classmethod over the class-level `_current_by_project` dict (session.py:481); `forget_current` (session.py:525), `refresh_current_from_repo` (session.py:534), `switch` (session.py:797), `mark_loop` (session.py:843), `read_loop` (session.py:863), and `append_log` (session.py:885) are classmethods that act on that global current session, so every caller that does not hold a session reaches the one saved as current.

### `hold-state-on-the-object-not-in-parameters` — Fail
- session.py:424 `output_paths_of`: PracticeSessionOutput takes one of its own fidelities as a parameter, as do session.py:436 `files_of` and session.py:445 `has_output_of`; each fidelity in the session should answer its own outputs and files (known open item).
- session.py:885 `append_log`: takes `conversation_id`, `transcript_path`, and `transcript_lines` as three strings beside the note, loop, and paths, and session.py:843 `mark_loop` takes the same three, although `ChatPointer` now models that pointer (P-24 partly done).
- session.py:797 `switch`: four location values (`name`, `workpath`, `repo_path`, `session_path`) are passed to a classmethod instead of switching a session object.

### `do-not-invent-parallel-object-models` — Fail
- session.py:295 `root_node_name`: PracticeSessionOutput publishes its graph root's name as a string beside `graph`.
- session.py:938 `saved_current_session`: writes the current session to `WorkState` and again through `harness.hooks.session_logs.SessionLogs` to `.sessions/_active`, so the current session is stored twice.

### `write-interactions` — Fail
- session.py:441 `files_of`: PracticeSessionOutput calls `self._session._worked_on_files`, and session.py:449 `has_output_of` reads `self._session._repo`; it reaches into Session's private members instead of asking through named operations.

### `model-modules-follow-the-partition` — Fail
- session.py:22 `Repo`: `space/session` imports `space.repo.repo.Repo` at module level, and `space/repo/repo.py:27` imports `Session` back, so the two modules depend on each other; `space/session` also imports `harness.graph`, `harness.guidance`, `harness.hooks`, `harness.mcp`, and `harness.installation`, while those harness modules import `space.session`, so the space and harness layers are not one-way.

### `domain-exception-carries-context` — Fail
- session.py:874 `read_loop`: raises bare `ValueError` with a message when no loop exists, instead of a typed session exception carrying the loop number.

### `use-typed-signatures` — Fail
- session.py:1111 `log_agent_tool`: `tool_input: dict`; session.py:1118 `log_tool` likewise.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `use-property-not-accessor`, `use-explicit-dependencies` (beyond the global current session judged above), `external-system-interface-is-one-way`, `errors-out-of-existence`, `no-redundant-relationship-paths`, `use-consistent-naming`. PracticeSessionOutput keeps the chosen format (`keep_format`, `use_kept_format`) and its root on itself (P-5/P-6 confirmed).
