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

**Generated:** 2026-11-07 04:16:10 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 6
**Rules with graph hits:** 4
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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\nodes.py#L240): OoadClass `Screen`: Class 'Screen' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/ux_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\ux_map.py#L17): OoadClass `UxMap`: Class 'UxMap' exposes 14 public operations (budget ~9). Split responsibilities.

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

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\nodes.py#L240): OoadClass `Screen`: Class 'Screen' constructs 'Name' inside its constructor.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/ux_map.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\ux_map.py#L17): OoadClass `UxMap`: Class 'UxMap' constructs 'BoundChildren' inside its constructor.

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

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/nodes.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\nodes.py#L197): Operation `load_control`: Operation 'load_control' is 34 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/ux_node.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\cdd_guidance\practices\ux\model\ux_node.py#L40): Operation `children`: Operation 'children' swallows a caught failure.

Evaluate the current context against this rule (never-swallow-exceptions):

## Judgment — `cdd_guidance/practices/ux/model/nodes.py`

### `do-not-invent-parallel-object-models` — Fail
- nodes.py:259 `Screen.story_names`, `scenario_names` (:260), `step_names` (:261): Stories' Story, Scenario, and Step are held as name strings ("Story › Scenario › Step") instead of references, although schema.yaml says `stories?: [story]`. Because of the copy, `harness/graph/schema_edges.py:161` matches `shownOn` edges by string, `harness/graph/bound_node.py:206` hard-codes these three UX field names in the framework, and `stories/model/claude_design/nodes.py:114/191/384` reads `getattr(screen, "story_names")`. A renamed story silently drops off its screen.
- nodes.py:250 `Screen.chrome_of: str`, nodes.py:258 `inactive_tabs: List[str]`, nodes.py:365 `Transition.from_screen`/`to_screen: str`, nodes.py:23 `Interaction.destination_screen: str`, nodes.py:423 `NavComponent.destinations: List[str]`: every screen-to-screen relationship is a `*_screen` name copy of a Screen reference the map already holds (schema.yaml names `chromeOf?: screen`). Renaming a screen leaves every transition, interaction, and tab pointing at nothing.
- nodes.py:131 `StoryDemoControl.story_steps: List[Dict]` and `item_story_steps`: `{"kind": given|when|then, "label": ...}` dicts copy Stories' `Step` (`StepType`, text) instead of referencing the steps.
- nodes.py:181 `Region.controls`, :266 `Screen.regions`, :64 `Control.interactions`: plain lists, not the graph's `BoundChildren`. Only `UxMap.screens` is a graph child list. Regions, controls, interactions, and (via collections.py) transitions never join the map's graph; each is constructed with `graph=None`, so `BoundNode.__init__` gives each its own new `Graph()` (checked: `region.graph is map.graph` is False). Graph rules for regions and controls (`ia-named-regions-only`) cannot see them.

### `use-consistent-naming` — Fail
- nodes.py:262 `Screen.domain_terms` and :263 `domain_concepts`: two lists for one concept (schema.yaml has only `domainTerms`); `drawio/cli_state.py:37` reads `domain_terms or domain_concepts`.
- nodes.py:55 `Control.control_type: str`: free-text control kinds that the html and drawio adapters classify with different alias sets (see their judgments); the kind belongs on Control as a typed property.

### `use-intention-revealing-names` — Fail
- nodes.py:178 `Region.slot` and `StoryDemoControl` docstring (:106 "bindings", :111 "rows"): banned words (`slot`, `binding`, `rows`) in a public field name and docstring.

### `keep-operations-small-focused` — Fail
- nodes.py:197 `Region.load_control`: 34 lines (graph hit confirmed), and it rebuilds Control and Interaction by hand beside `Control.load_interaction` (:83) and `JsonUxMap._control_from_dict`.

### `eliminate-duplication` — Fail
- nodes.py:131 `{"kind": s.get("kind", ""), "label": s.get("label", "")}`: the same story-step normalisation is written 6 times in this file (:131, :136, :146, :151, :160, :165) and 4 more in json/nodes.py:182/:189 and html/nodes.py:148/:163.
- nodes.py:197 `Region.load_control` and :83 `Control.load_interaction`: each node copies itself field by field in `load_*` and again in `update_self` and `snapshot_fields`; three lists of the same fields per class.

### `keep-classes-single-responsibility` — Fail
- nodes.py:240 `Screen`: 10 public operations (graph hit confirmed); `attach_story_name`, `attach_scenario_name`, `attach_step_name` are the Stories link kept as strings, a second job beside laying out regions.

## Judgment — `cdd_guidance/practices/ux/model/ux_node.py`

### `do-not-invent-parallel-object-models` — Fail
- ux_node.py:40 `UxNode.children`: a second child walk built on `child_collections`, beside BoundNode's own `_child_lists` / `_subtree` in `harness/graph/bound_node.py:191`. The two disagree: BoundNode sees only `screens`; `children()` sees regions, controls, and interactions.

### `never-swallow-exceptions` — Fail
- ux_node.py:45 `children`: `except NotImplementedError: pass` returns an empty list for any node whose subclass forgot `child_collections` (graph hit confirmed).

### `hold-state-on-the-object-not-in-parameters` — Fail
- ux_node.py:53 `_reconcile_collection`: per-call scratch state `self._consumed_ids` is written on the node for one call and read by `_find_match`, instead of being a local passed or a small reconciler object.
- ux_node.py:43 `children`: calls `self.child_collections(self)`, passing the node to itself as its own source.

### `put-logic-on-the-owning-resource` — Fail
- ux_node.py:23 `translate_from`: translation between formats is implemented as every node copying itself into a sibling adapter instance (`DrawioUxMap`, `JsonUxMap` are UxMap subclasses), so each format adapter is also a full UxMap; the format's job (read and write text) and the map's job are one class.

## Judgment — `cdd_guidance/practices/ux/model/ux_map.py`

### `no-legacy-api-after-refactor` — Fail
- ux_map.py:113 `append_transition`, :117 `append_content_type`, :121 `append_nav_component`: docstrings say "Delegate - prefer `ux_map.transitions.append`"; thin wrappers kept for the old API.

### `do-not-invent-parallel-object-models` — Fail
- ux_map.py:155 `all_story_names`: answers story names from the screens' string copies (see nodes.py:259).
- ux_map.py:64 `_copy_screens_on_graph`: when opened on a graph, copies only name and order from another UxMap on the same graph into new Screen objects, so a second UxMap with half-copied screens now sits beside the first.

### `keep-classes-single-responsibility` — Fail
- ux_map.py:17 `UxMap`: 14 public operations (graph hit confirmed); it is also the base class of every format adapter, so parse/render/from_workspace land on it too.

### `use-intention-revealing-names` — Fail
- ux_map.py:73 `story_references` docstring "Bind/dedupe behind the property": banned word.

## Judgment — `cdd_guidance/practices/ux/model/collections.py`

### `do-not-invent-parallel-object-models` — Fail
- collections.py:14 `UxComponentCollection(UxNode)`: a list is modelled as a graph node with its own `items` plain list, beside the graph's `BoundChildren`; transitions, content types, and nav components are never linked to the map on the graph (schema.yaml names `transitions?: [transition]` on map).

### `class-not-property-instance-or-subtype` — Fail
- collections.py:84 `Transitions`, :106 `ContentTypes`, :121 `NavComponents`: three classes that differ only by item type and name; a `BoundChildren(self, "transitions")` on UxMap holds the same thing.

### `eliminate-duplication` — Fail
- collections.py:94 `Transitions.load_component`: constructor-argument copy of Transition, written again in json/nodes.py:61.

## Judgment — `cdd_guidance/practices/ux/model/update_report.py`

### `do-not-invent-parallel-object-models` — Fail
- update_report.py:24 `Change`: `from_name`, `to_name`, `node_name`, `parent_name` are string copies of the node references the reconciler holds; `from_name` and `to_name` are always the same value (:44).

Passes: `cdd_guidance/practices/ux/model/__init__.py`, `cdd_guidance/practices/ux/model/reference_paths.py` (a small value object with dedupe; acceptable).

Graph hits dismissed: `use-explicit-dependencies` on Screen constructing `Name` (Name is the canonical slug value, not a collaborator) and on UxMap constructing `BoundChildren` (that is the graph's intended child-list mechanism).
