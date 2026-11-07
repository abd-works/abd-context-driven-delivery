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

**Generated:** 2026-11-07 00:32:37 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 53
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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L218): OoadClass `ProjectTicket`: Class 'ProjectTicket' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' exposes 65 public operations (budget ~9). Split responsibilities.

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

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' constructs 'ProjectTicketState' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2138): OoadClass `Worktree`: Class 'Worktree' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1861): Operation `workflow_commit_message`: Operation 'workflow_commit_message' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Operation `note`: Parameter 'payload' in 'note' is vague.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 13

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

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

Evaluate the current context against this rule (state-change-returns-record-or-named-failure):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2044): Operation `close_worktree`: Operation 'close_worktree' raises NoOpenWorktreeError without context; name the rejected rule.

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

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L587): Parameter `value`: Parameter 'value' does not reveal intent.

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

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo#L1): Module `repo`: Module 'repo' splits into many tiny classes (18); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 10

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

Evaluate the current context against this rule (keep-operations-small-focused):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2270): Operation `open_in_worktree`: Operation 'open_in_worktree' swallows a caught failure.

Evaluate the current context against this rule (never-swallow-exceptions):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 16

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

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2205): Operation `dirname`: Operation 'dirname' uses the unnamed number 24.

Evaluate the current context against this rule (provide-meaningful-context):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 17 Python classes of `space/repo` in this call's graph. Dismissed graph hits: `errors-out-of-existence` on `Repo.open`, `git`, `gh`, `commit`, `push_commit`, `write_annotated_tag`, `Worktree.open`, `cursor_path`, `ProjectTicket.close`, `project_item_id`, `set_status`, and `from_number` — each raises a typed error (`RepoConnectError`, `GhConnectError`, `ProjectTicketNotFoundError`, ...) for a missing clone, tool, or issue, which is a broken request; `Repo` and `Worktree` constructing `Path` (values); `value` on `write_text_field` (the field's new text); `Repo.open`, `memory`, `ProjectTicket.from_number`, and `Worktree.open` are factories; `keep-operations-small-focused`, `never-swallow-exceptions`, and `provide-meaningful-context` are code-fidelity rules; `note(payload)` names the git note's JSON body.

## Judgment — `space/repo/repo.py`

### `keep-classes-single-responsibility` — Fail
- repo.py:853 `Repo`: 111 methods, 65 public operations, and 15 properties — running git and gh, the GitHub project and its issues (`tickets`, `create_ticket`, `ensure_issue_type`), branches, worktrees, commits, pushes, tags and notes, and the session, backlog, and board files of a CDD project; the GitHub project and the CDD folders are separate reasons to change from the git clone.
- repo.py:479 `Project`: 14 public operations mixing status and theme options, item ids, text fields, archiving, and linking the repository.

### `hold-state-on-the-object-not-in-parameters` — Fail
- repo.py:926 `git`: a classmethod that takes `root` on every call, although a Repo is made for its root; repo.py:1000 `gh` likewise.

### `do-not-invent-parallel-object-models` — Fail
- repo.py:218 `ProjectTicket`: keeps `data: dict[str, str]` and `project_fields: dict[str, str]` bags beside its typed fields, and `parent_number`/`sub_issue_numbers` as issue numbers instead of the parent and child ProjectTickets; repo.py:872 `Repo._tickets` holds the in-memory issues in a dict keyed by issue number, which `tickets` (repo.py:889) hands to callers as storage (K-F13 partly open).
- repo.py:409 `CliAgentBinding`: doer and judge process ids and a status stored on a git tag in the repo module, beside the session that runs those agents.

### `eliminate-duplication` — Fail
- repo.py:445 `pid_is_alive`: a third liveness check (`os.kill(pid, 0)` or a Windows call) beside `RunningProcess` (harness/hooks/running_process.py), which bug 12 made the one place that checks a process without signalling it.

### `use-explicit-dependencies` — Fail
- repo.py:235 `bind_repo`: a ProjectTicket gets its Repo after construction and every operation goes through `_require_repo`, which raises when it was never set; the ticket should be made with its repo.

### `prefer-instance-operations` — Fail
- repo.py:556 `github_status_option`: a classmethod on Project that takes the option names a Project instance already reads (`status_option_names`), and repo.py:571 `github_theme_option` likewise. (`ProjectTicketState.backlog`, `in_progress`, and `done` are named constructors, which the factory exemption covers.)

### `errors-out-of-existence` — Fail
- repo.py:2044 `close_worktree`: raises `NoOpenWorktreeError` when no worktree is open, an ordinary state for a close; the error also carries no context beyond a fixed message.

### `use-typed-signatures` — Fail
- repo.py:926 `git`: `env: dict[str, str]` and string arguments; repo.py:519 `ticket_rows` returns untyped records of the project's items rather than ProjectTickets.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition` aside from the Session cycle judged in the `space/session` report, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `use-property-not-accessor`, `external-system-interface-is-one-way` (Project wraps the GitHub project and GitHub types do not import it), `limit-operation-parameters` (`workflow_commit_message` builds one message from its parts), `no-redundant-relationship-paths`, `use-consistent-naming`. `Branch` and `Worktree` are objects with their own state (1.9 confirmed); `Commit` is a plain class with `@data_field` properties.
