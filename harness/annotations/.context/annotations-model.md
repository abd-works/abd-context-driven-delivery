# harness/annotations

An *Annotation* is what an author types on a class or operation to say how CDD treats it; a *Destination* is an annotation that says where a member is published, and an *OmissionAnnotation* leaves a member out. Each publisher defines its own destinations (harness/installation, harness/mcp, harness/hooks), and every kind joins one registry, `annotation_kinds`, as it is defined. *Name* is one name written in every case CDD needs: `StoryMap`, `story_map`, and `story-map` are the same *Name*. `class_folder(cls)` is the folder a class is defined in.

- **Purpose:** Hold the annotations an author types, the one place a member's destinations are read, and the one way a name is written in each case, below every publisher, so publishers depend on toolsets and never the other way round.
- **Seam (terms):** Annotation, NamesAnnotation, Destination, ClassRegistry, Name, `annotation_kinds`, `class_folder`, and the annotations an author types `@hosted_only`, `@noCatalog`, `@noDeploy` (their classes, *OmissionAnnotation*, and the kinds of kind stay behind them)
- **Dependencies (one-way):** *(none)*

## Annotation

The base of every annotation an author types: it sets its `flag` on what it annotates, and `annotates(target)` reads it back. Each kind joins `annotation_kinds` as it is defined.

------
+ flag: str
+ copied: bool
----
+ annotates(target: Any): bool
+ written_as(): str
+ installs_member(): bool
+ companion_flags(): tuple[str, ...]
+ annotate(target: Any): Any

## NamesAnnotation : Annotation

An annotation that records a tuple of names on what it annotates and reads them back: the fields that name one object (`@identity`) and the arguments a tool takes from its call (*TakesFromCall*) are its kinds, each naming only its flag.

+ NamesAnnotation(*names: str)
------
----
+ annotate(target: Any): Any
+ names_on(target: Any): tuple[str, ...]

## OmissionAnnotation : Annotation

The base of an annotation that leaves what it annotates out of something: the catalog (`@noCatalog`) or every destination (`@noDeploy`).

------
+ omits_install: bool
----
+ annotates(target: Any): bool

## HostedOnly : OmissionAnnotation

`@hosted_only` on a class whose tools run only through the practice or toolset that holds it, such as a practice's rules or its fidelities: install and the hook server load no toolset of it on its own. It is read on the class it was written on, never inherited, so each practice that subclasses one stays a toolset.

------
----
+ annotates(target: Any): bool

## NoCatalog : OmissionAnnotation

`@noCatalog` on a class or operation: the catalog leaves it out; install still publishes it.

------
----

## NoDeploy : OmissionAnnotation

`@noDeploy` on an operation: install publishes it to no destination, whatever else annotates it; the catalog can still list it.

------
+ omits_install: bool
----

## Destination : Annotation

The base of an annotation that says where install publishes a member, by its `channel`: a skill, a command, a rules file, an MCP tool, or a hook.

------
+ channel: str
+ enlists_member: bool
----
+ name_annotated_on(operation: Any): str
+ disabled_on(operation: Any): bool
	// reads `{flag}_disabled`, which a destination that holds `disabled` sets, as `@Hook(..., disabled=True)` does

## Name

*Name* is one name, such as a class, an event, or a fidelity, that CDD writes in several cases: `StoryMap`, `story_map`, and `story-map` are the same name, and so are a title's words (`Pet visits`, `pet-visits`, `PetVisits`).

+ Name(text: str)
------
+ words: list[str]
+ snake: str
+ kebab: str
+ camel: str
+ spellings: list[str]
+ title_words: list[str]
+ title_slug: str
+ title_snake: str
+ title_pascal: str
+ title_camel: str
----
