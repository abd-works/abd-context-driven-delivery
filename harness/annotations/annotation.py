"""The annotations an author types on a class or member, and where an annotated member is published."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar, TypeAlias

from harness.annotations.name import Name

# What an annotation decorates and install reads back: a function, a method, a property's getter, or a class.
Annotatable: TypeAlias = Callable[..., Any] | type


class AnnotationKinds:
    """Every kind of annotation defined in this process, and the destinations among them: a destination kind is its
    channel. A kind registers here as its class is defined, so the toolset asks one object which annotations a member
    carries and where it is published, without importing the publishers that define the kinds."""

    def __init__(self) -> None:
        self._kinds: list[AnnotationKind] = []
        self._destinations: list[DestinationKind] = []

    def register(self, kind: AnnotationKind) -> None:
        """Add kind, the first kind with its flag; a destination with a channel is also one of the destinations, the
        first kind with its channel."""
        if kind.flag and all(known.flag != kind.flag for known in self._kinds):
            self._kinds.append(kind)
        channel = getattr(kind, "channel", "")
        if channel and all(known.channel != channel for known in self._destinations):
            self._destinations.append(kind)

    @property
    def copied_flags(self) -> tuple[str, ...]:
        """Every attribute a wrapper copies from the operation it wraps: each copied kind's flag, under which the
        annotation recorded itself with what it holds, such as the name a skill annotation gives."""
        return tuple(dict.fromkeys(kind.flag for kind in self._kinds if kind.copied))

    def copy_annotations(self, source: Annotatable, target: Annotatable) -> None:
        """Set on target each copied annotation source carries, so a wrapper installs the way the operation it wraps
        does."""
        for flag in self.copied_flags:
            if hasattr(source, flag):
                setattr(target, flag, getattr(source, flag))

    def withholds_install(self, target: Annotatable) -> bool:
        """True when a kind of omission that keeps members out of install annotates target."""
        return any(
            isinstance(kind, OmissionKind) and kind.omits_install and kind.annotates(target)
            for kind in self._kinds
        )

    def destinations_of(self, operation: Annotatable) -> tuple[DestinationKind, ...]:
        """Every destination install publishes operation to, in the order the destinations were defined. A destination
        whose publisher this process never imported publishes nothing."""
        return tuple(kind for kind in self._destinations if kind.publishes(operation))

    def deploy_name_of(self, operation: Annotatable) -> str:
        """The name a destination's annotation gave operation for the file it installs, such as a command's name; empty
        when none did. A destination that enlists its member names something else, such as the event a hook runs on."""
        return next((name for kind in self._destinations if not kind.enlists_member and (name := kind.name_given(operation))), "")

    @property
    def answering_calls(self) -> DestinationKind | None:
        """The destination whose server answers an agent's calls to the members it publishes, as MCP does; none when
        its publisher was never imported."""
        return next((kind for kind in self._destinations if kind.answers_calls), None)

    @property
    def installing_names(self) -> frozenset[str]:
        """The name an author types for each kind that makes a member installable, such as ``skill``, ``mcp`` or
        ``agent_tool``: install reads a repository's source without importing it, and finds a toolset by these names on
        its members. A kind whose publisher this process never imported is not among them."""
        return frozenset(kind.written_as() for kind in self._kinds if kind.installs_member())

    def enlisting(self, member: Annotatable) -> bool:
        """True when a destination that enlists its members, such as a hook, annotates member."""
        return any(kind.enlists_member and kind.annotates(member) for kind in self._destinations)

    def marking_a_collection(self, member: Annotatable) -> bool:
        """True when a destination whose member holds a collection of its toolset's tools, as a practice's ``@rules``
        member does, annotates member."""
        return any(kind.marks_a_collection and kind.annotates(member) for kind in self._destinations)


# An annotation is a class, and a class is defined once per process, so the list of kinds is one per process too.
annotation_kinds = AnnotationKinds()


class AnnotationKind(type):
    """A kind of annotation, such as *Skill* or *NoCatalog*: the class an author types as ``@skill`` or ``@noCatalog``
    is the one instance of its kind, so install and discovery ask the kind itself whether it is on a member and how it
    publishes one (``Skill.annotates(member)``). Each kind joins ``annotation_kinds`` as it is defined. A family of
    kinds that answers these in a way of its own names its own kind of kind, as *Destination* does."""

    flag: str
    copied: bool
    makes_installable: bool

    def __init__(kind, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(name, bases, namespace, **kwargs)
        annotation_kinds.register(kind)

    def annotates(kind, target: Annotatable) -> bool:
        """True when this kind of annotation is on target."""
        return bool(getattr(target, kind.flag, False))

    def recorded_on(kind, target: Annotatable) -> Any:
        """The annotation of this kind on target, which recorded itself there with what it holds, such as the name a
        ``@skill`` gives or ``@on_stage``'s place among a stage's actions; none when target carries none."""
        return getattr(target, kind.flag, None)

    def written_as(kind) -> str:
        """The name an author types for this kind, such as ``skill`` for *Skill*: its class name in snake case, unless
        the kind names another, as ``agent_tool`` does for *AgentToolAnnotation*."""
        return kind.__dict__.get("typed_name") or Name(kind.__name__).snake

    def installs_member(kind) -> bool:
        """Whether this kind on a member makes the member installable, so install counts its class as a toolset."""
        return kind.makes_installable


class Annotation(metaclass=AnnotationKind):
    """Install and discovery find what an author annotated: the operations and classes an annotation decorates. An
    annotation records itself, with what it holds, under its ``flag`` on what it decorates, and each kind of annotation
    is a subclass that names its flag; its kind (*AnnotationKind*) reads it back with ``annotates`` and
    ``recorded_on``. Every kind registers in ``annotation_kinds`` as it is defined, which is the one list of
    annotations."""

    flag = ""
    # A wrapper of an annotated operation, such as a collected or markdown property, copies the annotations whose kinds
    # say so, so the wrapper installs the way the operation does.
    copied = True
    # Whether this kind on a member makes the member installable, so install counts its class as a toolset.
    makes_installable: ClassVar[bool] = False

    def __new__(cls, target: Annotatable | None = None):
        annotation = object.__new__(cls)
        if callable(target):
            return annotation.annotate(target)
        return annotation

    def annotate(self, target: Annotatable) -> Annotatable:
        setattr(target, self.flag, self)
        return target

    def __call__(self, target: Annotatable) -> Annotatable:
        return self.annotate(target)


class NamesKind(AnnotationKind):
    """A kind of annotation that records a tuple of names on what it annotates and reads them back."""

    def names_on(kind, target: Annotatable) -> tuple[str, ...]:
        """The names this kind of annotation recorded on target; none when it carries none."""
        recorded = kind.recorded_on(target)
        return tuple(recorded.names) if recorded is not None else ()


class NamesAnnotation(Annotation, metaclass=NamesKind):
    """An annotation that records a tuple of names on what it annotates, such as the fields that name one object of a
    class or the arguments a tool takes from its call. Each kind names its flag; its kind reads the names back
    (``names_on``), and nothing is recorded on what no such annotation decorates."""

    copied = False

    def __new__(cls, *names: str):
        return object.__new__(cls)

    def __init__(self, *names: str) -> None:
        self.names = names


class OmissionKind(AnnotationKind):
    """A kind of annotation that leaves what it annotates out of something. A classmethod or bound method is annotated
    through the function it wraps, so the annotation is read there too."""

    def annotates(kind, target: Annotatable) -> bool:
        """True when target, or the function it wraps, carries this annotation."""
        return super().annotates(target) or super().annotates(getattr(target, "__func__", None))


class OmissionAnnotation(Annotation, metaclass=OmissionKind):
    """An annotation that leaves what it annotates out of something. A kind that sets ``omits_install`` keeps what it
    annotates out of every destination, so a member annotated for MCP or a skill is still not published."""

    copied = False
    omits_install: ClassVar[bool] = False


class HostedOnlyKind(OmissionKind):
    """The kind of ``@hosted_only``, which is read on the class it was written on and is not inherited."""

    def annotates(kind, target: Annotatable) -> bool:
        """True when target, a class or an instance of one, was itself annotated, not a class it derives from."""
        owner = target if isinstance(target, type) else type(target)
        return bool(vars(owner).get(kind.flag, False))


class HostedOnly(OmissionAnnotation, metaclass=HostedOnlyKind):
    """A class whose tools run only through the practice or toolset that holds it, such as a practice's rules or its
    fidelities: install and the hook server load no toolset of it on its own. Each subclass, such as a practice, is a
    toolset of its own, so the annotation is read on the class it was written on and is not inherited."""

    flag = "_hosted_only"


hosted_only = HostedOnly


class NoCatalog(OmissionAnnotation):
    """Omit this class or operation from the catalog.

    Install and deploy ignore this annotation. Use it when the behavior is real
    but not ready to show in the catalog.
    """

    flag = "_no_catalog"


class NoDeploy(OmissionAnnotation):
    """Omit this operation from install.

    Skill, command, MCP, and hook annotations on the same operation do not write
    files. The catalog can still list it.
    """

    flag = "_no_deploy"
    omits_install = True


noCatalog = NoCatalog
noDeploy = NoDeploy


class DestinationKind(AnnotationKind):
    """A kind of annotation that names where a member is published, and is that channel: *Skill*, *Command*, *Rules*,
    *Mcp*, and *Hook*. It answers whether install publishes a member there, the name the annotation gave the member
    there, and whether the annotation is turned off on it. Its ``channel`` is the channel's name, the key a published
    list and ``diagnostics.json`` file it under."""

    channel: str

    def installs_member(kind) -> bool:
        """A destination with a channel publishes the member it annotates there."""
        return bool(kind.channel)

    def publishes(kind, operation: Annotatable) -> bool:
        """True when install publishes operation here: it carries this annotation, the annotation is turned on, and no
        omission keeps it out of install."""
        if not kind.channel or not kind.annotates(operation) or kind.disabled_on(operation):
            return False
        return not annotation_kinds.withholds_install(operation)

    def name_given(kind, operation: Annotatable) -> str:
        """The name this destination's annotation gave the operation, such as a command's name or the event a hook runs
        on; empty when the operation carries no such annotation."""
        recorded = kind.recorded_on(operation)
        return str(recorded.name or "") if recorded is not None else ""

    def disabled_on(kind, operation: Annotatable) -> bool:
        """True when the annotation on operation is there but turned off, as ``@Hook(..., disabled=True)`` is."""
        recorded = kind.recorded_on(operation)
        return recorded is not None and recorded.disabled


class Destination(Annotation, metaclass=DestinationKind):
    """An annotation that names where a member is published: a skill, a command, a rules file, an MCP tool, or a
    hook. Each publisher defines its own kind with the ``channel`` it writes, and the kind registers in
    ``annotation_kinds`` as it is defined, so the toolset that lists a member's destinations asks every channel
    without importing the publishers. A channel whose publisher was never imported annotates nothing. An annotation
    that holds a ``name`` gives the member that name there, and one that holds ``disabled`` set turns itself off on
    the member, as ``@Hook(..., disabled=True)`` does."""

    channel: ClassVar[str] = ""
    # True when this annotation alone makes a member a tool of its toolset, as a hook is: the IDE calls the member, so
    # it needs no ``@agent_tool``.
    enlists_member: ClassVar[bool] = False
    # True when the member this annotation decorates holds a collection of its toolset's tools, as ``@rules`` does.
    marks_a_collection: ClassVar[bool] = False
    # True when this destination's server answers an agent's calls to the member, as MCP does, so a skill or command
    # for the member tells the agent to call the tool, and each call is logged in the caller's session.
    answers_calls: ClassVar[bool] = False
    # The name the annotation gives the member there, such as a command's name or a hook's event; none for the member's
    # own name.
    name: str | None = None
    # Whether the annotation is turned off on the member, as ``@Hook(..., disabled=True)`` is.
    disabled: bool = False
