# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report pass/fail per named practice fidelty and named rule with brief evidence.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.


### `ubiquitous-language-everywhere`

One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (ubiquitous-language-everywhere):

### `model-the-domain-not-the-implementation`

Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.

Evaluate the current context against this rule (model-the-domain-not-the-implementation):

### `vocabulary-traces-to-domain-source`

Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-concepts`

Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

Evaluate the current context against this rule (do-not-invent-concepts):

### `experts-words-preferred`

Use the words domain experts use. An invented synonym becomes a second term every reader must translate.

Evaluate the current context against this rule (experts-words-preferred):

### `domain-concepts-not-technical-names`

Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept. A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.

Evaluate the current context against this rule (domain-concepts-not-technical-names):

### `bc-by-lifecycle-not-ui-themes`

Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint journey-themed contexts that duplicate core domain contexts. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.

Evaluate the current context against this rule (bc-by-lifecycle-not-ui-themes):

### `one-meaning-per-context`

Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.

Evaluate the current context against this rule (one-meaning-per-context):

### `bc-above-aggregate`

A bounded context names a business area, department, or system collection with its own ubiquitous language — not a single aggregate. If the only candidate context is one aggregate, nest it under a broader context or record it as an **Integrations:** arc; omit the `###` heading. No real language boundary is better than a heading that merely duplicates an aggregate name.

Evaluate the current context against this rule (bc-above-aggregate):

### `one-module-per-context-when-small`

A consolidated custom context with only a handful of collaborating types is one clean-engineering module, not one package per aggregate or per class. Several entities under one `#### {module}/` is normal; four modules for four classes in the same context is the packaging version of `bc-above-aggregate`.

Evaluate the current context against this rule (one-module-per-context-when-small):

### `aggregate-clusters-entities`

An aggregate is a consistency cluster with a chosen root and the entities inside it — not one `####` heading per entity class. Several `#####` entities under one aggregate is normal; five aggregates for five account types that share one customer file is the same mistake at a finer grain.

Evaluate the current context against this rule (aggregate-clusters-entities):

### `integrations-cross-context-only`

**Integrations:** arcs cross a bounded-context boundary only. Another entity or aggregate in the same context is a property on the type that uses it — not an integration.

Evaluate the current context against this rule (integrations-cross-context-only):

### `dependency-fields-tracked`

Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc that names only a neighbor context does not tell anyone what to build.

Evaluate the current context against this rule (dependency-fields-tracked):

### `no-orphan-contexts`

Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.

Evaluate the current context against this rule (no-orphan-contexts):

### `vendor-not-implementation`

The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.

Evaluate the current context against this rule (vendor-not-implementation):

### `context-tree-bc-aggregate-concept`

Three levels on the bounded_context card only: BC → Aggregate → concept. Classes, stereotypes, and repositories wait for **model**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.

Evaluate the current context against this rule (context-tree-bc-aggregate-concept):

### `bounded-context-file-marks-the-folder`

In code, a bounded context is the folder that contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and each aggregate folder under it. A folder of classes with no such file is a module or a package, so the map and the tree disagree about where the language boundary is.

Evaluate the current context against this rule (bounded-context-file-marks-the-folder):

### `link-arrow-target`

Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.

Evaluate the current context against this rule (link-arrow-target):

### `hang-deps-on-owning-bc`

Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.

Evaluate the current context against this rule (hang-deps-on-owning-bc):

### `user-facing-system-first`

The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

Evaluate the current context against this rule (user-facing-system-first):

### `vocabulary-traces-to-domain-source`

Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-requirements`

Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

Evaluate the current context against this rule (do-not-invent-requirements):

### `evidence-distinguishes-observed-inferred-and-intended`

Label behaviour as observed, inferred, or intended and cite its source. When available evidence cannot exercise required behaviour, write the intended GWT and state the limitation, because an unobserved expectation must not be presented as a fact.

Evaluate the current context against this rule (evidence-distinguishes-observed-inferred-and-intended):

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-one-to-four`

A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.

Evaluate the current context against this rule (story-scenarios-one-to-four):

### `branch-on-mechanical-uniqueness`

Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.

Evaluate the current context against this rule (branch-on-mechanical-uniqueness):

### `right-size-story-nodes`

Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.

Evaluate the current context against this rule (right-size-story-nodes):

### `behaviours-not-one-time-tasks`

Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

Evaluate the current context against this rule (behaviours-not-one-time-tasks):

### `story-map-links-to-markdown`

Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

Evaluate the current context against this rule (story-map-links-to-markdown):