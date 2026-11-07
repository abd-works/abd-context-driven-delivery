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

**Generated:** 2026-11-07 09:07:12 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 7
**Rules with graph hits:** 2
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

- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\ticket.py#L57): OoadClass `Ticket`: Class 'Ticket' exposes 13 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [space/kanban/backlog_item.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\backlog_item.py#L36): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\board.py#L166): Operation `column`: Operation 'column' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/kanban/board.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\board.py#L213): Operation `practice`: Operation 'practice' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\ticket.py#L72): Operation `load`: Operation 'load' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\ticket.py#L129): Operation `progress_of`: Operation 'progress_of' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/kanban/ticket.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\kanban\ticket.py#L275): Operation `move_to`: Operation 'move_to' raises on an empty or missing value; return a quiet result instead.

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

---

# AI judgment (round 3, model fidelity, `space/kanban` Python: `__init__`, `backlog_item`, `board`, `report`, `ticket`)

Each finding says **new** or **left** (from rounds 1–2, citing `clean-engineering-validation.md`). The TypeScript app under `space/kanban/app` was not judged.

Graph hits:
- `keep-classes-single-responsibility` on `Ticket` (13 operations): dismissed — the operations are the ticket's own lifecycle (activate, leave, move, close, archive) and its MCP faces; Ticket is down from 73 members to 14 operations and its copies are gone. FidelityProgress, which the scanner did not flag, is the class that still does another object's job (below).
- `errors-out-of-existence` on `Ticket.load`, `BacklogItem.load`, `Board.column`, `Ticket.progress_of`, `Ticket.move_to`: dismissed — each refuses a name the caller supplied that the board does not have, with a named error (`TicketNotFoundError`, `ColumnNotFoundError`, `FidelityNotFoundError`, `NotAStageError`). `Board.practice`: dismissed as a rule hit, but the operation is dead (below).

## Judgment — `space/kanban/ticket.py`

### `do-not-invent-parallel-object-models` — Fail
- ticket.py:399 `FidelityProgress.ticket`: a data field holding the ticket's name as a string, beside the `Ticket` the progress holds, and `practice` (:423) is a string copy of `fidelity.practice_guidance.key`, and `fidelity_slug` (:405) a copy of `fidelity.slug` while `fidelity` (:411) is also sent in full. Decision 19 gives references `@data_field(reference=True)`; these three are the `*_name` copies the rule names (left, §2 / K-F21).

### `no-redundant-relationship-paths` — Fail
- ticket.py:187 `Ticket.next_fidelity`: sent under `next` as a whole FidelityProgress, the same object `progress` (:118) already sends in its list, so every ticket carries one fidelity's progress twice and a client can read two copies that disagree after an update. Decision 19 says a second path to an owned child is a reference. `Board.active` (board.py:162) sends a whole Ticket that a column also sends (new).

### `keep-classes-single-responsibility` — Fail
- ticket.py:361 `FidelityProgress`: about 28 members. Besides a fidelity's progress through its stage it works out which report answers which rule (`rules_answered_by` :552, `rule_descriptions` :559, `earlier_fidelities` :547, `_latest_report_in` :577, `_has_newer_report` :583) and holds `session` and `repo` for `ReportFile`; that is the fidelity's job (left, §5 / P-22).

### `hold-state-on-the-object-not-in-parameters` — Fail
- ticket.py:524 `finish_review`: a FidelityProgress hands its own slug to its ticket (`self._ticket.progress_of(self.fidelity_slug)`) so the ticket can search its stages and build it again (left, P-4 pattern).
- ticket.py:375 `FidelityProgress.from_log(fidelity, stage, entries, ticket)`: `entries` is `ticket.session.log.entries`, state the ticket argument already holds, passed beside it (new, low).
- ticket.py:218 `activate`: the ticket holds its own `Branch` (`self.branch()`) but calls the Repo's MCP faces with its name, `repo.switch_branch(self.name)`, `repo.switch_worktree(self.name)`, and `leave` calls `repo.close_branch(self.name)` (:242), so Repo looks the branch up again from a string (new).

### `use-consistent-naming` — Fail
- ticket.py:523 `finish_review`: the review line names the practice by its class (`type(...).__name__`) where action lines name it by key, which is why `LogEntry.names` matches both (left, §4).

## Judgment — `space/kanban/board.py`

### `do-not-invent-parallel-object-models` — Fail
- board.py:399 `Help`: a bag of a few of its subject's answers — `overview`, `guidance`, `rules` copied from the practice or fidelity — sent beside `practice` and `fidelity`, which are themselves sent in full (left, §2 / K-F20).

### `hold-state-on-the-object-not-in-parameters` — Fail
- board.py:200 `help(slug)`: the tile that asks already shows the fidelity, but passes its slug so the board searches every practice for it (left, P-28).

### `put-logic-on-the-owning-resource` — Fail
- board.py:446 `Help.href`: the board builds the forge page address and keeps the list of fidelities the forge has no page for (`FIDELITIES_WITHOUT_PAGE`, :38); the catalog generator, which publishes the forge, owns which pages exist, so a page added or removed there is not seen here (new, low).

### `no-legacy-api-after-refactor` — Fail
- board.py:213 `practice(key)`: no production caller (left, §7 dead code "`Board.practice`").

## Judgment — `space/kanban/report.py`

### `do-not-invent-parallel-object-models` — Fail
- report.py:27 `ReportRule`: holds a rule's slug as `name`, its body as `description`, and its fidelity as a slug string, all copied from the `Rule` and `FidelityGuidance` objects; the descriptions come from `FidelityProgress.rule_descriptions`, a dict holding one field of every rule (new).

### `write-interactions` — Fail
- report.py:171 `ReportFile._hits_by_rule`: the report is made with the progress that made it and calls back `progress.rules_answered_by(self)`, handing itself to its maker; the two objects share one job, choosing which rules a report answers for, that belongs to the fidelity (left, P-22).

### `class-not-property-instance-or-subtype` — Fail
- report.py:67 `Report`: means two things — one validation report (path, text, rules) and, from `from_reports`, the union of a ticket's reports, whose `path` is a folder and whose `text` is empty (new, low).

## Judgment — `space/kanban/backlog_item.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- backlog_item.py:55 `from_ticket(ticket, board)`: the board is passed beside a ticket that holds it (`ticket.board`) (new, low).
- backlog_item.py:133 `_ticket_opened`: `Ticket.create(..., project=self._board.repo.root)` loads the whole board again from a path although the item holds its board (left, P-13 pattern).

Passes: no `Workspace` bag, no `*_name` copies on Ticket, `TicketFiles` gone, Stage keeps its own WIP limit, Ticket hands callers its Session.
