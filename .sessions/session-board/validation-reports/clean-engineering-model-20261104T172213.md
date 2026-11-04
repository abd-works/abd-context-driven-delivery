# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Write the judgment in this shape, because the session board reads it and lists each finding beside the graph's hits, with a Fix that sends it back:

   ```markdown
   ## Judgment — `path/of/the/judged/file.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   One `###` heading per rule that fails, with Fail after the dash. One bullet per finding, opening with the judged file's name and the line, so a person can open the finding at that line. Leave passing rules out of these headings; a table or a Passes paragraph may list them.


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

## Judgment — `harness/kanban/.context/kanban-model.md`

### `vocabulary-traces-to-source` — Fail
- kanban-model.md:198 `Ticket.root`: the ticket calls the session's folder its root while `Session.workpath` (line 371) names the same folder, so readers translate between two words for one thing.

### `do-not-invent-terms` — Fail
- kanban-model.md:201 `Ticket.practice_roots`: a practice root on the ticket is the session's output root (line 415), a second noun for the folder a practice writes under.

### `do-not-invent-parallel-object-models` — Fail
- kanban-model.md:270 `FidelityProgress`: it reads the session log into its own done actions and states, while `Session.action_states`, `is_stage_done`, and `violations` (line 394) model the same progress.
- kanban-model.md:136 `Stage.work_required`: the same list as `Session.work_required` (line 382), kept in a second place.

### `keep-classes-single-responsibility` — Fail
- kanban-model.md:169 `Ticket`: it moves cards, records reviews, lists files, builds reports, sets roots, switches branches and worktrees, and writes generate commands; line 676 says so.

### `put-logic-on-the-owning-resource` — Fail
- kanban-model.md:258 `Ticket.report`: the session owns its reports and the graph that checked them, so building the rule list belongs there, as `Session.reports` (line 403) intends.
- kanban-model.md:250 `Ticket.files`: the session owns its fidelity outputs (line 408); the ticket only asks.

### `hide-inner-details` — Fail
- kanban-model.md:426 `Session.fields`: callers read `session.json` as a raw dictionary, so its layout becomes a public contract.
- kanban-model.md:456 `PracticeSessionOutput.output_paths`: exposes the stored list of paths instead of an operation that answers a question about them.

### `use-property-not-accessor` — Fail
- kanban-model.md:631 `GraphRulesCollection.slugs()`: derived state with no parameters, written as an operation; the same holds for `violations()`, `failed_slugs()`, and `passing_slugs()` below it.
- kanban-model.md:656 `GraphRule.failing()`: derived state written as an operation.

### `prefer-class-operations` — Fail
- kanban-model.md:593 `Graph.write_json`: the saved graph is read back by the module-level `violations_from_graph_json_files`, a free function that belongs on `Graph`.

### `use-explicit-dependencies` — Fail
- kanban-model.md:93 `Board.current`: finds its project from `CDD_PROJECT` or the current folder, a global the board reaches for; the one cdd server now names the project on each call, so this note is also out of date.

### `keep-operations-single-responsibility` — Fail
- kanban-model.md:208 `Ticket.move_previous`: one operation marks progress, moves stages, reopens a closed session, and moves a ticket into the Backlog.
- kanban-model.md:238 `Ticket.activate`: commits, pushes, merges, creates branches and worktrees, and switches the session in one call.

### `limit-operation-parameters` — Fail
- kanban-model.md:235 `Ticket.new`: four parameters; title, scope, parent, and path describe one new ticket.
- kanban-model.md:422 `Session.new`: five parameters.
- kanban-model.md:637 `GraphRulesCollection.record_violation`: five parameters; message, file, start, and end are one violation.

### `avoid-vague-parameter-names` — Fail
- kanban-model.md:428 `Session.save_fields(fields)`: fields says nothing about which values are saved.
- kanban-model.md:626 `GraphRulesCollection(node, entries, parent)`: parent does not say what it is the parent of.

### `state-change-returns-record-or-named-failure` — Fail
- kanban-model.md:214 `Ticket.finish_review`: it refuses a fidelity the ticket does not have, but names no failure.
- kanban-model.md:415 `Session.choose_output_root`: a state change that returns nothing and refuses a root inside `.context` with no failure named in the model.

### `domain-exception-carries-context` — Fail
- kanban-model.md:257 `Ticket.read_file`: refuses a path outside the repository, but the model names no typed exception carrying the path.

### `write-interactions` — Fail
- kanban-model.md:249 `Ticket.enable_practice`: reaches into `PracticeSessionOutput.enabled` instead of asking `Session`.
- kanban-model.md:260 `Ticket.report`: talks to `Graph.write_json` directly, past the session that owns the practice graphs (line 454).

### `no-redundant-relationship-paths` — Fail
- kanban-model.md:71 `Board.repo_root`: `Board.repo` (line 72) and `Repo.root` (line 343) already give the root.
- kanban-model.md:135 `Stage.practices`: a third path to the practices beside `Board.practices` (line 74) and `Ticket.practices` (line 180).
- kanban-model.md:175 `Ticket.name`: a copy of what its session (line 174) already says.

### `use-intention-revealing-names` — Fail
- kanban-model.md:189 `Ticket.next`: does not say what is next; it is the next fidelity.
- kanban-model.md:265 `Ticket.keep`: does not say what is kept or where.
- kanban-model.md:424 `Session.at`: does not say what it finds.
- kanban-model.md:233 `Ticket.load(ticket: str)`: the parameter is a ticket's name, not a ticket.

### `use-consistent-naming` — Fail
- kanban-model.md:210 `Ticket.move_to`: the same verb as `Session.move_to` (line 429), which moves a folder, not a card.
- kanban-model.md:90 `Board.load`: `current`, `at`, and `all_in` (lines 92, 424, 430) are four verbs for finding an object.

### `eliminate-duplication` — Fail
- kanban-model.md:536 `StageName`: `STAGE_NAMES` in `board.py` repeats the constants in `stages.py`, and `FidelityGuidance.stage` (line 512) is still a string.
- kanban-model.md:292 `FidelityProgress.from_log`: a second reader of session log lines beside `Activity.from_log_line` (line 492).

**Passes:** `model-modules-follow-the-partition` (the top-level modules are the repository's modules), `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `external-system-interface-is-one-way` (no external system in scope), `errors-out-of-existence`, `limit-comments`, `write-invariants` (lines 19 and 30), and `one-canonical-model-document` (the drawio mirrors this file and leaves Intended members out, as line 65 says).
