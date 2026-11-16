# Deep-module ratios

How many of each module's classes leave it (public) and how many stay inside it (private), against the Clean Engineering rule `deep-module`, with the module's methods beside them.

**The rule:**
- A **module** is a folder that owns `.context/module-context.md`. A folder without one is a package and rolls up into the module above it. In `cdd_guidance` that is one module per direct child and one per practice.
- A module is measured over its **whole subtree**: its own files, its nested packages and its nested modules. A nested module also gets a row of its own, over its own subtree.
- Classes are counted as **definitions**: two classes of the same name in different files are two classes. Total, public and private all count definitions, and private is total minus public.
- A class is **public** when it leaves the module's subtree by one of three routes:
  - **named**: production code outside the subtree imports it, re-exports it, or reaches it as `module.Class`. Each import is resolved to the one definition it names, through the module it is imported from, following a package's `__init__.py` or a script's `index.ts` that re-exports it. An import of a standard or third-party module, a path alias such as `@cdd/*`, a function, constant or type alias, or a star import names no class.
  - **registered**: a package registers it with a framework registry (`PRACTICE_CATALOGUE`, `ACTION_CATALOGUE`, `REGISTERED_PATTERNS`).
  - **published**: the installer publishes it as a toolset (`@agent_toolset`, or a member published as a tool), unless it is `@hosted_only` (its host is the toolset) or `@noDeploy`.
- Use inside the subtree does not count. A name starting with `_` is never public. Tests, fixtures, examples (`examples` and `_examples` folders) and test doubles (`mock_*`, `fake_*`) don't count either way, and neither do private records with no behaviour.
- **Threshold:** at most **40%** of a module's classes may be public. "Allowed" is 40% of the total, rounded down. A module with more public classes than that fails.
- Modules with fewer than 3 classes are not measured.

**The methods (for reading only; the limit stays on classes):**
- **Methods**: every operation of the module's counted classes, getters, setters and constructors included, and every module-level function of its production files.
- **Public methods**: those public by visibility. In Python, a name without a leading `_` (so `__init__` and other dunders are not public); in TypeScript, JavaScript and Java, one not marked `private` and not starting with `#`. A constructor is never public. **Private methods** are the rest.
- **Seam methods**: the public methods on the module's public classes, whatever route makes the class public. This is how many methods the module exposes to other modules. Module functions are on no class, so they are never seam methods.
- **% public methods** is public methods over methods; **% seam** is seam methods over methods.

Counted on branch `version-1-refactoring` at `438c9dfbd`, with the exact counting of this change applied, from the facts the graph records on each module node (`subtree_class_count`, `public_class_count`, `private_class_count`, `public_classes`, `operations_total`, `operations_public`, `operations_private`, `seam_operations`). "How public classes are reached" counts each public class once, by its first route in the order named, registered, published. Ordered by module, alphabetically.

| Module | Public classes | Private classes | Total classes | % public | Allowed (40%) | How public classes are reached (named / registered / published) | Methods | Public methods | Private methods | % public methods | Seam methods | % seam | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `cdd_guidance/actions` | 11 | 10 | 21 | 52% | 8 | 2 / 9 / 0 | 153 | 62 | 91 | 41% | 33 | 22% | **Fails** |
| `cdd_guidance/agents` | 0 | 0 | 0 | n/a | 0 | 0 / 0 / 0 | 0 | 0 | 0 | n/a | 0 | n/a | Not measured (fewer than 3 classes) |
| `cdd_guidance/builders` | 2 | 1 | 3 | 67% | 1 | 0 / 0 / 2 | 0 | 0 | 0 | n/a | 0 | n/a | **Fails** |
| `cdd_guidance/catalog` | 0 | 0 | 0 | n/a | 0 | 0 / 0 / 0 | 185 | 185 | 0 | 100% | 0 | 0% | Not measured (fewer than 3 classes) |
| `cdd_guidance/context_setup` | 2 | 17 | 19 | 11% | 7 | 1 / 0 / 1 | 66 | 31 | 35 | 47% | 13 | 20% | OK |
| `cdd_guidance/patterns` | 5 | 49 | 54 | 9% | 21 | 0 / 5 / 0 | 137 | 77 | 60 | 56% | 5 | 4% | OK |
| `cdd_guidance/practices` | 17 | 586 | 603 | 3% | 241 | 5 / 3 / 9 | 3191 | 1833 | 1358 | 57% | 129 | 4% | OK |
| `cdd_guidance/practices/agent_bdd` | 1 | 26 | 27 | 4% | 10 | 0 / 0 / 1 | 135 | 59 | 76 | 44% | 2 | 1% | OK |
| `cdd_guidance/practices/bdd` | 1 | 28 | 29 | 3% | 11 | 1 / 0 / 0 | 138 | 71 | 67 | 51% | 0 | 0% | OK |
| `cdd_guidance/practices/clean_engineering` | 21 | 195 | 216 | 10% | 86 | 20 / 0 / 1 | 1187 | 601 | 586 | 51% | 162 | 14% | OK |
| `cdd_guidance/practices/ddd` | 1 | 61 | 62 | 2% | 24 | 1 / 0 / 0 | 267 | 161 | 106 | 60% | 1 | 0% | OK |
| `cdd_guidance/practices/sketch_document` | 2 | 0 | 2 | 100% | 0 | 2 / 0 / 0 | 17 | 5 | 12 | 29% | 5 | 29% | Not measured (fewer than 3 classes) |
| `cdd_guidance/practices/stories` | 14 | 174 | 188 | 7% | 75 | 10 / 0 / 4 | 995 | 621 | 374 | 62% | 138 | 14% | OK |
| `cdd_guidance/practices/tdd` | 1 | 2 | 3 | 33% | 1 | 1 / 0 / 0 | 4 | 3 | 1 | 75% | 1 | 25% | At the limit |
| `cdd_guidance/practices/ux` | 1 | 74 | 75 | 1% | 30 | 1 / 0 / 0 | 445 | 311 | 134 | 70% | 2 | 0% | OK |
| `cdd_guidance/references` | 0 | 0 | 0 | n/a | 0 | 0 / 0 / 0 | 0 | 0 | 0 | n/a | 0 | n/a | Not measured (fewer than 3 classes) |
| `cdd_guidance/rules` | 0 | 0 | 0 | n/a | 0 | 0 / 0 / 0 | 0 | 0 | 0 | n/a | 0 | n/a | Not measured (fewer than 3 classes) |
| `harness` | 106 | 412 | 518 | 20% | 207 | 100 / 0 / 6 | 3579 | 2336 | 1243 | 65% | 708 | 20% | OK |
| `harness/agent_tools` | 13 | 39 | 52 | 25% | 20 | 13 / 0 / 0 | 316 | 157 | 159 | 50% | 78 | 25% | OK |
| `harness/annotations` | 5 | 10 | 15 | 33% | 6 | 5 / 0 / 0 | 51 | 41 | 10 | 80% | 18 | 35% | OK |
| `harness/catalog_generator` | 2 | 39 | 41 | 5% | 16 | 1 / 0 / 1 | 293 | 151 | 142 | 52% | 39 | 13% | OK |
| `harness/chat` | 2 | 11 | 13 | 15% | 5 | 2 / 0 / 0 | 65 | 44 | 21 | 68% | 18 | 28% | OK |
| `harness/chat-ui/pane` | 0 | 13 | 13 | 0% | 5 | 0 / 0 / 0 | 357 | 340 | 17 | 95% | 0 | 0% | OK |
| `harness/design_canvas` | 4 | 6 | 10 | 40% | 4 | 4 / 0 / 0 | 38 | 32 | 6 | 84% | 24 | 63% | At the limit |
| `harness/diagnostics` | 12 | 28 | 40 | 30% | 16 | 8 / 0 / 4 | 164 | 95 | 69 | 58% | 49 | 30% | OK |
| `harness/files_app` | 0 | 18 | 18 | 0% | 7 | 0 / 0 / 0 | 186 | 150 | 36 | 81% | 0 | 0% | OK |
| `harness/git` | 2 | 0 | 2 | 100% | 0 | 2 / 0 / 0 | 7 | 2 | 5 | 29% | 2 | 29% | Not measured (fewer than 3 classes) |
| `harness/graph` | 25 | 88 | 113 | 22% | 45 | 25 / 0 / 0 | 809 | 573 | 236 | 71% | 153 | 19% | OK |
| `harness/guidance` | 18 | 28 | 46 | 39% | 18 | 18 / 0 / 0 | 338 | 233 | 105 | 69% | 165 | 49% | At the limit |
| `harness/guidance_actions` | 3 | 10 | 13 | 23% | 5 | 3 / 0 / 0 | 78 | 44 | 34 | 56% | 19 | 24% | OK |
| `harness/hooks` | 9 | 18 | 27 | 33% | 10 | 9 / 0 / 0 | 145 | 91 | 54 | 63% | 51 | 35% | OK |
| `harness/installation` | 17 | 29 | 46 | 37% | 18 | 17 / 0 / 0 | 308 | 149 | 159 | 48% | 77 | 25% | OK |
| `harness/markdown` | 6 | 10 | 16 | 38% | 6 | 6 / 0 / 0 | 126 | 62 | 64 | 49% | 44 | 35% | At the limit |
| `harness/mcp` | 9 | 24 | 33 | 27% | 13 | 8 / 0 / 1 | 204 | 105 | 99 | 51% | 41 | 20% | OK |
| `harness/process` | 6 | 2 | 8 | 75% | 3 | 6 / 0 / 0 | 46 | 25 | 21 | 54% | 18 | 39% | **Fails** |
| `harness/whiteboard` | 4 | 8 | 12 | 33% | 4 | 4 / 0 / 0 | 48 | 42 | 6 | 88% | 32 | 67% | At the limit |
| `scripts` | 0 | 17 | 17 | 0% | 6 | 0 / 0 / 0 | 126 | 38 | 88 | 30% | 0 | 0% | OK |
| `scripts/unit_guard` | 0 | 4 | 4 | 0% | 1 | 0 / 0 / 0 | 9 | 5 | 4 | 56% | 0 | 0% | OK |
| `space` | 18 | 209 | 227 | 8% | 90 | 8 / 0 / 10 | 1780 | 1321 | 459 | 74% | 273 | 15% | OK |
| `space/kanban` | 5 | 98 | 103 | 5% | 41 | 0 / 0 / 5 | 1000 | 794 | 206 | 79% | 123 | 12% | OK |
| `space/repo` | 5 | 23 | 28 | 18% | 11 | 4 / 0 / 1 | 168 | 101 | 67 | 60% | 47 | 28% | OK |
| `space/session` | 18 | 77 | 95 | 19% | 38 | 14 / 0 / 4 | 603 | 420 | 183 | 70% | 162 | 27% | OK |
| `tools` | 6 | 10 | 16 | 38% | 6 | 0 / 0 / 6 | 100 | 56 | 44 | 56% | 28 | 28% | At the limit |

**Over the limit:** `cdd_guidance/actions` (its 9 action toolsets are registered with `ACTION_CATALOGUE`, and `Generate` and `Validate` are also imported), `cdd_guidance/builders` (2 published toolsets of 3 classes) and `harness/process` (6 classes imported from outside). The first two are new under this definition; they are real findings, not tuned away.

**Left out as examples and doubles:** `cdd_guidance/catalog/examples/ddd/tactics.ts` (9 classes) and `space/repo/mock_repo.py` (13 classes, the `MockGit` test double), besides every `_examples` folder, which was already left out.

## How to read it again

In the session's saved graph (`.sessions/<session>/.context/graph.json`), each node under `practices.clean_engineering.nodes` with `type` `Module` carries the counts in its `facts`. In Python, with the graph loaded:

```python
[(m.source.file, m.get_fact("public_class_count"), m.get_fact("subtree_class_count"), m.get_fact("seam_operations"))
 for m in practice.reading.in_graph.nodes("Module")]
```
