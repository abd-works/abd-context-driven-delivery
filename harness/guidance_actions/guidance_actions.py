"""First-order guidance-action prelude: an action made for its call's session runs an operation on the guidance the call
names."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Mapping, NotRequired, Sequence, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import ToolsetReference
from harness.annotations.annotation import annotation_kinds
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.action_catalogue import ACTION_CATALOGUE, Action
from harness.guidance.documents import document_in
from harness.guidance.guidance import FidelityGuidance, Guidance, PracticeGuidance
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE, PracticeSet
from harness.guidance.worked_session import WorkedSession
from harness.guidance_actions.generated_patterns import GeneratedPatterns
from harness.hooks.hook_server import rules_toast
from harness.hooks.hooks import Toast, hook

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload


class GuidanceRef(TypedDict):
    """One Guidance: a toolset ref, plus the fidelity or context that ref accepts."""

    toolset: str
    fidelity: NotRequired[str]
    context: NotRequired[dict[str, Any]]


# One Guidance a call sends: a slug or ``module:Class`` ref, a ``{toolset, …}`` mapping, or Guidance already made, such
# as a practice a spec makes.
GuidanceEntry = str | GuidanceRef | Guidance
# Guidance list, one Guidance, or a string to act on directly.
GuidanceArg = GuidanceEntry | list[GuidanceEntry]
# One Guidance an action lists: a practice of its set, or a toolset made from a ref that names none of them.
ListedGuidance = Guidance | AgentToolSet
# What an action hands each operation: a listed Guidance at the fidelity the action works at on it, or the text the
# action runs once on.
WorkedGuidance = ListedGuidance | str


GUIDANCE_PARAMETER = (
    "guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. "
    "A list runs this action once per slug. A module:Class ref is that slug after lookup. "
    "Any other string is text this action runs once."
)
_TOOLSET_REF = re.compile(r"^[A-Za-z_][\w.]*:[A-Za-z_]\w*$")
_GUIDANCE_SLUG = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
# One word written the way a slug or a name is, in any case, with hyphens or underscores: sent alone it is meant as a
# slug, never as prose.
_SLUG_SHAPED = re.compile(r"^[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*$")
# The formats a command writes its fidelities in, as the session board names them: `format=drawio,markdown`.
_FORMAT_WORD = "format="
# The session a command is for, as the session board names it: `session=.sessions/<name>/session.json`.
_SESSION_WORD = "session="
# The pattern overlays a command runs with, as the chat bar names them: `overlays=lern_domain_driven,mern_domain_driven`.
_OVERLAYS_WORD = "overlays="
# What an action works on before it names any guidance; None cannot stand for it, since naming None keeps what it had.
_NOTHING_WORKED_ON = object()


@dataclass(frozen=True)
class GuidanceCommand:
    """The guidance a call sends, read once where the call arrives: the Guidance it names (``guidance``), and the words a
    board or chat-bar command adds to it, which are chat text a person reads and an agent sends on as the guidance
    argument: the session it is for (``session=``), the pattern overlays it runs with (``overlays=``), and the formats it
    writes in (``format=``). The action holds this object from then on, so nothing below the call reads the text again
    (``cdr/0001-the-session-word-is-read-at-the-call.md``)."""

    written: GuidanceArg
    """The guidance as the call sent it, which the action runs once on when it names no Guidance."""
    guidance: GuidanceArg
    """The guidance with the command's words taken out."""
    session_file: str = ""
    """The session.json the command is for; empty when it names none, so the call works in its chat's session."""
    overlays: tuple[str, ...] | None = None
    """The patterns the command runs with; none when it names none, so the session keeps the overlays it has. A word
    with nothing after it names no overlay, and clears them."""
    formats: tuple[str, ...] = ()
    """The formats the command writes its fidelities in, each fidelity in those it writes."""

    @classmethod
    def from_guidance(cls, written: GuidanceArg) -> GuidanceCommand:
        """The command guidance is: a string's command words read out of it; any other guidance as it is."""
        if not isinstance(written, str):
            return cls(written, written)
        words = written.split()
        named = {prefix: next((word[len(prefix):] for word in words if word.startswith(prefix)), None) for prefix in (_SESSION_WORD, _OVERLAYS_WORD, _FORMAT_WORD)}
        rest = [word for word in words if not word.startswith((_SESSION_WORD, _OVERLAYS_WORD, _FORMAT_WORD))]
        overlays = named[_OVERLAYS_WORD]
        return cls(
            written,
            " ".join(rest) if len(rest) < len(words) else written,
            named[_SESSION_WORD] or "",
            None if overlays is None else tuple(name for name in overlays.split(",") if name),
            tuple(name for name in (named[_FORMAT_WORD] or "").split(",") if name),
        )


@dataclass(frozen=True)
class NamedGuidance:
    """One Guidance a call names, as the object the action works on: a practice of the action's set, or one of that
    practice's fidelities, with the format the call names for it; empty when it names none."""

    guidance: PracticeGuidance | FidelityGuidance
    format: str = ""

    @property
    def practice(self) -> PracticeGuidance:
        named = self.guidance
        return named.practice_guidance if isinstance(named, FidelityGuidance) else named


# One Guidance a guidance argument names: a practice or fidelity of the action's set, read into a *NamedGuidance*; any
# other Guidance as it was sent.
ArgumentEntry = NamedGuidance | GuidanceEntry


class UnknownGuidance(ValueError):
    """A listed guidance word that no practice or fidelity of the action's set has as its slug, such as
    ``clean_engineering`` for ``clean-engineering``. The message lists the slugs there are, so the caller can send one."""

    def __init__(self, word: str, slugs: Sequence[str]) -> None:
        super().__init__(f"no practice or fidelity has the slug {word!r}; the slugs are {', '.join(slugs)}")
        self.word = word
        self.slugs = tuple(slugs)


class GuidanceMappingUnreadable(ValueError):
    """A guidance argument written as a ``{toolset, fidelity, format}`` mapping, between braces, that is not JSON. Read
    as a slug instead, it would be refused as a practice nobody has, which hides the typo; the message names the text
    and where it stops being JSON."""

    def __init__(self, text: str, error: json.JSONDecodeError) -> None:
        super().__init__(f"the guidance mapping {text} is not JSON: {error.msg} at character {error.pos}")
        self.text = text


class GuidanceMappingNamesNoToolset(ValueError):
    """A guidance mapping with no ``toolset``, which is where a mapping names its practice. The message says what a
    toolset holds and lists the slugs there are."""

    def __init__(self, mapping: Mapping[str, Any], slugs: Sequence[str]) -> None:
        super().__init__(
            f"the guidance mapping {dict(mapping)!r} names no toolset; a mapping names its practice in toolset, as a slug "
            f"or a module:Class ref; the slugs are {', '.join(slugs)}"
        )
        self.mapping = dict(mapping)
        self.slugs = tuple(slugs)


class GuidanceTurnedOff(ValueError):
    """A guidance word names a practice CDD ships, or one of its fidelities, that is turned off for the session the
    action works in: the session's practices leave it out."""


class GuidanceArgument:
    """The guidance a command names, read as what the action works on. It is the Guidance list, one Guidance (a slug, a
    ``module:Class`` ref, a ``{"toolset": ...}`` mapping or its JSON, or a Guidance already made), or text the action
    runs once on. Agents on MCP often send several slugs in one string; each is Guidance, written in each of the formats
    the command names that it writes. A string with any other word is text, so prose still runs once; one word sent
    alone that is shaped like a slug and names nothing is a misspelt slug, refused as *UnknownGuidance*, since run as
    text it would generate with no rules and render or check nothing.

    A slug or a ref names a practice or a fidelity of the practices the action works with (``practices``), and is read
    once into that object, so the action never looks it up again."""

    def __init__(self, command: GuidanceCommand, practices: Callable[[], PracticeSet], session_name: str = "") -> None:
        self._command = command
        self._guidance = command.guidance
        self._practices = practices
        # The session whose practices these are; empty for a set that is every practice CDD ships.
        self._session_name = session_name

    @property
    def text(self) -> str | None:
        """The text the action runs once on, as the call wrote it; none when the argument names Guidance."""
        if not isinstance(self._guidance, str) or self._one_item() is not None or self._slug_words():
            return None
        self._refuse_misspelt_slug()
        return self._command.written

    def _refuse_misspelt_slug(self) -> None:
        """Refuse a guidance string that is one word, or words joined by commas, each shaped like a slug, when one of
        them names no practice or fidelity: it was meant as a slug, as the same word in a list is."""
        words = self._guidance.split()
        if len(words) != 1:
            return
        parts = [part for part in words[0].split(",") if part]
        if not all(_SLUG_SHAPED.match(part) for part in parts):
            return
        unknown = next((part for part in parts if self._named(part) is None), None)
        if unknown is not None:
            raise UnknownGuidance(unknown, self.slugs)

    @property
    def items(self) -> list[ArgumentEntry]:
        """Each Guidance the argument names: a *NamedGuidance* for a practice of the action's set or one of its
        fidelities, once for each format the command names that it writes; any other Guidance as the ref, ref mapping,
        or object it was sent as."""
        return [written for entry in self._entries() for written in self._in_formats(entry)]

    def _entries(self) -> list[ArgumentEntry]:
        one = self._one_item() if not isinstance(self._guidance, list) else None
        if one is not None:
            return [one]
        if isinstance(self._guidance, str):
            return self._slug_words()
        return [self._listed(entry) for entry in list(self._guidance or [])]

    def _in_formats(self, entry: ArgumentEntry) -> list[ArgumentEntry]:
        """entry once for each format the command names that it writes; entry itself when the command names none or
        entry names its own."""
        if not isinstance(entry, NamedGuidance) or entry.format or not self._command.formats:
            return [entry]
        return [NamedGuidance(entry.guidance, format) for format in self._listed_formats_of(entry.guidance, list(self._command.formats))]

    def _listed(self, entry: GuidanceEntry) -> ArgumentEntry:
        """One entry of a Guidance list: the Guidance it names. A word in a list is a slug, so a word that names no
        practice or fidelity raises *UnknownGuidance* rather than being made as a ``module:Class`` ref."""
        named = self._item(entry)
        if named is None and isinstance(entry, str):
            raise UnknownGuidance(entry, self.slugs)
        return entry if named is None else named

    @property
    def slugs(self) -> list[str]:
        """Every slug a call can name: each practice's, then each of its fidelities'."""
        return self._practices().slugs

    def _one_item(self) -> ArgumentEntry | None:
        return self._item(self._guidance)

    def _slug_words(self) -> list[NamedGuidance]:
        slugs = [slug for word in self._guidance.split() for slug in word.split(",") if slug]
        named = [self._named(slug) for slug in slugs]
        if not named or None in named:
            return []
        return [NamedGuidance(guidance) for guidance in named]

    def _listed_formats_of(self, guidance: PracticeGuidance | FidelityGuidance, listed: list[str]) -> list[str]:
        """The listed formats the guidance writes, the action running once for each: a stage Run lists the formats of
        every fidelity it acts on, and each fidelity takes its own, a diagram both drawio and whiteboard. A practice, or
        a fidelity that writes none of them, takes the first."""
        outputs = guidance.outputs if isinstance(guidance, FidelityGuidance) else {}
        written = [name for name in listed if name in outputs]
        return written or (listed or [""])[:1]

    def _item(self, entry: GuidanceEntry) -> ArgumentEntry | None:
        """One Guidance as entry names it; none for a string that names none."""
        if not isinstance(entry, str):
            return self._mapped(entry) if isinstance(entry, dict) else entry
        text = entry.strip()
        mapping = self._json_ref(text)
        if mapping is not None:
            return self._mapped(mapping)
        if _TOOLSET_REF.match(text):
            return self._mapped({"toolset": text})
        named = self._named(text)
        return NamedGuidance(named) if named is not None else None

    def _mapped(self, mapping: GuidanceRef) -> ArgumentEntry:
        """A ``{toolset, fidelity, format}`` mapping as the practice of the action's set its toolset names, at its
        fidelity; a mapping with constructor arguments of its own, or one whose toolset is no practice of the set, as it
        was sent, for the action to make. A toolset may also be a slug, which names its practice or fidelity as the
        slug alone does; one that is neither raises *UnknownGuidance*, and a mapping with none raises
        *GuidanceMappingNamesNoToolset*."""
        toolset = str(mapping.get("toolset") or "")
        if not toolset:
            raise GuidanceMappingNamesNoToolset(mapping, self.slugs)
        named = self._toolset_named(toolset, bool(mapping.get("context")))
        if named is None:
            return mapping if len(mapping) > 1 else mapping.get("toolset")
        fidelity = str(mapping.get("fidelity") or "")
        practice = named.practice_guidance if isinstance(named, FidelityGuidance) else named
        return NamedGuidance(practice.fidelities[fidelity] if fidelity else named, str(mapping.get("format") or ""))

    def _toolset_named(self, toolset: str, makes_its_own: bool) -> PracticeGuidance | FidelityGuidance | None:
        """The practice or fidelity of the action's set a mapping's toolset names, by ``module:Class`` ref or by slug;
        none for a ref to a class that is no practice of the set, or one the mapping gives constructor arguments
        (makes_its_own), which the action makes. A toolset that is neither a ref nor a slug raises *UnknownGuidance*."""
        if _TOOLSET_REF.match(toolset):
            return None if makes_its_own else self._practice_of_class(toolset)
        named = self._named(toolset)
        if named is None:
            raise UnknownGuidance(toolset, self.slugs)
        return named

    def _practice_of_class(self, reference: str) -> PracticeGuidance | None:
        toolset_class = ToolsetReference.parsed(reference).toolset_class
        return next((practice for practice in self._practices() if type(practice) is toolset_class), None)

    def _named(self, slug: str) -> PracticeGuidance | FidelityGuidance | None:
        """The practice or fidelity slug names among the action's practices (``PracticeSet.named``); none for a word
        that is no slug."""
        if not _GUIDANCE_SLUG.match(slug):
            return None
        named = self._practices().named(slug)
        if named is None and self._session_name:
            self._refuse_turned_off(slug)
        return named

    def _refuse_turned_off(self, slug: str) -> None:
        """A slug of a practice CDD ships that the session's practices leave out names a practice turned off for the
        session; run as text, it would check or render nothing, so it is refused, naming the practice to turn on."""
        catalogue = PRACTICE_CATALOGUE.create_all()
        practice = catalogue.practice_answering(slug)
        if practice is None:
            return
        kind = "the practice" if practice.slug == slug else "a fidelity of"
        raise GuidanceTurnedOff(f"{slug} is {kind} {practice.slug}, which is turned off for session {self._session_name}; turn {practice.slug} on for the session to work on it")

    def _json_ref(self, text: str) -> GuidanceRef | None:
        if not (text.startswith("{") and text.endswith("}")):
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as unreadable:
            raise GuidanceMappingUnreadable(text, unreadable) from unreadable
        return parsed if isinstance(parsed, dict) and parsed.get("toolset") else None


class WorkList:
    """What one guidance action works on: the guidance its call named, read once into its text or into the practices of
    the action's set, and the fidelity the action works at on each practice it lists. The action holds one. The
    fidelity is held here, never on the practice, which every call in a session shares, so a later call on another
    fidelity of the same practice changes nothing this one reads. A list made inside another action's (``outer``) asks
    that list for the practices it works with and the fidelity it works at on a practice it names no fidelity of."""

    def __init__(self, session: WorkedSession | None, outer: WorkList | None = None) -> None:
        self._session = session
        self._outer = outer
        # The guidance argument taken, so naming the same argument again keeps what it built.
        self.worked_on: Any = _NOTHING_WORKED_ON
        self.text: str | None = None
        self._items: list[ArgumentEntry] = []
        self._listed: list[ListedGuidance] | None = None
        self._practices: PracticeSet | None = None
        self._worked_at: dict[PracticeGuidance, FidelityGuidance | None] = {}
        # Each listed entry's format and the fidelity (or practice) that writes it, by the entry's place in the list:
        # a fidelity listed once per format, such as a diagram in drawio and in whiteboard, is worked in each in turn.
        self._formats: list[tuple[Guidance | None, str]] = []

    @property
    def is_inside(self) -> bool:
        """Whether this list was made inside another action's: the action that holds it was started by another."""
        return self._outer is not None

    def take(self, command: GuidanceCommand) -> None:
        """Work on the guidance command names, read once into the practices and fidelities of the action's set. The
        overlays the command names are chosen on the session first, so the action runs with them."""
        if command.overlays is not None and self._session is not None:
            self._session.choose_overlays(list(command.overlays))
        argument = GuidanceArgument(command, self.practice_set, self._session_name)
        self.worked_on = command.written
        self._listed = None
        self.text = argument.text
        self._items = argument.items if self.text is None else []

    def _take_listed(self, worked_on: str | list[ListedGuidance]) -> None:
        """Work on what another action already took: its text, or the Guidance it listed, as the same objects. A
        fidelity ``each`` handed it is its practice, worked at that fidelity."""
        self.worked_on = worked_on
        if isinstance(worked_on, str):
            self.text, self._items, self._listed = worked_on, [], None
            return
        listed = [self._held(guidance) for guidance in worked_on]
        self.text, self._items, self._listed = None, list(listed), list(listed)

    def take_fidelity(self, fidelity: FidelityGuidance, format: str = "") -> None:
        """Work on fidelity: its practice is the one Guidance listed, worked at that fidelity, in format when one is
        named, which the fidelity keeps."""
        practice = fidelity.practice_guidance
        if format:
            fidelity.format = format
        self.worked_on = fidelity
        self.text, self._items, self._listed = None, [practice], [practice]
        self._worked_at[practice] = fidelity

    def listed(self) -> list[ListedGuidance]:
        """The Guidance worked on. A practice CDD has is the session's own instance of it, the one the session's graph
        holds, worked at the fidelity the guidance names (``fidelity_of``), else the fidelity the practice was made at;
        the practice itself stays where it was made. A format the guidance names is the one that fidelity keeps; any
        other guidance is made from its ref."""
        if self.text is not None:
            return []
        if self._listed is None:
            self._formats = []
            self._listed = [self._worked_on(named) for named in self._items]
        return self._listed

    def _entry(self, index: int) -> ListedGuidance:
        """The listed entry at index, its fidelity set to the format that entry names, so a fidelity listed once per
        format works in each format in turn."""
        listed = self.listed()[index]
        writer, format = self._formats[index] if index < len(self._formats) else (None, "")
        if writer is not None and format and writer.format != format:
            writer.format = format
        return listed

    @property
    def _session_name(self) -> str:
        """The name of the session whose practices the list works with; empty when it works with every practice."""
        if self._outer is not None:
            return self._outer._session_name
        return getattr(self._session, "name", "") if self._session is not None else ""

    def practice_set(self) -> PracticeSet:
        """The practices worked with, made known once: the session's own instances, the ones its graph holds; for no
        session, a set of their own; for a list made inside another action's, that list's."""
        if self._outer is not None:
            return self._outer.practice_set()
        if self._practices is None:
            session = self._session
            self._practices = (
                PracticeSet(output.guidance for output in session.practices.values()) if session is not None else PRACTICE_CATALOGUE.create_all()
            )
        return self._practices

    def practice_of(self, guidance: WorkedGuidance) -> WorkedGuidance:
        """The practice guidance belongs to: a fidelity's practice; guidance itself for a practice, other guidance, or
        text."""
        if isinstance(guidance, FidelityGuidance) and guidance.practice_guidance is not None:
            return guidance.practice_guidance
        return guidance

    def fidelity_of(self, guidance: WorkedGuidance) -> FidelityGuidance | None:
        """The fidelity worked at on guidance, one of the Guidance listed: the one its call named, read when it was
        listed; its current fidelity for guidance no session holds; a fidelity ``each`` handed out is itself, and none
        for text. A list made inside another action's works at the fidelity that one works at, unless it was handed a
        fidelity of its own."""
        if isinstance(guidance, FidelityGuidance):
            return guidance
        if isinstance(guidance, PracticeGuidance) and guidance in self._worked_at:
            return self._worked_at[guidance]
        if self._outer is not None:
            return self._outer.fidelity_of(guidance)
        return getattr(getattr(guidance, "fidelities", None), "current", None)

    def at_fidelity(self, guidance: ListedGuidance) -> ListedGuidance:
        """guidance, one of the Guidance this list holds, as the fidelity the action works at on it; guidance itself when
        it has none."""
        fidelity = self.fidelity_of(guidance)
        return fidelity if fidelity is not None else guidance

    def each(self, operation: Callable[[WorkedGuidance], Any]) -> list[Any]:
        """Run ``operation`` once on a guidance string, or once per Guidance. A listed practice is handed over as the
        fidelity the action works at on it, which answers its own instructions, templates, examples, rules and
        generate_output, so another call that moves the practice to another fidelity never changes this one's text;
        Guidance with no fidelity is handed over itself. A recipe reads only what the operation returns, so an
        operation gives its text back rather than reading it into nothing."""
        if self.text is not None:
            return [operation(self.text)]
        return [operation(self.at_fidelity(self._entry(index))) for index in range(len(self.listed()))]

    @property
    def rules_to_follow(self) -> str:
        """The rules each listed guidance holds the agent to, read from the fidelity the action works at on it: its
        shared rules and that fidelity's, or the guidance text itself. It checks nothing, so it saves no report and logs
        no validate line, which would tell the session board the work had been checked."""
        rules = (worked if isinstance(worked, str) else worked.checked_rules_text() for worked in self.each(lambda worked: worked))
        return "\n\n".join(part for part in rules if part)

    def _held(self, sent: GuidanceEntry | ListedGuidance) -> GuidanceEntry | ListedGuidance:
        """sent as it is listed: a fidelity is its practice, worked at that fidelity; any other Guidance is itself."""
        practice = self.practice_of(sent)
        if practice is not sent:
            self._worked_at[practice] = sent
        return practice

    def _made(self, entry: GuidanceEntry | ListedGuidance) -> ListedGuidance:
        """The toolset entry names, made: a ``module:Class`` reference or a ``{toolset, …}`` mapping, as a call sends
        it, is parsed and made with its context; Guidance already made is itself."""
        if isinstance(entry, str):
            return ToolsetReference.parsed(entry).made()
        if isinstance(entry, dict):
            context = {**{key: value for key, value in entry.items() if key not in ("toolset", "context")}, **dict(entry.get("context") or {})}
            return ToolsetReference.parsed(entry["toolset"]).made(**context)
        return entry

    def _worked_on(self, named_entry: ArgumentEntry) -> ListedGuidance:
        """What named_entry names: a practice of the set, worked at the fidelity and in the format it names; or guidance
        made from it when it names none of them."""
        named = named_entry if isinstance(named_entry, NamedGuidance) else self._own_counterpart(named_entry)
        if named is None:
            self._formats.append((None, ""))
            return self._made(self._held(named_entry))
        practice = named.practice
        fidelity = named.guidance if named.guidance is not practice else practice.fidelities.current
        writer = fidelity if fidelity is not None else practice
        if named.format:
            # The fidelity chooses the format it is given in its session, so the next action on it works in it without
            # being told: the chosen formats are the session's choice, which every chat and page of the session reads.
            writer.format = named.format
        self._formats.append((writer, named.format))
        if self._session is not None:
            self._session.practice(practice.key)
        self._worked_at[practice] = fidelity
        return practice

    def _own_counterpart(self, made: GuidanceEntry) -> NamedGuidance | None:
        """A practice or fidelity made outside the session, such as one a spec makes, as the session's own instance of
        it, at the same fidelity and format; none for no session, which works on what it is handed, and for anything
        that is no practice of the session's set."""
        if self._session is None or not isinstance(made, (PracticeGuidance, FidelityGuidance)):
            return None
        practice = self.practice_of(made)
        own = next((candidate for candidate in self.practice_set() if type(candidate) is type(practice)), None)
        if own is None:
            return None
        fidelity = made if isinstance(made, FidelityGuidance) else practice.fidelities.current
        format = fidelity.format if fidelity is not None else practice.format
        return NamedGuidance(own.fidelities[fidelity.name] if fidelity is not None else own, format)


@dataclass
class GuidanceAgentOperation(AgentOperation):
    """An ``@agent_tool`` on a guidance action: its call is logged as the action, such as ``render``, rather than as a
    ``tool …`` line."""

    def log_session_invocation(self, call: ToolCall) -> None:
        """Log the call as its action, in the session the action made for it works in."""
        if not self.should_log_session_invocation(call.arguments):
            return
        self.toolset.log_running(self.name)


class ActionWorksInNoSession(Exception):
    """An action made for no session, such as one listed for install, was asked for the session it works in."""

    def __init__(self, action: str) -> None:
        super().__init__(f"{action} was made for no session; make it for the session its call works in")
        self.action = action


def source_label(content: str = "", paths: list[str] | str | None = None) -> str:
    """What an instruction names as its source: the paths a call names, one per line, else its in-process text. The file
    bodies stay on disk."""
    if paths in ("", None, []):
        return content or ""
    return paths if isinstance(paths, str) else "\n".join(str(entry) for entry in paths)


class ActionFiles:
    """The files one guidance action names and writes in the session it works in: a path a call names, read from the
    session's project; the document a call names, read from there; and the files the action just wrote, which the
    session's graph is refreshed with. The action holds one (``action.files``), made with it."""

    def __init__(self, action: GuidanceAction) -> None:
        self._action = action

    def path_named(self, named: str | Path) -> Path:
        """named as a path in the action's session's project; an absolute path stays where it is, in no session too."""
        path = Path(named)
        return path.resolve() if path.is_absolute() else self._action.session.paths.path_named(path)

    def paths_to_read(self, named: list[str] | str | None) -> list[Path]:
        """Each path a call names to read, as a path in the action's session's project, which must be there under one of
        the session's roots: the session's files refuse one that is not, by name, as validate's paths are refused, so an
        action never reads nothing or writes outside the project and answers as if all were well. An action made for no
        session, such as one run in process, takes each path as given."""
        entries = [named] if isinstance(named, (str, Path)) else list(named or [])
        session = self._action.works_in
        if session is None:
            return [self.path_named(entry) for entry in entries]
        return [session.work_root / session.session_files.from_root(entry) for entry in entries]

    def read(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """The document a call names: content, or the files at paths read from the action's session's project; an action
        made for no session, such as one run in process, reads paths as given."""
        return document_in(self._action.works_in, content, paths)

    def wrote(self, paths: list[str | Path]) -> None:
        """Refresh the session's graph with exactly the files the action just wrote, so the graph holds them as they are
        now; nothing watches the files. An action made for no session holds no graph to refresh."""
        if self._action.works_in is not None:
            self._action.graph.refresh([str(path) for path in paths], self._action.call)


# Where a pattern a report holds the work to came from: the folder's patterns file, which generate wrote, or the session's
# own overlays. A report that names the wrong one sends the reader looking in the wrong place.
_RECORDED_IN_PATTERNS_FILE = "This content was generated with the {name} pattern, as `.context/patterns.md` records"
_OVERLAID_BY_SESSION = "This session overlays the {name} pattern"


class SessionBrief:
    """What an agent following one action's instructions is told about the session the action works in: the session
    itself, the project root paths are named from, the session's root and where each listed practice writes
    (``session_context``), and the rules of the patterns the work is held to with the stories the session's increment is
    about (``overlay_rules``). The action holds one (``action.brief``), made with it; an action made for no session is
    told nothing."""

    def __init__(self, action: GuidanceAction) -> None:
        self._action = action

    def overlay_rules(self, paths: list[str] | None = None) -> str:
        """The shared rules of each pattern the work is held to, such as lern_domain_driven, which apply on top of the
        practices' rules: for content paths names, the patterns it was generated with; otherwise, as for generate, the
        patterns the session overlays. None for an action made for no session."""
        session = self._action.works_in
        if session is None:
            return ""
        patterns = self._action.graph.applied_patterns
        root = session.work_root
        recorded = GeneratedPatterns(patterns).recorded_for([root / path for path in paths or []], root)
        names = recorded or list(session.overlays)
        source = _RECORDED_IN_PATTERNS_FILE if recorded else _OVERLAID_BY_SESSION
        rules = [self._overlay_rules_of(patterns.pattern_named(name), name, source) for name in names if name in patterns.names]
        return "\n\n".join(part for part in [*rules, self._story_scope(names)] if part)

    def _story_scope(self, patterns: list[str]) -> str:
        """The stories this session's increment is about, which generate and validate work on, each with the patterns
        its content was generated with. Stories outside them are other increments' work."""
        stories = list(getattr(self._action.works_in, "stories", None) or [])
        if not stories:
            return ""
        return "\n".join([
            "## Stories in this session",
            "",
            "This session's increment is these stories, named in its ticket. Generate and validate every one of them with "
            f"the patterns its content is generated with ({', '.join(patterns) or 'none'}). Stories outside this list "
            "belong to other increments: do not generate, judge, or report them.",
            "",
            *(f"- {story}" for story in stories),
        ])

    def _overlay_rules_of(self, pattern: PracticeGuidance, name: str, source: str) -> str:
        """The pattern's shared rules, opened by where the pattern came from, so the reader can check that claim."""
        return (
            f"## Pattern overlay: {name}\n\n"
            f"{source.format(name=name)}, so its shared rules below apply on top of the practices' rules. "
            f"Its whole guidance is its instructions, `{pattern.slug}_instructions`.\n\n"
            f"{pattern.section_text('Shared rules')}"
        )

    @property
    def session_context(self) -> str:
        """The open session as an agent acting on this command needs it: its session.json, the project root paths
        are named from, the session's root, and where each listed practice writes. The agent works from the project's
        checkout, so every path it sees starts there; told nothing, it guesses where files go under a moved root."""
        session = self._action.works_in
        if session is None or session.record_folder is None:
            return ""
        writes = self._practice_folders()
        return "\n".join([
            "## Session",
            "",
            f"Session {session.name}, kept in {session.session_file.resolve().as_posix()}.",
            f"Name paths from the project's root, {session.checkout.root.as_posix()}, or absolute.",
            f"The session's root is {session.work_root.as_posix()}.",
            *(["", "Where each listed practice writes:", *writes] if writes else []),
            "",
            "```json",
            json.dumps(session.record.fields.as_dict(), indent=2),
            "```",
        ])

    def _practice_folders(self) -> list[str]:
        """One line per listed practice the session holds, naming the folder it writes in, so the agent never guesses
        where a practice's files go under a moved root."""
        held = [(listed, self._action.session_practice(listed)) for listed in self._action.listed() if not isinstance(listed, str)]
        return [f"- {listed.slug}: {output.folder.as_posix()}" for listed, output in held if output is not None]


@agent_toolset
class GuidanceAction:
    """An action, such as generate, on the guidance a call names, such as stories-story-map, made for the session that
    call works in.

    The cdd server makes a new action for each call (``for_call``), so the guidance a call names, the session it works
    in, and the fidelity it works at on each practice it lists belong to that action alone. The practices themselves
    are the session's, which every call in the session shares, so an action never moves a practice's current fidelity:
    it holds the fidelity it works at (``work.fidelity_of``) and hands that fidelity to each operation and log line. A board
    command names its ticket's session in a ``session=`` word, because it runs in whichever chat it is sent to, and the
    action reads it once into the *GuidanceCommand* it works on; any other call works in the session open in its
    project. What the agent is told about that session is the action's *SessionBrief* (``brief``). An action
    started inside another (``_inside``) is made for that action's session and works on the same practices, and logs
    nothing: only the action the call asked for has run. An action made for no session, such as one listed for install,
    logs nothing and keeps no format.
    """

    parameter_notes = {"guidance": GUIDANCE_PARAMETER}
    injects_rules: ClassVar[bool] = True
    """Whether the action hands the agent its listed Guidance's rules after it returns; an action that only records
    what exists, such as Document, sets it false."""

    def __init__(self, session: WorkedSession | None = None, call: ToolCall | None = None) -> None:
        super().__init__()
        self._session = session
        # The call this action was made for: every line it logs points at its chat, and it says where a graph build the
        # action starts runs; none in process. An action started inside another holds the same call.
        self.call = call
        self._logged_session_action: str | None = None
        # What this action works on: the guidance its call named, read once, and the fidelity it works at on each
        # practice it lists. An action started inside another holds a list made inside that action's (``_inside``).
        self.work = WorkList(session)
        self.files = ActionFiles(self)
        self.brief = SessionBrief(self)

    def for_call(self, call: ToolCall) -> GuidanceAction:
        """An action of this kind made for call and working on the guidance it names, read once into a
        *GuidanceCommand*: in the session that command names, else the session open in the call's project, else the
        session this action was made for. A session is space/session's *Session*, which the call opens; the framework
        never names its class."""
        guidance = call.arguments.get("guidance")
        command = GuidanceCommand.from_guidance(guidance)
        named = command.session_file
        action = self._made_for((call.session_named(named) if named else None) or call.session or self._session, call)
        if guidance is not None:
            action.work.take(command)
        return action

    def _made_for(self, session: WorkedSession | None, call: ToolCall | None = None) -> GuidanceAction:
        """An action of this kind, set up as this one is, made for session and call."""
        return type(self)(session=session, call=call)

    def session_for(self, call: ToolCall) -> WorkedSession | None:
        """The session this action logs call in: the one it was made for."""
        return self._session

    @property
    def works_in(self) -> WorkedSession | None:
        """The session this action was made for; none for an action made for no session."""
        return self._session

    @property
    def session(self) -> WorkedSession:
        """The session this action works in."""
        if self._session is None:
            raise ActionWorksInNoSession(type(self).__name__)
        return self._session

    @property
    def log(self) -> Any:
        """What this action writes in its session's log: each line points at the chat of the call it was made for."""
        return self.session.log.by(self.call.request.chat if self.call is not None else None)

    @property
    def graph(self) -> Any:
        """The knowledge graph of the session this action works in, which the cdd server holds between calls; an action
        whose agent writes files lists its ``refresh`` as the tool to call with exactly those files."""
        return self.session.graph

    @property
    def operation_type(self) -> type[AgentOperation]:
        """Each ``@agent_tool`` of an action logs its call as the action, such as ``render``."""
        return GuidanceAgentOperation

    def _work_on(self, guidance: GuidanceArg | None = None) -> None:
        """Work on what guidance names: its Guidance, or its text. Naming again what this action already works on keeps
        the Guidance it built, so its operations all work on the same objects."""
        if guidance is None or guidance == self.work.worked_on:
            return
        self.work.take(GuidanceCommand.from_guidance(guidance))

    def listed(self) -> list[ListedGuidance]:
        """The Guidance this action works on (``WorkList.listed``)."""
        return self.work.listed()

    def session_practice(self, practice: WorkedGuidance) -> Any:
        """What practice, one of this action's practices, has in the session it works in (its PracticeSessionOutput);
        none when the action works in no session or practice is no practice of the session."""
        if self._session is None:
            return None
        return next((output for output in self._session.practices.values() if output.guidance is practice), None)

    def _worked_fidelities(self) -> list[Any]:
        """What the fidelity this action works at on each listed practice has in this action's session (its
        FidelitySessionOutput), which the lines it logs name. Guidance that is no practice CDD has, and a practice
        worked at no fidelity, are left out: a log line names the fidelity work was done at."""
        found = [self._worked_output(listed) for listed in self.listed() if not isinstance(listed, str)]
        return [worked for worked in found if worked is not None]

    def _worked_output(self, practice: ListedGuidance) -> Any:
        """What the fidelity this action works at on practice has in its session; none for guidance the session does
        not hold."""
        held = self.session_practice(practice)
        fidelity = self.work.fidelity_of(practice) if held is not None else None
        return fidelity.session_output if fidelity is not None else None

    def _inside(
        self, action_type: type[GuidanceAction], guidance: str | list[ListedGuidance] | None = None
    ) -> GuidanceAction:
        """An action of action_type started inside this one: made for this action's session and call, and working on
        guidance, this action's text or some of its listed Guidance, or on everything this action works on when
        guidance is none. It holds this action and asks it for the practices and the fidelity it works at, so it works
        on the same objects at the same fidelity, and it logs nothing, since building this action's instructions runs
        its recipe without the agent doing its work."""
        inner = action_type(session=self._session, call=self.call)
        inner.work = WorkList(self._session, outer=self.work)
        inner.work._take_listed(guidance if guidance is not None else self.work.text if self.work.text is not None else self.listed())
        return inner

    def _tool_inside(self, action_type: type[GuidanceAction]) -> GuidanceAction:
        """An action of action_type started inside this one (``_inside``), as this action's recipe names it: a tool the
        agent calls, listed by name, rather than its own recipe pasted into this one's instructions with none of the
        call's arguments."""
        inner = self._inside(action_type)
        inner.mode = "tool"
        return inner

    def run(self, operation: Callable[[WorkedGuidance], Any], *, action: str = "") -> list[Any]:
        """Run ``operation`` on the guidance this action works on: once on its string, or once per Guidance."""
        self.log_running(action)
        try:
            return self.work.each(operation)
        except BaseException as failure:
            if self._session is not None:
                self.log.failure(failure, tool=action or type(self).__name__)
            raise

    def log_running(self, action: str) -> None:
        """Log that this action runs action, once, in the session it works in. An action started inside another logs
        nothing: the session board counts a generate line as generate done, so the generate a sketch's instructions end
        with must not say it ran while the agent has written nothing."""
        if not action or self._session is None or self.work.is_inside or self._logged_session_action == action:
            return
        self._logged_session_action = action
        self._log(action)

    def _log(self, action: str) -> None:
        """Write the line saying this action runs action, naming the practices it works on; an action such as Validate
        that logs differently overrides it."""
        self.log.guidance_action(action, self._worked_fidelities())

    # No recipe runs begin: every guidance action inherits it, and the prompt-notify hook reads its Toast, so a call to any
    # of an action's tools toasts as that action without the action annotating anything.
    @Toast
    @agent_instructions
    def begin(self, guidance: GuidanceArg | None = None, action: str = "") -> str:
        """Start a guidance action on the guidance it names, in the session the call names. With no named session the action runs in the main session. Follow act_quickly."""
        self._work_on(guidance)
        tools(self.act_quickly)
        return ""

    @property
    def session_context(self) -> str:
        """What the agent following this action's instructions is told about its session (``SessionBrief``)."""
        return self.brief.session_context

    @agent_instructions
    def act_quickly(self) -> str:
        """Guidance action code should finish in well under 10 seconds. Pass paths — a file, a list of files, or a folder — and let the action read them. Do not put a document body on an MCP call. If a call has stalled for more than 10 seconds, stop it, find the cause, and report that diagnosis. Add a failing test for that cause before changing the code. Do not rerun the same call outside the tool."""
        return (
            "Guidance action code should finish in well under 10 seconds. "
            "Pass paths — a file, a list of files, or a folder — and let the action read them. "
            "Do not put a document body on an MCP call. "
            "If a call has stalled for more than 10 seconds, stop it, find the cause, and report that diagnosis. "
            "Add a failing test for that cause before changing the code. "
            "Do not rerun the same call outside the tool."
        )

    @Toast
    @hook("postToolUse")
    def inject_rules(self, tool_use: HookPayload) -> dict[str, Any]:
        """Inject listed Guidance rules markdown after this action returns; tool_use is the tool call that just
        finished, as the IDE reports it."""
        if not self.injects_rules or not self._is_this_action(tool_use):
            return {}
        action = self.for_call(tool_use.call)
        parts, labels = action._listed_inject_parts(tool_use)
        if not parts:
            return {}
        return {"additional_context": "\n\n".join(parts), "toast": rules_toast(self.slug, labels)}

    def _listed_inject_parts(self, tool_use: HookPayload) -> tuple[list[str], list[str]]:
        parts: list[str] = []
        labels: list[str] = []
        for guidance in self.listed():
            text = guidance.rules_after_edit(tool_use) if isinstance(guidance, Guidance) else ""
            if text:
                parts.append(text)
                labels.append(type(guidance).__name__)
        return parts, labels

    def _is_this_action(self, tool_use: HookPayload) -> bool:
        """True when the hook is about one of the MCP tools this action publishes, however the IDE spells its name:
        ``generate.generate``, or ``mcp__cdd__generate_generate`` in Claude Code. Each tool says whether a spelling names
        it, by the rule the server resolves calls with."""
        return any(tool.is_called(tool_use.tool_name) for tool in self.tools_published_to(annotation_kinds.answering_calls))


class FidelityActionRunner:
    """Runs a guidance action on one fidelity, for ``fidelity.actions``: the action is made for the session the
    fidelity's practice works in and holds that fidelity, so it works on it whatever another call works on."""

    def works_on_fidelities(self, action: Action) -> bool:
        """Whether action is a guidance action whose operation takes the guidance a caller names."""
        return issubclass(action.toolset_class, GuidanceAction) and "guidance" in inspect.signature(action.operation).parameters

    def run(self, action: Action, fidelity: FidelityGuidance, arguments: dict[str, Any]) -> Any:
        """Run action on fidelity. A ``format`` the operation does not take is the format the fidelity works in."""
        practice = fidelity.practice_guidance
        made = action.toolset_class(session=practice.session if practice is not None else None)
        taken = inspect.signature(action.operation).parameters
        format = "" if "format" in taken else str(arguments.pop("format", "") or "")
        made.work.take_fidelity(fidelity, format)
        return getattr(made, action.name)(guidance=None, **arguments)


ACTION_CATALOGUE.run_actions_with(FidelityActionRunner())
