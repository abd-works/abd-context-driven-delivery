# A property named for the group its class's properties sit under becomes its own parent, and a validate's save never ends

- **Charter:** supervisor, found by the regression run (heavy tier), after exploratory testing closed.
- **Tester:** Bolt (regression run resumed in chat d0e9c5f2).
- **Story:** Map Work Into Knowledge Graph > Build Practice Trees From Source > Read Modules Classes And Operations. No scenario covered a member named as one of the explorer tree's groups.
- **Module and class:** `harness/graph/graph.py`, `NodeTree._holder_for` through `_child_named`: the child that holds the edges of a kind was found by its name alone, so a class's property named `properties` (`OoadClass.properties: list[Property]` in `cdd_guidance/practices/clean_engineering/model/base_class_model.py`, a direct child of its class through its `relative` edge) was taken as the holder of every property of its class, itself included; `_placed_under` then took it as its own parent, since a holder parent gives way to any part.
- **Severity:** blocks work (every validate with `graph: true` on a folder holding such a class never answers; its graph worker spins at full use of one core until killed, and outlives a server stopped by force).
- **Steps:**
  1. Start a spec server with the Clean Engineering, Graph, Validate and Sessions toolsets.
  2. Load a copy of `cdd_guidance/practices` with every practice (`graph.load_working_copy`).
  3. Call `validate.validate` with `guidance: clean-engineering-code`, `graph: true`, `paths: [clean_engineering/model/operation.py, clean_engineering/rules/class_rules.py]`.
- **Expected:** the validate answers with its graph report, as it did when graph_build_heavy_spec was written.
- **Actual:** the worker never finishes: `SavedFiles.reads` walks up `node.parent` from `module_path`, reaches `properties`, whose parent is itself, and loops. graph_build_heavy_spec held the heavy tier past 30 minutes (and a worker orphaned at 17:45 had used three hours of CPU by 21:20). With a walk that remembers what it saw, the loop showed as a RecursionError instead, and every validate answered `isError`.
- **Tier that should catch it:** unit, `graph_reading_spec.py`: a class with a property named as a group of the explorer tree.

## Triage

- **Status:** confirmed. A probe in `SavedFiles` wrote the loop: one node long, `clean_engineering:Property:clean_engineering/model/base_class_model.py:properties:OoadClass`, with no edge from it to itself. Reproduced in a unit fixture: `Ledger.properties: list[Entry]` made `Ledger.total` hang under the property `properties`.
- **Severity:** blocks work.
- **Triaged by:** Bolt; reporter and fixer are the same robot here, since the regression run found it after the testers had closed.

## Fix

- **Scenario:** Group a class's properties apart from a property named for the group (`story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-practice-trees-from-source/read_practice_trees_from_source_story.test.md`).
- **Test (unit):** `cdd_guidance/practices/clean_engineering/reading/graph_reading_spec.py`, with a class whose property is named as the group its properties sit under › should hang no property under a property, itself included. Seen failing (`total` under `properties`), then passing.
- **Fix:** `NodeTree._holder_named` finds the holder of a kind only among the holders (`type == name`), never a part that shares its name.
- **Found with it:** saving a validate's checked graph walked up every node's parents for every node, edge and folder, working out each node's places (and its file's format) each time; `Node.other_places` (ad0a10ac0) and a save that remembers each node's answer (44474bf29) take that from minutes to seconds.
- **Commit:** 8cfa4f875.
