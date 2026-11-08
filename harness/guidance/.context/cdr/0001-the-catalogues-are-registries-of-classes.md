# The catalogues are registries of the classes a package registers

The round-6 review (harness core, row 3) flagged `PracticeCatalogue` and `ActionCatalogue` for answering through class operations, and asked for one catalogue instance that the MCP host holds and hands to its callers.

The catalogues stay registries held by their classes. What they hold is a fact of the process, like a class definition: the package that defines the practices (`cdd_guidance/practices/__init__.py`) and the package that defines the actions (`cdd_guidance/actions/__init__.py`) register their classes when they are imported, and the framework never imports them.

## Why the registry is held by the class

- **Every process needs the same list, and only one of them is the MCP host.** The hook daemon (prompt notify), the catalog generator's command line, the installer, the diagnostics probes, the agent BDD harness and every spec read the practices and actions too. An instance held by the MCP host does not reach them; each would have to rebuild it from the same registration, which is a second owner of one list.
- **The framework cannot import what it lists.** `harness/` imports nothing from `cdd_guidance/`, so the list arrives by registration at import time. A registration that the importing module makes has to land somewhere every later reader can find without being handed it; the class is that place, as `ToolCall.open_sessions_with` and `ActionCatalogue.run_actions_with` are for their seams.
- **Objects that hold state are made per set, not shared.** A session makes its own practices (`create_all`), which its graph and its actions share; a caller that works outside any session makes its own with `create(key)`, which now makes the practice's set with it (the practice it extends and its Clean Engineering companion). The shared instances from `practices()` are read only, for readers that work in no session, such as the board's chips and the diagnostics probes; nothing switches them, so they are no current object.

## What round 6 changed

- The slug lookup no longer makes a round trip through `module:Class` text: `toolset_ref`, `key_of` and their helpers are deleted. A guidance action reads a slug once into the practice and fidelity objects of its own set (`PracticeGuidance.answers_to`, `fidelity_called`).
- `PracticeCatalogue.holds` is deleted, and `guidance.py` no longer calls the catalogue at all, so the catalogue alone knows the practice type and the file cycle between them is gone.

## Consequences

- A new process that needs the practices imports the package that registers them, as every process that loads the repository's toolsets already does.
- A caller that changes a practice's fidelity or format makes its own with `create`, never changes the shared instances.
