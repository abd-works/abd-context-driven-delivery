# Name lives in the annotations module, and the module is all seam

The round-5, round-6 and round-7 reviews (harness core, row 11 in round 7) asked for *Name* to move to a small module of its own, or for a record that keeps it, and counted 7 of the module's 8 classes as public (`deep-module`).

*Name* stays in `harness/annotations`.

## Why

- **The annotations need it, and nothing may sit below them.** `Annotation.written_as` turns a kind's class name into the name an author types (`skill`, `agent_tool`), so the module that defines annotations reads *Name* itself. `harness/annotations` is the lowest module of the framework; a separate `harness/name` module would sit beside it with one class and one reader below it, and every module that publishes a name (markdown, agent_tools, installation, hooks, mcp) would depend on two bottom modules for one job.
- **The one rule is that every case conversion reads *Name*.** Keeping it with the annotations that publish names under it keeps that rule in one card, which the module's constraint states.
- **The module is a set of bases and annotations an author types, so it is all seam by design.** *Annotation*, *OmissionAnnotation*, *Destination*, *NamedDestination* and *NamesAnnotation* are bases that publishers subclass; *HostedOnly* and *Toast* are annotations an author writes on a class or operation; `class_folder` is the folder every reader of a class's markdown starts from. A deep module hides a large job behind a small interface; this module has no large job to hide, and its registry's own class (*AnnotationKinds*) is already reached only through `annotation_kinds`.

## Consequences

- Converting a name between cases anywhere else is a second conversion, which the module's constraint forbids.
- A deep-module count on this module reads its purpose, not a leak; the round-8 review should not count it.
