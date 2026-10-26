# Schema practice builder — plan

Status: planned, not started. Parked 2026-10-26 so the facts refactor could land first.

## Goal

Every practice and pattern is built the same way, and `cdd_guidance/builders/create_practice_guidance`
guides an AI through that way when it creates or edits one. The chain, in order:

1. **Practice has a schema** — `model/schema.yaml` (node types, fields, `is:` supertypes, rule slugs per type).
2. **Schema has nodes** — each schema type is one graph node type.
3. **Nodes are implemented as model nodes** — classes that inherit the base graph node
   (`BoundNode` today, in `harness/graph/bound_node.py`; itself a `harness.graph.graph.Node`).
4. **Nodes have rules** — markdown rule prose (slug + text in the practice guidance) and an executable
   `PracticeGraphRule` per slug, registered in the practice's `rules/__init__.py`.
5. **Rules require facts** — a rule reads only `node.get_fact(key)` and graph structure
   (edges, `context.practice.registered(id)`). It never opens a file, parses code, or reads source text.
6. **Facts are loaded onto the graph node** — whoever builds the graph sets them with
   `node.set_fact(key, value)` (or writes them into the row's data payload). A fact a whole file owns
   lives once on the file's top node; children read it through `get_fact`, which falls back to the parent.

## What already exists (landed with the facts refactor)

- `Node.set_fact / get_fact / has_fact` in `harness/graph/graph.py`; `get_fact` walks up direct parents.
- Every practice's executable rules read facts only: stories, clean_engineering, ddd, bdd, ux, and the
  lern_domain_driven pattern (mern has no rules of its own).
- Fact loaders today:
  - Clean engineering — language parsers (python / typescript / javascript models) fill attributes on
    `OoadClass`, `Operation`, `Parameter`, `Module`; `harness/graph/working_copy.py` copies them into rows
    (`_CLASS_FACTS`, `_OPERATION_FACTS`, `_PARAMETER_FACTS`, `_FOLDER_FACTS`).
  - DDD — `TacticalBuildingBlock.load_tactical_facts` in `practices/ddd/model/nodes.py`; folder facts on
    Aggregate / BoundedContext rows.
  - BDD — `PythonBddModel` / `TypeScriptBddModel.parse_code` build the describe tree from spec code;
    `BddModel.load_source_facts` and `BehaviorNode.load_span_facts`; recorder `_record_bdd`.
  - Stories — `load_map_facts` on story nodes; file facts on the Story row in `GraphStoryModel`.
  - LERN — `patterns/lern_domain_driven/tier_facts.py`, set on tier nodes by `_set_tier_facts`.

## Steps

1. **Reverse-engineer every practice and pattern** (stories, clean_engineering, ddd, bdd, ux,
   lern_domain_driven, mern_domain_driven). Per schema type: implementing model class, rule slugs
   (markdown and code), facts each code rule reads, who sets each fact. Write it as
   `create_practice_guidance/practice_inventory.md`. Flag gaps: schema types with no model class,
   markdown slugs with no code rule, code rules with no test, facts nobody sets.
2. **Meta-schema** — `create_practice_guidance/meta_schema.yaml`, in the style of the practice
   `schema.yaml` files: practice → schema → node type → model node → rule (markdown, code) →
   required facts → fact setter → recorder. Patterns: overlay → practice → added node types and rules.
3. **Move the base node** into the builder as the meta-model element every practice node inherits.
   Pick the module path under `create_practice_guidance/`; update every import (no alias left at
   `harness/graph/bound_node.py`); check for import cycles with `harness.graph.graph`.
4. **Builder guidance** — update `create_practice_guidance.md` (and templates) to walk through, in order:
   schema, model nodes, fact setting, recorder, rules in markdown, rules in code (facts only), specs
   (one fault / clean pair per rule through the real working-copy build).
5. **Specs** — builder specs plus the graph specs that import the base node; record before/after counts.

## Known follow-ups found during the refactor

- `.gitignore` line 80 (`_*`) ignores every `_examples` fixture folder; the practice specs read from
  them. The clean_engineering, ddd, and bdd `model/python/_examples` folders were force-added.
- Two clean_engineering fixtures disagree with their rules: `keep-classes-single-responsibility`
  (fixture has 11 public operations, rule budget is 18) and `use-exceptions-properly`
  (TypeScript `catch { }` is treated as intentional by the detector).
- `graph_view_spec.py` writes fixtures into `harness/graph/examples/folds/` and never removes them.
- Python module-level functions in a file that also has classes are hung on the first class by the
  Python parser and dropped from the graph by `OoadClass.own_operations`.
