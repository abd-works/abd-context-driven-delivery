"""The annotations an author types on a class or member, and where an annotated member is published."""
from __future__ import annotations

from typing import Any, ClassVar

from harness.annotations.name import Name


class AnnotationKinds:
    """Every kind of annotation defined in this process, and the channel each destination publishes to. A kind
    registers here as its class is defined, so the toolset asks one object which annotations a member carries and
    where it is published, without importing the publishers that define the kinds."""

    def __init__(self) -> None:
        self._kinds: list[type[Annotation]] = []
        self._channels: dict[str, type[Destination]] = {}

    def register(self, kind: type[Annotation]) -> None:
        """Add kind, the first kind with its flag; a destination also becomes the kind of its channel."""
        if kind.flag and all(known.flag != kind.flag for known in self._kinds):
            self._kinds.append(kind)
        channel = getattr(kind, "channel", "")
        if channel:
            self._channels.setdefault(channel, kind)

    @property
    def copied_flags(self) -> tuple[str, ...]:
        """Every attribute a wrapper copies from the operation it wraps: each copied kind's flag and the attributes that
        go with it, such as the name a skill annotation gives."""
        flags = [flag for kind in self._kinds if kind.copied for flag in (kind.flag, *kind.companion_flags())]
        return tuple(dict.fromkeys(flags))

    def copy_annotations(self, source: Any, target: Any) -> None:
        """Set on target each copied annotation source carries, so a wrapper installs the way the operation it wraps
        does."""
        for flag in self.copied_flags:
            if hasattr(source, flag):
                setattr(target, flag, getattr(source, flag))

    def withholds_install(self, target: Any) -> bool:
        """True when a kind of omission that keeps members out of install annotates target."""
        return any(
            issubclass(kind, OmissionAnnotation) and kind.omits_install and kind.annotates(target)
            for kind in self._kinds
        )

    def of_channel(self, channel: str) -> type[Destination] | None:
        """The kind of annotation that publishes to channel; none when its publisher was never imported."""
        return self._channels.get(channel)

    def annotated_for(self, channel: str, operation: Any) -> bool:
        """True when operation carries the annotation of channel, whether or not install publishes it."""
        kind = self.of_channel(channel)
        return kind is not None and kind.annotates(operation)

    def publishes(self, channel: str, operation: Any) -> bool:
        """True when install publishes operation to channel: it carries that channel's annotation, the annotation is
        turned on, and no omission keeps it out of install."""
        kind = self.of_channel(channel)
        if kind is None or not kind.annotates(operation) or kind.disabled_on(operation):
            return False
        return not self.withholds_install(operation)

    def name_given_for(self, channel: str, operation: Any) -> str:
        """The name channel's annotation gave operation, such as a command's name or a hook's event; empty when none."""
        kind = self.of_channel(channel)
        return kind.name_annotated_on(operation) if kind is not None else ""

    @property
    def installing_names(self) -> frozenset[str]:
        """The name an author types for each kind that makes a member installable, such as ``skill``, ``mcp`` or
        ``agent_tool``: install reads a repository's source without importing it, and finds a toolset by these names on
        its members. A kind whose publisher this process never imported is not among them."""
        return frozenset(kind.written_as() for kind in self._kinds if kind.installs_member())

    def enlisting(self, member: Any) -> bool:
        """True when a destination that enlists its members, such as a hook, annotates member."""
        return any(kind.enlists_member and kind.annotates(member) for kind in self._channels.values())


# An annotation is a class, and a class is defined once per process, so the list of kinds is one per process too.
annotation_kinds = AnnotationKinds()


class Annotation:
    """Install and discovery find what an author annotated: the operations and classes an annotation decorates. An
    annotation records itself by setting its ``flag`` on what it decorates, and each kind of annotation is a subclass
    that names its flag and reads it with ``annotates``. Every kind registers in ``annotation_kinds`` as it is
    defined, which is the one list of annotations."""

    flag = ""
    # A wrapper of an annotated operation, such as a collected or markdown property, copies the annotations whose kinds
    # say so, so the wrapper installs the way the operation does.
    copied = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        annotation_kinds.register(cls)

    def __new__(cls, target: Any = None):
        annotation = object.__new__(cls)
        if callable(target):
            return annotation.annotate(target)
        return annotation

    @classmethod
    def annotates(cls, target: Any) -> bool:
        """True when this kind of annotation is on target."""
        return bool(getattr(target, cls.flag, False))

    @classmethod
    def written_as(cls) -> str:
        """The name an author types for this kind, such as ``skill`` for *Skill*: its class name in snake case, unless
        the kind names another, as ``agent_tool`` does for *AgentToolAnnotation*."""
        return cls.__dict__.get("typed_name") or Name(cls.__name__).snake

    @classmethod
    def installs_member(cls) -> bool:
        """Whether this kind on a member makes the member installable, so install counts its class as a toolset."""
        return False

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        """The other attributes this kind of annotation sets beside its flag."""
        return ()

    def annotate(self, target: Any) -> Any:
        setattr(target, self.flag, True)
        return target

    def __call__(self, target: Any) -> Any:
        return self.annotate(target)


class OmissionAnnotation(Annotation):
    """An annotation that leaves what it annotates out of something. A classmethod or bound method is annotated
    through the function it wraps, so the annotation is read there too. A kind that sets ``omits_install`` keeps what
    it annotates out of every destination, so a member annotated for MCP or a skill is still not published."""

    copied = False
    omits_install: ClassVar[bool] = False

    @classmethod
    def annotates(cls, target: Any) -> bool:
        """True when target, or the function it wraps, carries this annotation."""
        return super().annotates(target) or super().annotates(getattr(target, "__func__", None))


class HostedOnly(OmissionAnnotation):
    """A class whose tools run only through the practice or toolset that holds it, such as a practice's rules or its
    fidelities: install and the hook server load no toolset of it on its own. Each subclass, such as a practice, is a
    toolset of its own, so the annotation is read on the class it was written on and is not inherited."""

    flag = "_hosted_only"

    @classmethod
    def annotates(cls, target: Any) -> bool:
        """True when target, a class or an instance of one, was itself annotated, not a class it derives from."""
        owner = target if isinstance(target, type) else type(target)
        return bool(vars(owner).get(cls.flag, False))


hosted_only = HostedOnly


class Destination(Annotation):
    """An annotation that names where a member is published: a skill, a command, a rules file, an MCP tool, or a
    hook. Each publisher defines its own kind with the ``channel`` it writes, and the kind registers in
    ``annotation_kinds`` as it is defined, so the toolset that lists a member's destinations asks every channel
    without importing the publishers. A channel whose publisher was never imported annotates nothing."""

    channel: ClassVar[str] = ""
    # True when this annotation alone makes a member a tool of its toolset, as a hook is: the IDE calls the member, so
    # it needs no ``@agent_tool``.
    enlists_member: ClassVar[bool] = False

    def annotate(self, target: Any) -> Any:
        setattr(target, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(target, f"{self.flag}_name", name)
        return target

    @classmethod
    def installs_member(cls) -> bool:
        """A destination with a channel publishes the member it annotates there."""
        return bool(cls.channel)

    @classmethod
    def name_annotated_on(cls, operation: Any) -> str:
        """The name this destination's annotation gave the operation, such as the event a hook runs on; empty when the
        operation carries no such annotation."""
        return str(getattr(operation, f"{cls.flag}_name", "") or "")

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        return (f"{cls.flag}_name",)

    @classmethod
    def disabled_on(cls, operation: Any) -> bool:
        """True when the annotation on operation is there but turned off, as ``@Hook(..., disabled=True)`` is."""
        return False


class Toast(Destination):
    """Annotate an operation or instructions so the IDE shows a toast naming it when an agent calls it. The notifier
    that shows toasts reads this annotation; the operation names no notifier."""

    flag = "_toast"


class NamedDestination(Destination):
    """A destination whose annotation may name what it installs: ``@skill("name")``, ``@skill(name="name")``, or bare
    ``@skill`` for the operation's own name."""

    def __new__(cls, target: Any = None, name: str | None = None):
        annotation = object.__new__(cls)
        if isinstance(target, str):
            annotation.name = target
            return annotation
        annotation.name = name
        if callable(target):
            return annotation.annotate(target)
        return annotation
