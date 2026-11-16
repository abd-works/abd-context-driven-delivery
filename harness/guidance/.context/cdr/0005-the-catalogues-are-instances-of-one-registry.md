# The catalogues are instances of one registry

Supersedes `0001-the-catalogues-are-registries-of-classes.md`.

The version-1 refactoring review (Clean Engineering code, `prefer-instance-operations`, `eliminate-duplication`, `use-explicit-dependencies`) flagged three copies of one mechanism: `PracticeCatalogue.register`, `ActionCatalogue.register`, and `PatternOverlays.register` each kept classes in a `ClassVar` and answered through classmethods, and `Action.run_on` and `FidelityActions` reached the class-level runner and actions as globals.

## Decision

- There is one mechanism for classes a package registers with the framework: *ClassRegistry* (`harness/annotations/class_registry.py`), an instance that holds classes in the order they were registered, each by its name (`register`, `classes`, `names`, `has`, `named`).
- Each catalogue is an instance the process holds once, beside the classes it lists, as `annotation_kinds`, `SERVER_CHANNELS`, and `SESSION_OPENING` are: `PRACTICE_CATALOGUE` (*PracticeCatalogue*), `ACTION_CATALOGUE` (*ActionCatalogue*), and `REGISTERED_PATTERNS` (a *ClassRegistry* of pattern classes, by their `pattern` name). Every operation is an instance operation; the factories `create` and `create_all` make new practices and stay so named.
- The registration still happens when the package that defines the classes is imported (`cdd_guidance/practices`, `cdd_guidance/actions`, `cdd_guidance/patterns`), because the framework never imports them, and every process that loads the repository's toolsets imports them.
- An object that works with a catalogue is handed it: an *Action* holds the catalogue that made it and runs through its runner; *FidelityActions* is made with the catalogue; *ApproachStage* is made with the action catalogue and reads its actions from it; *PatternOverlays* is made with the registry of patterns (the process's unless a caller hands it another).
- `PracticeCatalogue.keys()` is now `names`, the word every registry uses for the identifiers of what it holds.
- `create_all()` answers a *PracticeSet*, which answers what a slug names (`answering`, `practice_answering`, `named`, `slugs`), so a guidance action and a diagnostics probe ask their own set instead of each searching the practices.

## Why an instance held once per process, not one handed down from the MCP host

The reasons of `0001` still hold for where the list lives: every process (the hook daemon, the catalog command, the installer, the probes, every spec) needs the same list, and only one of them is the MCP host. What changed is what holds it: an instance whose operations read its own state, which can be handed to the objects that work with it, rather than class-level state every caller reaches.

## Consequences

- Readers write `PRACTICE_CATALOGUE.create_all()`, `ACTION_CATALOGUE.actions`, `REGISTERED_PATTERNS.register(...)`.
- A spec can make a catalogue or a registry of its own and hand it to what it tests.
