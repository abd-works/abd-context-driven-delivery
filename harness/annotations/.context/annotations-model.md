# harness/annotations

An *Annotation* is what an author types on a class or operation to say how CDD treats it; a *Destination* is an annotation that says where a member is published, and an *OmissionAnnotation* leaves a member out. Each publisher defines its own destinations (harness/installation, harness/mcp, harness/hooks), and every kind joins one registry, `annotation_kinds`, as it is defined. *Name* is one name written in every case CDD needs: `StoryMap`, `story_map`, and `story-map` are the same *Name*. `class_folder(cls)` is the folder a class is defined in.

- **Purpose:** Hold the annotations an author types, the one place a member's destinations are read, and the one way a name is written in each case, below every publisher, so publishers depend on toolsets and never the other way round.
- **Seam (terms):** Annotation, NamesAnnotation, Destination, DestinationKind, ClassRegistry, Name, `annotation_kinds` (*AnnotationKinds*), `class_folder`, and the annotations an author types `@hosted_only`, `@noCatalog`, `@noDeploy` (their classes, *OmissionAnnotation*, and the other kinds of kind stay behind them)
- **Dependencies (one-way):** *(none)*

## Annotation

The base of every annotation an author types: it records itself, with what it holds, under its `flag` on what it annotates; `annotates(target)` and `recorded_on(target)` read it back, so a destination's `.name` and `.disabled`, a names annotation's `.names`, and a data field's `.key` and `.reference` are read from the annotation, never from attributes beside it. Each kind joins `annotation_kinds` as it is defined.

------
+ flag: str
+ copied: bool
----
+ annotates(target: Any): bool
+ recorded_on(target: Any): Annotation | None
+ written_as(): str
+ installs_member(): bool
+ annotate(target: Any): Any

## NamesAnnotation : Annotation

An annotation that records a tuple of names on what it annotates and reads them back: the fields that name one object (`@identity`) and the arguments a tool takes from its call (*TakesFromCall*) are its kinds, each naming only its flag.

+ NamesAnnotation(*names: str)
------
+ names: tuple[str, ...]
----
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

The base of an annotation that says where install publishes a member: a skill, a command, a rules file, an MCP tool, or a hook. Each destination kind (*Skill*, *Command*, *Rules*, *Mcp*, *Hook*, a *DestinationKind*) is that channel, and is asked as one: `Mcp.publishes(operation)`, `Hook.name_given(operation)`. Its `channel` is only the channel's name, the key a published list and `diagnostics.json` file it under.

------
+ channel: str
+ enlists_member: bool
+ marks_a_collection: bool
	// true for Rules: the member it decorates holds a collection of its toolset's tools
+ answers_calls: bool
	// true for Mcp: its server answers an agent's calls to the member, so a skill or command tells the agent to call the tool
+ name: str | None
	// the name it gives the member there; none for the member's own name
+ disabled: bool
	// true when it is turned off on the member, as `@Hook(..., disabled=True)` is
----
+ publishes(operation: Any): bool
	// it carries this annotation, turned on, and no omission keeps it out of install
+ name_given(operation: Any): str
	// the name the annotation gave the operation, such as a command's name or the event a hook runs on
+ disabled_on(operation: Any): bool
	// the recorded annotation's `disabled`, as `@Hook(..., disabled=True)` holds it

## AnnotationKinds

Every kind of annotation defined in the process, and the destinations among them, in the order they were defined; the process keeps one, `annotation_kinds`. A toolset asks it where a member is published without importing a publisher.

------
+ answering_calls: DestinationKind | None
	// the destination whose server answers an agent's calls, MCP; none when its publisher was never imported
----
+ destinations_of(operation: Any): tuple[DestinationKind, ...]
+ deploy_name_of(operation: Any): str
	// the name a destination's annotation gave operation for the file it installs, such as a command's name; empty when none did
+ marking_a_collection(member: Any): bool
+ enlisting(member: Any): bool
+ withholds_install(operation: Any): bool

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
