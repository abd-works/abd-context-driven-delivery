# Deep-module ratios

How much of each module's interface other modules can call, against the Clean Engineering rule `deep-module`, with the module's class exposure beside it as context.

**Why methods:** a module's interface is the methods its callers can call. A deep module hides much behind a small interface (John Ousterhout, *A Philosophy of Software Design*): many methods inside, few of them reachable from outside. So `deep-module` judges the share of a module's methods that sit on its seam. How many of its classes are public is a secondary signal: it shows how much of the module's design is exposed, but one public class with forty methods is a wider interface than four public classes with two each, so the class share never fails a module on its own.

**The rule:**
- A **module** is a folder that owns `.context/module-context.md`. A folder without one is a package and rolls up into the module above it. In `cdd_guidance` that is one module per direct child and one per practice.
- A module is measured over its **whole subtree**: its own files, its nested packages and its nested modules. A nested module also gets a row of its own, over its own subtree.
- **Methods:** every operation of the module's counted classes, getters, setters and constructors included, and every module-level function of its production files. Methods are counted where they are declared: a class that inherits its interface, such as a practice or builder deriving from `PracticeGuidance`, adds those methods to the module that declares them.
- **Public methods:** public by visibility. In Python, a name without a leading `_` (so `__init__` and other dunders are not public); in TypeScript, JavaScript and Java, one not marked `private` and not starting with `#`, and for a module-level function, one its file exports. A constructor is never public. **Private methods** are the rest.
- **Seam methods:** the public methods on the module's public classes. These are the methods the module exposes to other modules. Module functions are on no class, so they are never seam methods.
- **Threshold:** at most **35%** of a module's methods may be seam methods. "Allowed seam methods" is 35% of the methods, rounded down. A module with more seam methods than that fails. A module with fewer than 10 methods is not measured.

**The classes (context only):**
- Classes are counted as **definitions**: two classes of the same name in different files are two classes. Private classes are the total minus the public ones.
- A class is **public** when it leaves the module's subtree by one of three routes:
  - **named**: production code outside the subtree imports it, re-exports it, or reaches it as `module.Class`. Each import is resolved to the one definition it names, through the module it is imported from, following a package's `__init__.py` or a script's `index.ts` that re-exports it. A script's import of a generated language adapter (`@cdd/...`) names the Python module the adapter is generated from, and `{Class}Data` names the class it sends. An import of a standard or third-party module, a function, constant or type alias, or a star import names no class.
  - **registered**: a package registers it with a framework registry (`PRACTICE_CATALOGUE`, `ACTION_CATALOGUE`, `REGISTERED_PATTERNS`).
  - **published**: the installer publishes it as a toolset (`@agent_toolset`, or a member published as a tool), unless it is `@hosted_only` (its host is the toolset) or `@noDeploy`.
- Use inside the subtree does not count. A name starting with `_` is never public. Tests, fixtures, examples (`examples` and `_examples` folders) and test doubles (`mock_*`, `fake_*`) don't count either way, and neither do private records with no behaviour.
- "How public classes are reached" counts each public class once, by its first route in the order named, registered, published.

Counted on branch `version-1-refactoring` at `725163e74`, with this change applied, from the facts the graph records on each module node (`operations_total`, `operations_public`, `operations_private`, `seam_operations`, `subtree_class_count`, `public_class_count`, `private_class_count`, `public_classes`). Ordered by module, alphabetically.

| Module | Methods | Public methods | Private methods | Seam methods | % seam | Allowed seam methods (35%) | Status | Public classes | Private classes | Total classes | % public classes | How public classes are reached (named / registered / published) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `cdd_guidance/actions` | 153 | 62 | 91 | 33 | 22% | 53 | OK | 11 | 10 | 21 | 52% | 2 / 9 / 0 |
| `cdd_guidance/agents` | 0 | 0 | 0 | 0 | n/a | 0 | Not measured (fewer than 10 methods) | 0 | 0 | 0 | n/a | 0 / 0 / 0 |
| `cdd_guidance/builders` | 0 | 0 | 0 | 0 | n/a | 0 | Not measured (fewer than 10 methods) | 2 | 1 | 3 | 67% | 0 / 0 / 2 |
| `cdd_guidance/catalog` | 185 | 0 | 185 | 0 | 0% | 64 | OK | 0 | 0 | 0 | n/a | 0 / 0 / 0 |
| `cdd_guidance/context_setup` | 66 | 31 | 35 | 13 | 20% | 23 | OK | 2 | 17 | 19 | 11% | 1 / 0 / 1 |
| `cdd_guidance/patterns` | 137 | 77 | 60 | 5 | 4% | 47 | OK | 5 | 49 | 54 | 9% | 0 / 5 / 0 |
| `cdd_guidance/practices` | 3194 | 1768 | 1426 | 129 | 4% | 1117 | OK | 17 | 586 | 603 | 3% | 5 / 3 / 9 |
| `cdd_guidance/practices/agent_bdd` | 135 | 59 | 76 | 2 | 1% | 47 | OK | 1 | 26 | 27 | 4% | 0 / 0 / 1 |
| `cdd_guidance/practices/bdd` | 138 | 71 | 67 | 0 | 0% | 48 | OK | 1 | 28 | 29 | 3% | 1 / 0 / 0 |
| `cdd_guidance/practices/clean_engineering` | 1190 | 602 | 588 | 162 | 14% | 416 | OK | 21 | 195 | 216 | 10% | 20 / 0 / 1 |
| `cdd_guidance/practices/ddd` | 267 | 161 | 106 | 1 | 0% | 93 | OK | 1 | 61 | 62 | 2% | 1 / 0 / 0 |
| `cdd_guidance/practices/sketch_document` | 17 | 5 | 12 | 5 | 29% | 5 | At the limit | 2 | 0 | 2 | 100% | 2 / 0 / 0 |
| `cdd_guidance/practices/stories` | 995 | 584 | 411 | 138 | 14% | 348 | OK | 14 | 174 | 188 | 7% | 10 / 0 / 4 |
| `cdd_guidance/practices/tdd` | 4 | 3 | 1 | 1 | 25% | 1 | Not measured (fewer than 10 methods) | 1 | 2 | 3 | 33% | 1 / 0 / 0 |
| `cdd_guidance/practices/ux` | 445 | 282 | 163 | 2 | 0% | 155 | OK | 1 | 74 | 75 | 1% | 1 / 0 / 0 |
| `cdd_guidance/references` | 0 | 0 | 0 | 0 | n/a | 0 | Not measured (fewer than 10 methods) | 0 | 0 | 0 | n/a | 0 / 0 / 0 |
| `cdd_guidance/rules` | 0 | 0 | 0 | 0 | n/a | 0 | Not measured (fewer than 10 methods) | 0 | 0 | 0 | n/a | 0 / 0 / 0 |
| `harness` | 3579 | 2108 | 1471 | 711 | 20% | 1252 | OK | 107 | 411 | 518 | 21% | 101 / 0 / 6 |
| `harness/agent_tools` | 316 | 157 | 159 | 78 | 25% | 110 | OK | 13 | 39 | 52 | 25% | 13 / 0 / 0 |
| `harness/annotations` | 51 | 41 | 10 | 18 | 35% | 17 | **Fails** | 5 | 10 | 15 | 33% | 5 / 0 / 0 |
| `harness/catalog_generator` | 293 | 151 | 142 | 39 | 13% | 102 | OK | 2 | 39 | 41 | 5% | 1 / 0 / 1 |
| `harness/chat` | 65 | 44 | 21 | 24 | 37% | 22 | **Fails** | 4 | 9 | 13 | 31% | 4 / 0 / 0 |
| `harness/chat-ui/pane` | 357 | 234 | 123 | 0 | 0% | 124 | OK | 0 | 13 | 13 | 0% | 0 / 0 / 0 |
| `harness/design_canvas` | 38 | 32 | 6 | 24 | 63% | 13 | **Fails** | 4 | 6 | 10 | 40% | 4 / 0 / 0 |
| `harness/diagnostics` | 164 | 95 | 69 | 49 | 30% | 57 | OK | 12 | 28 | 40 | 30% | 10 / 0 / 2 |
| `harness/files_app` | 186 | 86 | 100 | 0 | 0% | 65 | OK | 0 | 18 | 18 | 0% | 0 / 0 / 0 |
| `harness/git` | 7 | 2 | 5 | 2 | 29% | 2 | Not measured (fewer than 10 methods) | 2 | 0 | 2 | 100% | 2 / 0 / 0 |
| `harness/graph` | 809 | 515 | 294 | 153 | 19% | 283 | OK | 25 | 88 | 113 | 22% | 25 / 0 / 0 |
| `harness/guidance` | 338 | 233 | 105 | 165 | 49% | 118 | **Fails** | 18 | 28 | 46 | 39% | 18 / 0 / 0 |
| `harness/guidance_actions` | 78 | 44 | 34 | 19 | 24% | 27 | OK | 3 | 10 | 13 | 23% | 3 / 0 / 0 |
| `harness/hooks` | 145 | 91 | 54 | 51 | 35% | 50 | **Fails** | 9 | 18 | 27 | 33% | 9 / 0 / 0 |
| `harness/installation` | 308 | 149 | 159 | 77 | 25% | 107 | OK | 17 | 29 | 46 | 37% | 17 / 0 / 0 |
| `harness/markdown` | 126 | 62 | 64 | 44 | 35% | 44 | At the limit | 6 | 10 | 16 | 38% | 6 / 0 / 0 |
| `harness/mcp` | 204 | 105 | 99 | 41 | 20% | 71 | OK | 9 | 24 | 33 | 27% | 8 / 0 / 1 |
| `harness/process` | 46 | 25 | 21 | 18 | 39% | 16 | **Fails** | 6 | 2 | 8 | 75% | 6 / 0 / 0 |
| `harness/whiteboard` | 48 | 42 | 6 | 32 | 67% | 16 | **Fails** | 4 | 8 | 12 | 33% | 4 / 0 / 0 |
| `scripts` | 126 | 38 | 88 | 0 | 0% | 44 | OK | 0 | 17 | 17 | 0% | 0 / 0 / 0 |
| `scripts/unit_guard` | 9 | 5 | 4 | 0 | 0% | 3 | Not measured (fewer than 10 methods) | 0 | 4 | 4 | 0% | 0 / 0 / 0 |
| `space` | 1780 | 1159 | 621 | 334 | 19% | 623 | OK | 27 | 200 | 227 | 12% | 18 / 0 / 9 |
| `space/kanban` | 1000 | 632 | 368 | 149 | 15% | 350 | OK | 10 | 93 | 103 | 10% | 6 / 0 / 4 |
| `space/repo` | 168 | 101 | 67 | 47 | 28% | 58 | OK | 5 | 23 | 28 | 18% | 4 / 0 / 1 |
| `space/session` | 603 | 420 | 183 | 189 | 31% | 211 | OK | 21 | 74 | 95 | 22% | 17 / 0 / 4 |
| `tools` | 100 | 56 | 44 | 28 | 28% | 35 | OK | 6 | 10 | 16 | 38% | 1 / 0 / 5 |

**Over the limit:** `harness/annotations`, `harness/chat`, `harness/design_canvas`, `harness/guidance`, `harness/hooks`, `harness/process` and `harness/whiteboard`. These are real findings under the method measure, not tuned away.

**Reading some rows:**
- `cdd_guidance/builders` and `cdd_guidance/practices/bdd` show public classes but no seam methods: `CreateAgentToolset`, `CreatePracticeGuidance` and `Bdd` declare no methods of their own. Their tools are the methods of `PracticeGuidance`, counted once in `harness/guidance`.
- `harness/chat-ui/pane` has many public methods but no seam: its public methods are the functions its files export to the Claude Code mod host that loads them, and no module of the repository imports its classes. Its `@cdd/...` imports point the other way; they make the Python classes they reach public in their own modules.
- `cdd_guidance/catalog` holds no counted classes; its methods are the functions of the catalog's page scripts, none of them exported.

**Left out as examples and doubles:** `cdd_guidance/catalog/examples/ddd/tactics.ts` (9 classes) and `space/repo/mock_repo.py` (13 classes, the `MockGit` test double), besides every `_examples` folder.

## How to read it again

In the session's saved graph (`.sessions/<session>/.context/graph.json`), each node under `practices.clean_engineering.nodes` with `type` `Module` carries the counts in its `facts`. In Python, with the graph loaded:

```python
[(m.source.file, m.get_fact("seam_operations"), m.get_fact("operations_total"), m.get_fact("public_class_count"))
 for m in practice.reading.in_graph.nodes("Module")]
```
