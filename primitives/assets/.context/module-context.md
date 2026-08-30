# assets

**Purpose:** Locate and merge a context tool’s `contexts`, `examples`, and `templates` into the first generate blob — without splitting kit files on disk.

**Primary use case:** Stories / Clean Engineering / DDD / UX / BDD generate at one fidelity and format. The host already knows those two values; this module keeps only the matching slices.

**Rationale:** The leftover clock after single-command is the model reading an unfiltered dump. Filter at expand time. One `stories.md` / `clean_engineering.md`, one `examples/` tree, one `templates/` tree.

**Seam:** `AssetLocator` holds host `fidelity` / `format`. `.contexts` / `.examples` / `.templates` locate, merge, and filter. Instruction expansion only calls `AssetLocator.expand()`.

**Public API:** `AssetLocation` (`label`, `fidelity`, `format`), `AssetLocator` (those properties + slot properties), `Asset`, `AssetCollection` (collect applies the matching filter).

**Dependencies:** host `fidelity` / `format`. Thin helpers stay private to this package.
