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

**Generated:** 2026-11-07 00:13:44 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 37
**Rules with graph hits:** 13
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

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L144): OoadClass `McpInstallation`: Class 'McpInstallation' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L597): OoadClass `McpHost`: Class 'McpHost' exposes 11 public operations (budget ~9). Split responsibilities.

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

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [harness/mcp/cdd_home.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\cdd_home.py#L48): OoadClass `CddHome`: Class 'CddHome' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_daemon.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_daemon.py#L37): OoadClass `McpDaemon`: Class 'McpDaemon' constructs 'CddHome' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L376): OoadClass `McpServer`: Class 'McpServer' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L597): OoadClass `McpHost`: Class 'McpHost' constructs 'RestartGate' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server_host_heavy_spec.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server_host_heavy_spec.py#L114): OoadClass `TwoWorktrees`: Class 'TwoWorktrees' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L20): OoadClass `UserHome`: Class 'UserHome' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L44): OoadClass `SpecServer`: Class 'SpecServer' constructs 'CddHome' inside its constructor.
- [X] **ERROR** **[graph rule]** - [harness/mcp/spec_support.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\spec_support.py#L101): OoadClass `ThrowawayMachine`: Class 'ThrowawayMachine' constructs 'UserHome' inside its constructor.

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

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Operation `echo`: Operation 'echo' takes 22 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L215): Operation `allow_cdd_tools`: Parameter 'settings' in 'allow_cdd_tools' is vague.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `state-change-returns-record-or-named-failure`

When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/restart_gate.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\restart_gate.py#L35): Operation `restarting`: Operation 'restarting' mutates state but does not return the record or a named failure.

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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L81): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L87): Parameter `value`: Parameter 'value' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L93): Parameter `value`: Parameter 'value' does not reveal intent.

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

- [X] **ERROR** **[graph rule]** - [harness/mcp](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp#L1): Module `mcp`: Module 'mcp' splits into many tiny classes (33); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/mcp/__main__.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\__main__.py#L9): Operation `main`: Operation 'main' is 24 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Operation `echo`: Operation 'echo' is 50 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L451): Operation `start`: Operation 'start' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L844): Operation `http_app`: Operation 'http_app' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L888): Operation `diagnose`: Operation 'diagnose' is 21 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `missing-module-context`

**Graph violations:** 7

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L11): OoadClass `PlanWorkResult`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L16): OoadClass `OrchestrateResult`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/hosting_demo/hosting_demo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\hosting_demo\hosting_demo.py#L22): OoadClass `HostingDemo`: Module folder 'hosting_demo' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/illegitimate_name/illegitimate_name.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\illegitimate_name\illegitimate_name.py#L9): OoadClass `IllegitimateName`: Module folder 'illegitimate_name' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L11): OoadClass `NamedRecord`: Module folder 'parameter_types' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L17): OoadClass `ParameterTypes`: Module folder 'parameter_types' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.
- [X] **ERROR** **[graph rule]** - [harness/mcp/scripts/connect.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\scripts\connect.py#L1): OoadClass `_module`: Module folder 'scripts' defines classes but has no .context/module-context.md. Add one with at minimum: Purpose, Seam, Dependencies.

Evaluate the current context against this rule (missing-module-context):

### `one-way-deps`

Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp#L1): Module `mcp`: Circular import between 'mcp' and 'illegitimate_name' breaks one-way dependencies.

Evaluate the current context against this rule (one-way-deps):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L924): Operation `standup`: Operation 'standup' is a classmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L451): Operation `start`: Operation 'start' nests control flow 4 levels deep (max 3).

Evaluate the current context against this rule (simplify-control-flow):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L22): Parameter `untyped_fields`: Parameter 'untyped_fields' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/_examples/parameter_types/parameter_types.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\_examples\parameter_types\parameter_types.py#L93): Parameter `value`: Parameter 'value' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L156): Parameter `tool`: Parameter 'tool' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L315): Parameter `server`: Parameter 'server' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/mcp/mcp_server.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\harness\mcp\mcp_server.py#L831): Parameter `daemon`: Parameter 'daemon' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

---

# Judgment (model fidelity, judged against the graph this call built)

Scope: the 22 Python classes of `harness/mcp` in this call's graph; `_examples` and `spec_support.py` (test support) are left out. Dismissed graph hits: `missing-module-context` and the `_examples` cycles (example toolsets the specs load, not production dependencies); `keep-operations-small-focused` and `simplify-control-flow` are code-fidelity rules; `CddHome` and `McpServer` "construct Path" (a value, not a collaborator); `McpHost` constructing its `RestartGate` (an owned part with no identity outside the host, which composition allows); `settings` on `allow_cdd_tools` names the Claude settings file it edits; `restarting` is a context manager whose state change is the gate itself, not a record.

## Judgment — `harness/mcp/mcp_server.py`

### `hold-state-on-the-object-not-in-parameters` — Fail
- mcp_server.py:773 `_dispatch_reporting`: the project a call works on is set as a context-wide global with `working_on(project)` and read back inside by `project_checkout()` (mcp_server.py:802) and `Board.current()`, instead of being handed to the runtime and the toolsets that act on it; a call started from inside another, which nobody hands the project to, reads whatever is set.
- mcp_server.py:805 `_dispatch_between_restarts`: refreshes the global current session (`Session.refresh_current_from_repo(project)`) on every call, and the chat pointer is popped from the arguments and set for the call with `ChatPointer.serving(chat)`; per-call state set on shared, process-wide objects.

### `keep-classes-single-responsibility` — Fail
- mcp_server.py:144 `McpInstallation`: 13 public operations covering the MCP manifest (`write`, `record_operation`, `write_mcp_manifest`), editing user and project config (`allow_cdd_tools`, `drop_project_cdd_server`, `drop_user_cdd_server`), and running the server (`ensure_server`, `pin_server`, `serve_from_checkout`, `server_is_running`, `standup`, `diagnose`).
- mcp_server.py:597 `McpHost`: 11 public operations mixing call dispatch, the HTTP app, restarts, diagnosis, and notices.

### `use-explicit-dependencies` — Fail
- mcp_server.py:330 `server_home`: builds a new `CddHome()` on every read, typed `Any`, and mcp_server.py:339 `ensure_server`, `pin_server`, and `serve_from_checkout` each build a new `McpDaemon` inside the operation; the installation is never given the home or daemon it drives.

### `put-logic-on-the-owning-resource` — Fail
- mcp_server.py:347 `pin_server`: McpInstallation sequences CddHome's install and pin and McpDaemon's restart; pinning and serving a checkout are CddHome's and McpDaemon's jobs, so the installation only forwards to them (also `serve_from_checkout` at mcp_server.py:355).

### `prefer-instance-operations` — Fail
- mcp_server.py:924 `standup`: a classmethod that stands up a host for a repo found from a global when none is given; McpInstallation calls it and keeps the result in `self.host`.

### `use-typed-signatures` — Fail
- mcp_server.py:156 `write`: `tool: Any` although McpInstallation only writes AgentTools; mcp_server.py:315 `bind` takes `server: Any`; mcp_server.py:831 `serve` takes `daemon: Any`.

## Judgment — `harness/mcp/mcp_daemon.py`

### `use-explicit-dependencies` — Fail
- mcp_daemon.py:45 `__init__`: `self.home = home or CddHome()` builds the user's home when none is given, so a daemon made without one always acts on the real `~/.cdd`.

## Judgment — `harness/mcp/cdd_home.py`

### `use-typed-signatures` — Fail
- cdd_home.py:80 `write_claude_plugin`: `server: dict[str, object]`, an untyped record of the server entry.

Passes: `vocabulary-traces-to-source`, `do-not-invent-terms`, `do-not-invent-parallel-object-models` (MCP reads AgentTool; no second operation model), `model-modules-follow-the-partition`, `class-not-property-instance-or-subtype`, `shape-classes-around-resources`, `hide-inner-details`, `use-property-not-accessor`, `prefer-class-operations` (only entry-point `main` functions), `external-system-interface-is-one-way`, `limit-operation-parameters` (`from_refs` is a factory), `errors-out-of-existence`, `domain-exception-carries-context` (typed `McpStandupFailed`, `ServerDidNotStart`, `PinFailed`), `no-redundant-relationship-paths`, `use-consistent-naming`, `eliminate-duplication`.
