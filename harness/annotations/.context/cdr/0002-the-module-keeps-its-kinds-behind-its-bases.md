# The module keeps its kinds behind its bases

Round 2 of the Clean Engineering graph rules counted 11 of the module's 15 classes as named by other modules (`deep-module`, at most 40%). `0001` had kept the module "all seam by design"; this decision replaces that part of it. *Name* still lives here, for the reasons `0001` gives.

## Decision

- **A kind of kind is the module's own.** A publisher that needs a member's annotation turned off sets `disabled` on its annotation, and *DestinationKind* records and reads it (`{flag}_disabled`, `disabled_on`) for every destination, so harness/hooks defines no *HookKind*. An annotation that records itself on what it decorates is read back with `AnnotationKind.recorded_on`, so harness/guidance defines no kind for `@on_stage`.
- **A class lives with the one module that uses it.** *NamedDestination* is the base of the file destinations that take a name (`Skill`, `Command`), so it is in `harness/installation/files.py`. *Toast* is shown by the notifier the hook server shows toasts with (`HOOK_TOASTS`, `rules_toast`), so it is in `harness/hooks/hooks.py`.
- **The omission annotations are here.** `@noCatalog` and `@noDeploy` are annotations an author types, siblings of `@hosted_only`, and `annotation_kinds.withholds_install` already reads `@noDeploy`'s `omits_install`; they moved here from `harness/installation/destination.py`. Other modules read an omission through the name an author types (`noCatalog.annotates`, `hosted_only.annotates`, `hosted_only.written_as()`), so *OmissionAnnotation*, *HostedOnly*, *NoCatalog* and *NoDeploy* are named by no other module.

## Consequences

- The classes other modules name are the bases a publisher subclasses (*Annotation*, *NamesAnnotation*, *Destination*), *ClassRegistry*, and *Name*.
- A new publisher that needs a way of answering of its own adds it to the kind here rather than defining a kind of kind in its own module.
