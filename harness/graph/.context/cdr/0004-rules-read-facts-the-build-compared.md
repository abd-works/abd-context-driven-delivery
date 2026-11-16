# Rules read facts the build compared; they compute nothing across nodes when they check

Several graph rules did their real work while they checked. `deep-module` built, at check time, which production classes each module folder holds (through a class index over the whole practice) and which modules import each class name (from every folder's imports and the root's), and then decided which classes were public. `one-way-deps` ran a strongly-connected-components walk over every folder's `dependsOn` edges; `low-coupling` compared each module with every other module's path; `layer-separation`, `shape-classes-around-resources`, `do-not-invent-parallel-object-models`, `extensions-live-with-the-domain`, `use-explicit-dependencies`, and `domain-exception-carries-context` asked a class index (`ClassGraph`, made per check through `RuleCheckContext.index`) to compare each class with the others; `eliminate-duplication` fingerprinted and bucketed every operation's body; `no-module-per-class` scanned every class for each module. BDD's `no-implementation` and LERN's screen-story rule cross-referenced one node type against another the same way.

The answer such a rule gives is a fact about the code, not about the rule: which of a module's classes code outside it names is what the module is, whether or not a rule then holds it to 40%. Worked out at check time, it could not be seen in the graph, could not be queried, and was worked out again on every check.

## Decision

Rules come from facts; facts are assembled when the graph is built. A rule's check (`check` or `check_practice`) reads only a node's facts (`node.get_fact`), its identity and source, and the graph's edges, and compares them with the rule's limit. Whatever compares one node with others is a fact the practice records when its read ends, over every node it holds — those it read now and those a refresh kept, from their saved facts and the graph's edges (CDR 0002) — so a refresh of a few files records it again over the whole practice and stays right when it depends on other files, and a graph read back from `graph.json` holds it as saved.

Clean Engineering records these in its model (*ComparedFacts*, `model/compared_facts.py`, run by its *GraphReading* after the call links, with the folder, class, and operation facts in `folder_facts.py`, `class_facts.py`, and `operation_facts.py`), which holds *ClassGraph*, *ImportCycles*, and *NearCopies*, moved into the model from the rules package. A folder keeps the class names its production files import by file (`imported_names_by_file`), so a refresh that reads one file again replaces only that file's names. BDD records `in_developed_spec` on each observation and context after its specs are read; LERN's overlay records `has_screen_story` on each story after it reads the screen story files. `RuleCheckContext.index`, which only made indexes at check time, is deleted. The saved shape is now 4, so a graph saved without these facts is read from the folder again.

`deep-module` also changes how it counts, at the user's direction: a module is measured over its whole subtree — its files, its packages, and its nested modules, each nested module measured again on its own — and a class is public for a module when production code outside that subtree names it. Each module keeps `subtree_class_count`, `public_classes` (each with the folders outside the subtree that name it), `public_class_count`, and `private_class_count`.

## Considered options

- **Keep the computation in the rule, cached per check.** Rejected: the answer stays invisible to anyone reading the graph, and it is still computed again for each check.
- **Let each rule record its own facts in a build hook.** Rejected: the facts describe the code, so the practice's reading, which already links every class after a read, owns them; a rule that wrote facts would make the rules package a second reader of the graph.

## Consequences

- A new rule that needs to compare a node with others adds a fact to its practice's reading and reads it; a rule that walks other nodes to work an answer out is a defect.
- The rules hit the same nodes with the same messages as before (checked on this repository and on an older revision of it, 15 and 1,803 hits, before and after, fresh and read back from a saved graph); `deep-module`'s verdicts come from the new counting.
- The facts can be read from the graph: each Clean Engineering Module node in `graph.json` (`practices.clean_engineering.nodes[].facts`) carries its subtree's class counts and public classes.
- Not moved: Stories' `given-names-complex-state-root-first`, which reads the DDD model's aggregates for each step it checks (`_owned_parts`), and *ConformsToSchema*, which reads only edges.
