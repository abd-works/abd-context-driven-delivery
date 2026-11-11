# The catalog's utilities are the toolsets of the work and tools layers

`Utility.load_all` (`catalog_generator.py`) shows as utilities the toolset classes the installer finds whose module is in `space` or `tools`, unless annotated `@noCatalog`, and raises when one of those cannot be imported. It tells them apart by the start of each class's module name (`_UTILITY_PACKAGES`). Round 7 (R7-L3, the catalog half of round 6's M11) asked each toolset class to say where it belongs instead, through its install destination or a catalog annotation.

## Decision

Keep sorting by the layer a toolset is written in.

- **The layer is where a toolset belongs.** `AGENTS.md` names the repository's layers: `harness/` is the framework, `space/` is the work (sessions, the repository, the CDD Kanban), `tools/` holds independent toolsets, and `cdd_guidance/` holds the practices and actions, which have pages of their own. A utility is a toolset of the work or tools layer, so the folder its module sits in is the fact the catalog reads, not a name standing in for one.
- **An annotation would repeat the folder and could disagree with it.** Every toolset in `space/` and `tools/` would carry a catalog mark saying what its folder already says, and a new utility written without it would be missing from the catalog with nothing to show why. Reading the layer shows every new toolset there, and `@noCatalog` remains the one way to leave one out.
- **No install destination says it.** Utilities publish through the same MCP, skill, and command destinations as the framework's own toolsets and the actions, so a destination cannot tell them apart.
- **The framework still imports nothing from those layers.** The catalog reads module names the installer already loaded; it names `space.` and `tools.` as layers, never a module in them.

## Consequences

Moving a toolset between layers moves it in or out of the catalog's utilities, which is the intent. If a layer gains toolsets that are not utilities, mark those `@noCatalog`. If the repository's layers are renamed, `_UTILITY_PACKAGES` changes with `AGENTS.md`.
