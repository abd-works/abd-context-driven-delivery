# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


# Graph rule validation

**Generated:** 2026-11-03 20:39:42 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-session-board\.sessions\session-board\edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `model-modules-follow-the-partition`

Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.

Evaluate the current context against this rule (model-modules-follow-the-partition):

### `class-not-property-instance-or-subtype`

Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.

Evaluate the current context against this rule (class-not-property-instance-or-subtype):

### `keep-classes-single-responsibility`

Give each class one reason to change.

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

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

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


# Judgment

Judged on `harness/kanban/.context/kanban-model.md` against `harness/kanban/board.py`, `ticket.py`, `backlog_item.py`, `space/session/session.py`, and the actions, on 2026-11-03. **Result: fails.** The graph checked nothing: it loaded two module nodes and none of the model's classes, so "No graph rule violations" says nothing about the model. The model's own claim that everything not marked Intended "mirrors the code" no longer holds after today's changes.

**Where the model no longer matches the code**

- `Board.active` reads `Session.active_name(repo)`, not `WorkState`. `Board.current()` uses `project_checkout()` (the checkout holding `CDD_PROJECT`), not the folder as given. `Board.folders(path)` is missing.
- `Stage(name, board, actions: list[str])` and `FidelityProgress.done_actions` / `remaining_actions` are step names (`generate`, `validate`, `review`), not action types.
- `Ticket` is missing `move_to(stage, done)` (returns a ticket, or the backlog item a ticket dragged into the Backlog becomes), `finish_review(fidelities)`, `choose_root(path)`, `choose_practice_root(practice, path)`, `use_default_practice_root(practice)`, `root`, `practice_roots`, `session_files()`, and `keep(file)`. `Ticket.next` now reaches back to unfinished fidelities in earlier stages, not only its own stage.
- `BacklogItem.holding` keeps the ticket as `_backlog/<name>/<name>.md`, and the Backlog lists such folders as items.
- `Session` is missing `active_name`, `change_workpath`, `choose_output_root`, `forget_output_root`, `has_chosen_output_root`, and `practice_root`.
- `Review : GuidanceAction` is gone, and so is the Open note calling it a command. Review is `Ticket.finish_review`. `Validate` has gained `rules_of(guidance)`.

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-source` | Pass | Board, ticket, stage, backlog item, fidelity, and session are the code's and the story map's words. |
| `do-not-invent-terms` | **Fail** | The code now says *root* (`Ticket.choose_root`, `root`) for what `Session` calls *workpath* (`change_workpath`), and *practice root* for what `Session` calls *output root* (`choose_output_root`). That is two nouns for one concept, introduced today. |
| `do-not-invent-parallel-object-models` | Pass | One model; `Activity`, `ActionState`, and `StageName` are marked Intended, not parallel copies. |
| `model-modules-follow-the-partition` | Pass | `harness/kanban`, `space/repo`, `space/session`, `harness/guidance`, `harness/guidance_actions`, and `harness/graph` match the module cards. |
| `class-not-property-instance-or-subtype` | Pass | Classes earn their place; Backlog and Stage are subtypes of Column. |
| `keep-classes-single-responsibility` | **Fail** | `Ticket` moves, activates, closes, archives, reviews, chooses roots, lists and reads files, reports violations, builds generate commands, and parses the log (34 public members). Files, reports, and roots are the session's work; the model's own Intended notes move several to `Session`. |
| `shape-classes-around-resources` | Pass | Board, Ticket, Session, and BacklogItem own their state; no service-plus-bag pairs. |
| `put-logic-on-the-owning-resource` | Partial | The ticket reads its session's log itself (`FidelityProgress.from_log`), and root choice goes through `Ticket` into `Session`. The model already says these belong on `Session` (Intended). |
| `hide-inner-details` | Pass | Callers use named operations; the log format stays inside `Ticket` and `FidelityProgress`. |
| `use-property-not-accessor` | Pass with a note | `Ticket.workspace()` returns facts the ticket already holds and could be a property. |
| `prefer-class-operations` | Pass on the model | The model shows none; the code has module functions (`name_of`, `practice_key`, `_files_matching`, `_named_parts_as_wildcards`), which a code-fidelity validate should judge. |
| `use-explicit-dependencies` | Pass with a note | `Board.repo` builds a `Repo` from its own root each time instead of being given one. |
| `external-system-interface-is-one-way` | Pass | No external-system types here. |
| `keep-operations-single-responsibility` | Pass with a note | `Ticket.activate` leaves the old session, opens branch and worktree, and switches the session in one operation; the dialog depends on that. |
| `limit-operation-parameters` | Pass | Domain operations take at most 3; `Session.new` (5) is a factory. |
| `avoid-vague-parameter-names` | Pass | None named `data` or `options`. |
| `errors-out-of-existence` | Pass | Unknown ticket, fidelity, and a path outside the repository raise; ordinary empty cases return empty. |
| `state-change-returns-record-or-named-failure` | Pass | Moves return the ticket or backlog item; refusals are named errors. |
| `domain-exception-carries-context` | Pass | `TicketNotFoundError`, `FidelityNotFoundError`, and `TicketFileError` carry the input. |
| `limit-comments` | Pass | Notes explain constraints, not lines. |
| `write-invariants` | Pass | Board stores no ticket state; a ticket never moves itself; every card is in one column. |
| `write-interactions` | **Fail** | The operations added today have no `->` interactions in the model, so their collaborators (`Session.change_workpath`, `Session.record`) are undrawn. |
| `no-redundant-relationship-paths` | Pass with a note | `Board.wip_limit(stage)` and `Stage.wip_limit` are two ways to the same fact. |
| `use-intention-revealing-names` | Pass | Names say what they are for. |
| `use-consistent-naming` | **Fail** | `move_to` means a column move on `Ticket` and a folder move on `Session`; root, workpath, and output root name the same idea. |
| `eliminate-duplication` | Pass with a note | The three step names are spelled out in `board.STAGE_ACTIONS` and again in `ticket.ALWAYS_ALLOWED` / `ONCE_THERE_IS_OUTPUT`. |
| `one-canonical-model-document` | Pass | One model document; `kanban-model.drawio` draws it. |

**To fix:** bring the model back to the code (the list above), pick one word for the session's folder and one for a practice's folder and use them in both `Ticket` and `Session`, and draw the new operations' interactions. Making the graph read the model's classes, so this rule set can be checked mechanically, is separate work in `harness/graph`.
