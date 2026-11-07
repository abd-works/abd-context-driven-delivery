"""The marks an author types on a class or member, and where a marked member is published."""
from __future__ import annotations

from typing import Any, ClassVar


class MarkKinds:
    """Every kind of mark defined in this process, and the channel each destination publishes to. A kind registers here
    as its class is defined, so the toolset asks one object which marks a member carries and where it is published,
    without importing the publishers that define the kinds."""

    def __init__(self) -> None:
        self._kinds: list[type[Mark]] = []
        self._channels: dict[str, type[Destination]] = {}

    def register(self, kind: type[Mark]) -> None:
        """Add kind, the first kind with its flag; a destination also becomes the kind of its channel."""
        if kind.flag and all(known.flag != kind.flag for known in self._kinds):
            self._kinds.append(kind)
        channel = getattr(kind, "channel", "")
        if channel:
            self._channels.setdefault(channel, kind)

    @property
    def copied_flags(self) -> tuple[str, ...]:
        """Every attribute a wrapper copies from the operation it wraps: each copied kind's flag and the attributes that
        go with it, such as the name a skill mark gives."""
        flags = [flag for kind in self._kinds if kind.copied for flag in (kind.flag, *kind.companion_flags())]
        return tuple(dict.fromkeys(flags))

    def copy_marks(self, source: Any, target: Any) -> None:
        """Set on target each copied mark source carries, so a wrapper installs the way the operation it wraps does."""
        for flag in self.copied_flags:
            if hasattr(source, flag):
                setattr(target, flag, getattr(source, flag))

    def withholds_install(self, target: Any) -> bool:
        """True when a kind of omission that keeps members out of install marks target."""
        return any(
            issubclass(kind, OmissionMark) and kind.omits_install and kind.marks(target) for kind in self._kinds
        )

    def of_channel(self, channel: str) -> type[Destination] | None:
        """The kind of mark that publishes to channel; none when its publisher was never imported."""
        return self._channels.get(channel)

    def marked_for(self, channel: str, operation: Any) -> bool:
        """True when operation carries the mark of channel, whether or not install publishes it."""
        kind = self.of_channel(channel)
        return kind is not None and kind.marks(operation)

    def publishes(self, channel: str, operation: Any) -> bool:
        """True when install publishes operation to channel: it carries that channel's mark, the mark is turned on, and
        no omission keeps it out of install."""
        kind = self.of_channel(channel)
        if kind is None or not kind.marks(operation) or kind.disabled_on(operation):
            return False
        return not self.withholds_install(operation)

    def name_given_for(self, channel: str, operation: Any) -> str:
        """The name channel's mark gave operation, such as a command's name or a hook's event; empty when none."""
        kind = self.of_channel(channel)
        return kind.name_marked_on(operation) if kind is not None else ""

    def enlisting(self, member: Any) -> bool:
        """True when a destination that enlists its members, such as a hook, marks member."""
        return any(kind.enlists_member and kind.marks(member) for kind in self._channels.values())


# A mark is a class, and a class is defined once per process, so the list of kinds is one per process too.
mark_kinds = MarkKinds()


class Mark:
    """Install and discovery find what an author marked: the operations and classes a mark decorates. A mark records
    itself by setting its ``flag`` on what it decorates, and each kind of mark is a subclass that names its flag and
    reads it with ``marks``. Every kind registers in ``mark_kinds`` as it is defined, which is the one list of marks."""

    flag = ""
    # A wrapper of a marked operation, such as a collected or markdown property, copies the marks whose kinds say so,
    # so the wrapper installs the way the operation does.
    copied = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        mark_kinds.register(cls)

    def __new__(cls, target: Any = None):
        mark = object.__new__(cls)
        if callable(target):
            return mark.annotate(target)
        return mark

    @classmethod
    def marks(cls, target: Any) -> bool:
        """True when this kind of mark is on target."""
        return bool(getattr(target, cls.flag, False))

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        """The other attributes this kind of mark sets beside its flag."""
        return ()

    def annotate(self, target: Any) -> Any:
        setattr(target, self.flag, True)
        return target

    def __call__(self, target: Any) -> Any:
        return self.annotate(target)


class OmissionMark(Mark):
    """A mark that leaves what it marks out of something. A classmethod or bound method is marked through the function
    it wraps, so the mark is read there too. A kind that sets ``omits_install`` keeps what it marks out of every
    destination, so a member marked for MCP or a skill is still not published."""

    copied = False
    omits_install: ClassVar[bool] = False

    @classmethod
    def marks(cls, target: Any) -> bool:
        """True when target, or the function it wraps, carries this mark."""
        return super().marks(target) or super().marks(getattr(target, "__func__", None))


class Destination(Mark):
    """A mark that names where a member is published: a skill, a command, a rules file, an MCP tool, or a hook. Each
    publisher defines its own kind with the ``channel`` it writes, and the kind registers in ``mark_kinds`` as it is
    defined, so the toolset that lists a member's destinations asks every channel without importing the publishers. A
    channel whose publisher was never imported marks nothing."""

    channel: ClassVar[str] = ""
    # True when this mark alone makes a member a tool of its toolset, as a hook is: the IDE calls the member, so it
    # needs no ``@agent_tool``.
    enlists_member: ClassVar[bool] = False

    def annotate(self, target: Any) -> Any:
        setattr(target, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(target, f"{self.flag}_name", name)
        return target

    @classmethod
    def name_marked_on(cls, operation: Any) -> str:
        """The name this destination's mark gave the operation, such as the event a hook runs on; empty when the
        operation carries no such mark."""
        return str(getattr(operation, f"{cls.flag}_name", "") or "")

    @classmethod
    def companion_flags(cls) -> tuple[str, ...]:
        return (f"{cls.flag}_name",)

    @classmethod
    def disabled_on(cls, operation: Any) -> bool:
        """True when the mark on operation is there but turned off, as ``@Hook(..., disabled=True)`` is."""
        return False


class Toast(Destination):
    """Mark an operation or instructions so the IDE shows a toast naming it when an agent calls it. The notifier that
    shows toasts reads this mark; the operation names no notifier."""

    flag = "_toast"


class NamedDestination(Destination):
    """A destination whose mark may name what it installs: ``@skill("name")``, ``@skill(name="name")``, or bare
    ``@skill`` for the operation's own name."""

    def __new__(cls, target: Any = None, name: str | None = None):
        mark = object.__new__(cls)
        if isinstance(target, str):
            mark.name = target
            return mark
        mark.name = name
        if callable(target):
            return mark.annotate(target)
        return mark
