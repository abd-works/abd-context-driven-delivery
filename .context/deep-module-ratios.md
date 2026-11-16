# Deep-module ratios

How many of each module's classes other modules use (public) and how many stay inside it (private), against the Clean Engineering rule `deep-module`.

**The rule:**
- A **module** is a folder that owns `.context/module-context.md`. A folder without one is a package and rolls up into the module above it.
- A module is measured over its **whole subtree**: its own files, its nested packages and its nested modules. A nested module also gets a row of its own, over its own subtree.
- A class is **public** when production code **outside** the module's subtree names it. Use inside the subtree does not count. Tests and fixtures don't count either way, and neither do private records with no behaviour.
- **Threshold:** at most **40%** of a module's classes may be public. "Allowed" is 40% of the total, rounded down. A module with more public classes than that fails.
- Modules with fewer than 3 classes are not measured.

Counted on branch `version-1-refactoring` at `1606df425`, from the facts the graph records on each module node (`subtree_class_count`, `public_class_count`, `private_class_count`, `public_classes`). Ordered by share public, highest first.

| Module | Public | Private | Total | % public | Allowed (40%) | Status |
|---|---|---|---|---|---|---|
| `harness/process` | 6 | 2 | 8 | 75% | 3 | **Fails** (user decides later) |
| `harness/design_canvas` | 4 | 6 | 10 | 40% | 4 | At the limit |
| `harness/guidance` | 18 | 28 | 46 | 39% | 18 | At the limit |
| `harness/markdown` | 6 | 10 | 16 | 38% | 6 | At the limit |
| `harness/installation` | 16 | 30 | 46 | 35% | 18 | OK |
| `harness/annotations` | 5 | 10 | 15 | 33% | 6 | OK |
| `harness/hooks` | 9 | 18 | 27 | 33% | 10 | OK |
| `harness/whiteboard` | 4 | 8 | 12 | 33% | 4 | At the limit |
| `harness/mcp` | 9 | 24 | 33 | 27% | 13 | OK |
| `harness/agent_tools` | 13 | 39 | 52 | 25% | 20 | OK |
| `harness/graph` | 28 | 85 | 113 | 25% | 45 | OK |
| `harness/guidance_actions` | 3 | 10 | 13 | 23% | 5 | OK |
| `harness` | 104 | 414 | 518 | 20% | 207 | OK |
| `harness/diagnostics` | 8 | 32 | 40 | 20% | 16 | OK |
| `cdd_guidance/practices/clean_engineering/model` | 30 | 135 | 165 | 18% | 66 | OK |
| `harness/chat` | 2 | 11 | 13 | 15% | 5 | OK |
| `cdd_guidance/actions` | 3 | 18 | 21 | 14% | 8 | OK |
| `cdd_guidance/practices/clean_engineering/model/drawio` | 3 | 19 | 22 | 14% | 8 | OK |
| `space/session` | 13 | 82 | 95 | 14% | 38 | OK |
| `cdd_guidance/practices/clean_engineering` | 21 | 186 | 207 | 10% | 82 | OK |
| `cdd_guidance/practices/ux/story-demo` | 2 | 19 | 21 | 10% | 8 | OK |
| `space/repo` | 4 | 37 | 41 | 10% | 16 | OK |
| `harness/chat-ui/pane` | 1 | 12 | 13 | 8% | 5 | OK |
| `cdd_guidance/practices/bdd` | 2 | 27 | 29 | 7% | 11 | OK |
| `cdd_guidance/practices/stories` | 12 | 176 | 188 | 6% | 75 | OK |
| `cdd_guidance/practices/ux/model` | 3 | 45 | 48 | 6% | 19 | OK |
| `cdd_guidance/context_setup` | 1 | 18 | 19 | 5% | 7 | OK |
| `space` | 9 | 231 | 240 | 4% | 96 | OK |
| `cdd_guidance/practices/ux` | 2 | 73 | 75 | 3% | 30 | OK |
| `cdd_guidance/practices` | 10 | 584 | 594 | 2% | 237 | OK |
| `cdd_guidance/practices/ddd` | 1 | 61 | 62 | 2% | 24 | OK |
| `harness/catalog_generator` | 1 | 40 | 41 | 2% | 16 | OK |
| `space/kanban` | 2 | 101 | 103 | 2% | 41 | OK |

**No public classes (0%):** `cdd_guidance/patterns`, `cdd_guidance/practices/agent_bdd`, `cdd_guidance/practices/stories/app`, `cdd_guidance/builders`, `harness/files_app`, `scripts`, `scripts/unit_guard`, `tools`. Each holds between 3 and 54 classes. `cdd_guidance/patterns` reads 0% because the practices reach its classes by registration at import, not by naming them.

**Not measured (fewer than 3 classes):** `harness/git` and `cdd_guidance/practices/sketch_document`.

## How to read it again

In the session's saved graph (`.sessions/<session>/.context/graph.json`), each node under `practices.clean_engineering.nodes` with `type` `Module` carries the counts in its `facts`. In Python, with the graph loaded:

```python
[(m.source.file, m.get_fact("public_class_count"), m.get_fact("subtree_class_count"))
 for m in practice.reading.in_graph.nodes("Module")]
```
