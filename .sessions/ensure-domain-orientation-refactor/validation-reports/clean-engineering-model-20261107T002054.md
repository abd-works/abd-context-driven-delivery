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

**Generated:** 2026-11-07 00:20:54 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 197
**Rules with graph hits:** 17
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

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L24): OoadClass `AccountCredentialsClient`: Class 'AccountCredentialsClient' exposes 19 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L33): OoadClass `AccountCredentials`: Class 'AccountCredentials' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L108): OoadClass `CustomerRepository`: Class 'CustomerRepository' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/tests/onboard-a-customer/authenticate-user/examples/account-credentials.examples.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\tests\onboard-a-customer\authenticate-user\examples\account-credentials.examples.ts#L1): OoadClass `_module`: Class '_module' exposes 20 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L1): OoadClass `_module`: Class '_module' exposes 28 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L1): OoadClass `_module`: Class '_module' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L1): OoadClass `_module`: Class '_module' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L1): OoadClass `_module`: Class '_module' exposes 27 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L432): OoadClass `Filter`: Class 'Filter' exposes 11 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Class 'PracticeGraph' exposes 12 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Class 'Graph' exposes 17 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L1): OoadClass `_module`: Class '_module' exposes 15 public operations (budget ~9). Split responsibilities.

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

- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L53): OoadClass `BoundNode`: Class 'BoundNode' constructs 'Graph' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Class 'PracticeGraph' constructs 'Node' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Class 'Graph' constructs 'Filter' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):

### `external-system-interface-is-one-way`

Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.

Evaluate the current context against this rule (external-system-interface-is-one-way):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L434): Operation `readSavedOverlays`: Operation 'readSavedOverlays' mixes I/O-style calls with domain calculation; split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L131): Operation `copyCorrectPrompt`: Operation 'copyCorrectPrompt' delegates to both I/O and domain helpers; give it one job.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L43): Operation `practice_from_class_text`: Operation 'practice_from_class_text' mixes I/O-style calls with domain calculation; split responsibilities.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 20

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Operation `postOperation`: Operation 'postOperation' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L240): Operation `exception`: Operation 'exception' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L410): Operation `overlayFilterRefresh`: Operation 'overlayFilterRefresh' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Operation `keep`: Operation 'keep' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L281): Operation `violationLineDecorations`: Operation 'violationLineDecorations' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Operation 'inlineCallLayout' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L611): Operation `callsOnLine`: Operation 'callsOnLine' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L640): Operation `resolveCall`: Operation 'resolveCall' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L671): Operation `appendOperation`: Operation 'appendOperation' takes 12 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Operation `appendClass`: Operation 'appendClass' takes 10 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L39): Operation `assert_bdd_source_pair`: Operation 'assert_bdd_source_pair' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L78): Operation `assert_rule_pair`: Operation 'assert_rule_pair' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L52): Operation `violations_for_ddd_rule`: Operation 'violations_for_ddd_rule' takes 6 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1190): Operation `load_working_copy`: Operation 'load_working_copy' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1224): Operation `load_files`: Operation 'load_files' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L288): Operation `qualified_rule_label`: Operation 'qualified_rule_label' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Operation `violations_for_story_source`: Operation 'violations_for_story_source' takes 4 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L88): Operation `assert_stories_ts_pair`: Operation 'assert_stories_ts_pair' takes 5 parameters (maximum 3, excluding self).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L49): Operation `assert_stories_folder_pair`: Operation 'assert_stories_folder_pair' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Operation `postOperation`: Parameter 'payload' in 'postOperation' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-client.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-client.tsx#L161): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Parameter 'options' in 'inlineCallLayout' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Parameter `options`: Parameter 'options' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L22): Operation `encode_node_data`: Parameter 'data' in 'encode_node_data' is vague.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L22): Parameter `data`: Parameter 'data' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L39): Operation `assert_bdd_source_pair`: Operation 'assert_bdd_source_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_module_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_module_example_harness.py#L21): Operation `assert_module_example_pair`: Operation 'assert_module_example_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L19): Operation `ce_rule_by_slug`: Operation 'ce_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L17): Operation `ddd_rule_by_slug`: Operation 'ddd_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L64): Operation `tree_named`: Operation 'tree_named' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L13): Operation `stories_rule_by_slug`: Operation 'stories_rule_by_slug' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L88): Operation `assert_stories_ts_pair`: Operation 'assert_stories_ts_pair' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L229): Operation `storeCustomerId`: Operation 'storeCustomerId' mutates state but does not return the record or a named failure.

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

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L532): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L675): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L222): OoadClass `Source`: Operation 'startLine' uses camelCase while other operations on 'Source' use the other convention.

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

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials#L1): Module `account-credentials`: Module 'account-credentials' splits into many tiny classes (10); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 36

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials.ts#L183): Operation `authenticateAccount`: Operation 'authenticateAccount' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/customer/customer.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\customer\customer.ts#L205): Operation `read`: Operation 'read' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' is 342 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Operation `load`: Operation 'load' is 37 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L176): Operation `applyOverlays`: Operation 'applyOverlays' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L234): Operation `applyFilter`: Operation 'applyFilter' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Operation `keep`: Operation 'keep' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L887): Operation `answer`: Operation 'answer' is 71 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L1030): Operation `rowsFor`: Operation 'rowsFor' is 34 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/filter/FilterView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\filter\FilterView.tsx#L20): Operation `FilterView`: Operation 'FilterView' is 98 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphView.tsx#L24): Operation `GraphView`: Operation 'GraphView' is 71 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/query-progress.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\query-progress.ts#L26): Operation `queryProgress`: Operation 'queryProgress' is 82 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/kind-mark.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\kind-mark.tsx#L1): Operation `kindLabel`: Operation 'kindLabel' is 61 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/kind-mark.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\kind-mark.tsx#L115): Operation `KindMark`: Operation 'KindMark' is 364 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L85): Operation `collectFoldMembers`: Operation 'collectFoldMembers' is 42 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L160): Operation `braceFolds`: Operation 'braceFolds' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L232): Operation `inlineCallLayout`: Operation 'inlineCallLayout' is 59 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L333): Operation `variableTypes`: Operation 'variableTypes' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L374): Operation `callCatalog`: Operation 'callCatalog' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L611): Operation `callsOnLine`: Operation 'callsOnLine' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L640): Operation `resolveCall`: Operation 'resolveCall' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L671): Operation `appendOperation`: Operation 'appendOperation' is 40 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Operation `appendClass`: Operation 'appendClass' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/vite.config.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\vite.config.ts#L15): Operation `ping`: Operation 'ping' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L66): Operation `assert_ddd_example_pair`: Operation 'assert_ddd_example_pair' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L303): Operation `align_to_example_export`: Operation 'align_to_example_export' is 29 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L837): Operation `serialize`: Operation 'serialize' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L868): Operation `rule_rows`: Operation 'rule_rows' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1190): Operation `load_working_copy`: Operation 'load_working_copy' is 30 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L13): Operation `attach_rules`: Operation 'attach_rules' is 57 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L167): Operation `ce_anchor_type`: Operation 'ce_anchor_type' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L222): Operation `rules_for_practice`: Operation 'rules_for_practice' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Operation `violations_for_story_source`: Operation 'violations_for_story_source' is 28 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L49): Operation `assert_stories_folder_pair`: Operation 'assert_stories_folder_pair' is 23 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy.py#L60): Operation `fill_working_copy`: Operation 'fill_working_copy' is 33 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 55

- [X] **ERROR** **[graph rule]** - [harness/graph/app_smoke_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app_smoke_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_examples_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_examples_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_invokes_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_invokes_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L19): OoadClass `BoundChildren`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L53): OoadClass `BoundNode`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/c_family_parse_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\c_family_parse_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_module_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_module_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/drawio_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\drawio_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L15): OoadClass `GraphLoaded`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L27): OoadClass `GraphSaved`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L39): OoadClass `RuleHit`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L73): OoadClass `ExplorerEntry`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L102): OoadClass `RuleCategory`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L118): OoadClass `RuleEntry`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L150): OoadClass `Overlay`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L162): OoadClass `FilteredNode`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L206): OoadClass `Member`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L255): OoadClass `NodeSource`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L116): OoadClass `GraphFailure`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L178): OoadClass `EdgeType`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L185): OoadClass `Edge`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L213): OoadClass `Call`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L222): OoadClass `Source`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L432): OoadClass `Filter`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L650): OoadClass `Node`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L898): OoadClass `PracticeGraph`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1090): OoadClass `Inventory`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1114): OoadClass `AppliedOverlays`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1129): OoadClass `Graph`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_json_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_json_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L11): OoadClass `GraphRule`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L71): OoadClass `GraphRulesCollection`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/guidance_prose_index.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\guidance_prose_index.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/language_for_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\language_for_node.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_data.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_data.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rule.py#L11): OoadClass `PracticeGraphRule`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rules_registry.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rules_registry.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_category_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_category_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L11): OoadClass `RuleCheckContext`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_edges.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_edges.py#L87): OoadClass `SchemaField`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/skipped_folders.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\skipped_folders.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_rules_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_rules_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_ts_folder_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_ts_folder_harness.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/story_scenario_count_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\story_scenario_count_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/graph/working_copy_scan_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\working_copy_scan_spec.py#L1): OoadClass `_module`: Module folder 'graph' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials#L1): Module `account-credentials`: Circular import between 'account-credentials' and 'customer' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/graph/_examples/input/src/account-credentials/account-credentials-node.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\_examples\input\src\account-credentials\account-credentials-node.ts#L68): Operation `destination`: Operation 'destination' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L199): Operation `fact`: Operation 'fact' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1143): Operation `of_practice`: Operation 'of_practice' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L42): Operation `prose_only`: Operation 'prose_only' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/graph/app/app.test.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\app.test.tsx#L887): Operation `answer`: Operation 'answer' uses the unnamed number 7.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphView.tsx#L18): Operation `elapsedLabel`: Operation 'elapsedLabel' uses the unnamed number 60.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/query-progress.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\query-progress.ts#L26): Operation `queryProgress`: Operation 'queryProgress' uses the unnamed number 120.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/SourceView.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\SourceView.tsx#L266): Operation `sourceHeight`: Operation 'sourceHeight' uses the unnamed number 16.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/vite.config.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\vite.config.ts#L15): Operation `ping`: Operation 'ping' uses the unnamed number 5173.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L736): Operation `fact`: Operation 'fact' uses the unnamed number 7.

Evaluate the current context against this rule (provide-meaningful-context):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L30): Operation `App`: Operation 'App' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L75): Operation `tick`: Operation 'tick' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L303): Operation `align_to_example_export`: Operation 'align_to_example_export' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L787): Operation `populate`: Operation 'populate' nests control flow 4 levels deep (max 3).
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1035): Operation `direct_parent`: Operation 'direct_parent' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 31

- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Parameter `next`: Parameter 'next' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L115): Parameter `force`: Parameter 'force' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L234): Parameter `practices`: Parameter 'practices' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/App.tsx](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\App.tsx#L500): Parameter `violationsOnly`: Parameter 'violationsOnly' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/graph/GraphClient.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\graph\GraphClient.ts#L11): Parameter `title`: Parameter 'title' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L206): Parameter `quote`: Parameter 'quote' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/app/source/call-expansion.ts](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\app\source\call-expansion.ts#L727): Parameter `again`: Parameter 'again' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bdd_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bdd_example_harness.py#L22): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L28): Parameter `child`: Parameter 'child' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/bound_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\bound_node.py#L36): Parameter `child`: Parameter 'child' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/ce_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ce_rule_eval_harness.py#L60): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/ddd_rule_eval_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\ddd_rule_eval_harness.py#L52): Parameter `rule`: Parameter 'rule' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/explorer.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\explorer.py#L49): Parameter `hit`: Parameter 'hit' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L568): Parameter `request`: Parameter 'request' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L675): Parameter `value`: Parameter 'value' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L679): Parameter `default`: Parameter 'default' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L762): Parameter `row`: Parameter 'row' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph.py#L1010): Parameter `fact`: Parameter 'fact' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/graph_rules_collection.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\graph_rules_collection.py#L49): Parameter `source`: Parameter 'source' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/graph/language_for_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\language_for_node.py#L8): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/node_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\node_rules.py#L11): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rule.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rule.py#L15): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/practice_rules_registry.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\practice_rules_registry.py#L79): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L18): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L26): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L33): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L37): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rule_context.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rule_context.py#L40): Parameter `node`: Parameter 'node' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\rules.py#L13): Parameter `practice`: Parameter 'practice' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/schema_rules.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\schema_rules.py#L271): Parameter `practice_graph`: Parameter 'practice_graph' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/graph/stories_example_harness.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\graph\stories_example_harness.py#L58): Parameter `rule`: Parameter 'rule' is missing a type annotation.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 43 Python classes and module-function sets of `harness/graph` in this call's graph; the TypeScript explorer under `harness/graph/app` and the sample inputs under `_examples` are left out, so their cycles (`app` with `app/filter` and `app/graph`, and the sample `account-credentials`/`customer` pair) are not judged here. The `*_example_harness.py` and `*_rule_eval_harness.py` files are spec support for the rule scanners, so their free functions and `rule:` parameters are dismissed.

## Judgment — `harness/graph/graph.py`

### `do-not-invent-parallel-object-models` — Fail
- graph.py:650 `Node`: the graph still builds its own Node for every parsed object and keeps the parsed object beside it as `Node.model`; `BoundNode` (bound_node.py:53) subclasses Node rather than the graph registering the parsed BoundNodes, so two objects describe each concept (1.4 Mode B still open).
- graph.py:675 `set_fact`: Node keeps a free-form facts dict (`set_fact`, `get_fact`, `has_fact`, `graph_facts`) that holds copies of what the parsed model already knows.

### `prefer-instance-operations` — Fail
- graph.py:1163 `current`: a classmethod over the class-level `_current` (graph.py:1132), so every tool reads and filters one process-wide graph instead of the graph of the session or practice it works on.

### `hold-state-on-the-object-not-in-parameters` — Fail
- graph.py:1190 `load_working_copy`: takes the folder, a `practices` dict of names to roots, a database, overlays, and `force` on each call, and graph.py:1224 `load_files` takes folder, practices, files, and overlays; the practice roots belong to the session's practices, which should own their graph (P-19/P-20 still open in this seam).
- graph.py:1143 `of_practice`: takes the practice's name and source root as strings rather than the practice that holds them.

### `keep-classes-single-responsibility` — Fail
- graph.py:1129 `Graph`: 47 methods and 17 public operations covering loading the working copy, scoping edited files, saving JSON, overlays, inventory, filter choices, node source lookup, and returning filtered nodes.
- graph.py:898 `PracticeGraph`: 12 public operations mixing node and edge registration, rule attachment (`bind_rule`, `rules_for`, `apply_rules`, `nodes_for_rule`), and tree rebuilding.

### `use-property-not-accessor` — Fail
- graph.py:679 `get_fact`: `get_fact`/`set_fact`/`has_fact` are storage accessors over a dict; callers need to know the fact keys instead of reading named properties.

### `use-consistent-naming` — Fail
- graph.py:453 `node_types`: Filter has a `node_types` setter and a `select_node_types` operation (graph.py:503), `rules` and `select_rules` (graph.py:473, graph.py:484), and `relationships` and `select_relationships`; two verbs for setting one selection.

### `use-typed-signatures` — Fail
- graph.py:568 `narrowed_by`: `request: dict`; graph.py:1569 `return_nodes` takes `filter: dict`; graph.py:762 `from_fact` takes `row: dict`.

## Judgment — `harness/graph/explorer.py`

### `do-not-invent-parallel-object-models` — Fail
- explorer.py:255 `NodeSource`: re-exposes its Node's `node_id`, `name`, `type`, `file`, and lines as separate data fields; explorer.py:162 `FilteredNode` and explorer.py:206 `Member` do the same, and explorer.py:73 `ExplorerEntry` / explorer.py:118 `RuleEntry` form an `*Entry` family describing nodes and rules for the explorer; the Node and Rule should publish their own fields.

## Judgment — `harness/graph/working_copy.py`

### `prefer-class-operations` — Fail
- working_copy.py:60 `fill_working_copy`: a file of 71 module-level functions, one public, nearly all taking the Graph or a PracticeGraph first (`_typescript_files(graph, ...)`, `_model_files(graph, ...)`, `_record_clean(practice, ...)`, `_record_bdd(practice, ...)`); loading the working copy is Graph's and PracticeGraph's job.

## Judgment — `harness/graph/schema_rules.py`

### `prefer-class-operations` — Fail
- schema_rules.py:222 `rules_for_practice`: 27 module-level functions keyed by a practice's name string (`fidelities_for_type`, `slugs_for_type`, `ce_anchor_type`, `qualified_rule_label`, `bind_practice_rules`, ...); they belong on PracticeGraph and the practice's guidance.

### `hold-state-on-the-object-not-in-parameters` — Fail
- schema_rules.py:247 `slugs_for_type`: `practice: str`, `node_type: str`, and `active_patterns` are passed to every function so each can look the practice up again by name.

## Judgment — `harness/graph/practice_rules_registry.py`

### `do-not-invent-parallel-object-models` — Fail
- practice_rules_registry.py:34 `graph_rules_for_practice`: a registry of rules keyed by practice name (`channel_rules_for_practice`, `pattern_rules_for_practice`, `checks_for_practice`, `checks_for_node`) beside the rules each PracticeGuidance already holds (`PracticeGuidance.rules`, `GraphRulesCollection`).

## Judgment — `harness/graph/node_data.py`

### `prefer-class-operations` — Fail
- node_data.py:9 `decode_node_data`: free `decode_node_data(row: list)` and `encode_node_data(data: dict)` do Node's serialization; graph.py:736 `Node.fact` and graph.py:762 `Node.from_fact` are a second way to read the same row.

## Judgment — `harness/graph/graph_rules_collection.py`

### `do-not-invent-parallel-object-models` — Fail
- graph_rules_collection.py:71 `GraphRulesCollection`: publishes `failed_slugs` and `passing_slugs`, slug-string copies of the rules it holds.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `hide-inner-details`, `external-system-interface-is-one-way`, `errors-out-of-existence`, `domain-exception-carries-context`, `no-redundant-relationship-paths`. `Operation.owner` and the DDD node models (G3, G4, G13, G14) are confirmed in place.
