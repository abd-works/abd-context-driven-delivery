"""First-order guidance-action prelude: an action made for its call's session runs an operation on the guidance the call
names."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar, NotRequired, Sequence, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import InstallDestination, ToolsetReference
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.action_catalogue import ActionCatalogue
from harness.guidance.documents import document_in
from harness.guidance.patterns_file import PatternsFile
from harness.guidance.guidance import FidelityGuidance, Guidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.hooks.hook_server import rules_toast
from harness.hooks.hooks import hook
from harness.annotations.annotation import Toast

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload


class GuidanceRef(TypedDict):
    """One Guidance: a toolset ref, plus the fidelity or context that ref accepts."""

    toolset: str
    fidelity: NotRequired[str]
    context: NotRequired[dict[str, Any]]


# Guidance list, one Guidance (ref or {toolset, …}), or a string to act on directly.
GuidanceArg = str | GuidanceRef | list[str | GuidanceRef]
GUIDANCE_PARAMETER = (
    "guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. "
    "A list runs this action once per slug. A module:Class ref is that slug after lookup. "
    "Any other string is text this action runs once."
)
_TOOLSET_REF = re.compile(r"^[A-Za-z_][\w.]*:[A-Za-z_]\w*$")
_GUIDANCE_SLUG = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")
_FORMAT_WORD = "format="
# The session a command is for, as the session board names it: `session=.sessions/<name>/session.json`.
_SESSION_WORD = "session="
# The pattern overlays a command runs with, as the chat bar names them: `overlays=lern_domain_driven,mern_domain_driven`.
_OVERLAYS_WORD = "overlays="
# What an action works on before it names any guidance; None cannot stand for it, since naming None keeps what it had.
_NOTHING_WORKED_ON = object()
PATHS_NOTE = (
    "paths: a file, a list of files, or a folder. Pass paths on an MCP call. "
    "This action reads them locally. Leave the document body out of the call."
)


def session_file_named(guidance: Any) -> str:
    """The session.json a ``session=`` word of guidance names, as the session board writes it; empty when none does. A
    board command is chat text typed into whichever chat it is sent to, so the word is read here, once, at the call."""
    if not isinstance(guidance, str):
        return ""
    return next((word[len(_SESSION_WORD):] for word in guidance.split() if word.startswith(_SESSION_WORD)), "")


def overlays_named(guidance: GuidanceArg) -> list[str] | None:
    """The patterns an ``overlays=`` word of guidance names, comma separated; none when no such word is there, so the
    session keeps the overlays it has. A word with nothing after it names no overlay, and clears them."""
    if not isinstance(guidance, str):
        return None
    word = next((word for word in guidance.split() if word.startswith(_OVERLAYS_WORD)), None)
    return None if word is None else [name for name in word[len(_OVERLAYS_WORD):].split(",") if name]


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


class UnknownGuidance(ValueError):
    """A listed guidance word that no practice or fidelity of the action's set has as its slug, such as
    ``clean_engineering`` for ``clean-engineering``. The message lists the slugs there are, so the caller can send one."""

    def __init__(self, word: str, slugs: Sequence[str]) -> None:
        super().__init__(f"no practice or fidelity has the slug {word!r}; the slugs are {', '.join(slugs)}")
        self.word = word
        self.slugs = tuple(slugs)


class GuidanceArgument:
    """The guidance argument a call sends an action, read as what the action works on. It is the Guidance list, one
    Guidance (a slug, a ``module:Class`` ref, a ``{"toolset": ...}`` mapping or its JSON, or a Guidance already made),
    or text the action runs once on. Agents on MCP often send several slugs, a ``format=`` word, and a ``session=`` word
    in one string; the slugs are Guidance, the format word is each one's format, and the session word names the
    session the call is for. A string with any other word is text, so prose still runs once.

    A slug or a ref names a practice or a fidelity of the practices the action works with (``practices``), and is read
    once into that object, so the action never looks it up again."""

    def __init__(self, guidance: GuidanceArg, practices: Callable[[], Sequence[PracticeGuidance]]) -> None:
        self._guidance = guidance
        self._practices = practices

    @property
    def text(self) -> str | None:
        """The text the action runs once on; none when the argument names Guidance."""
        if not isinstance(self._guidance, str) or self._one_item() is not None or self._slug_words():
            return None
        return self._guidance

    @property
    def items(self) -> list:
        """Each Guidance the argument names: a *NamedGuidance* for a practice of the action's set or one of its
        fidelities; any other Guidance as the ref, ref mapping, or object it was sent as."""
        one = self._one_item() if not isinstance(self._guidance, list) else None
        if one is not None:
            return [one]
        if isinstance(self._guidance, str):
            return self._slug_words()
        return [self._listed(item) for item in list(self._guidance or [])]

    def _listed(self, item: Any) -> Any:
        """One entry of a Guidance list: the Guidance it names. A word in a list is a slug, so a word that names no
        practice or fidelity raises *UnknownGuidance* rather than being made as a ``module:Class`` ref."""
        named = self._item(item)
        if named is None and isinstance(item, str):
            raise UnknownGuidance(item, self.slugs)
        return item if named is None else named

    @property
    def slugs(self) -> list[str]:
        """Every slug a call can name: each practice's, then each of its fidelities'."""
        return [slug for practice in self._practices() for slug in (practice.slug, *practice.fidelity_slugs)]

    def _one_item(self) -> Any:
        return self._item(self._guidance)

    def _slug_words(self) -> list:
        words = [word for word in self._guidance.split() if not word.startswith((_SESSION_WORD, _OVERLAYS_WORD))]
        listed = next((word[len(_FORMAT_WORD):].split(",") for word in words if word.startswith(_FORMAT_WORD)), [])
        slugs = [slug for word in words if not word.startswith(_FORMAT_WORD) for slug in word.split(",") if slug]
        named = [self._named(slug) for slug in slugs]
        if not named or None in named:
            return []
        return [NamedGuidance(guidance, self._listed_format_of(guidance, listed)) for guidance in named]

    def _listed_format_of(self, guidance: PracticeGuidance | FidelityGuidance, listed: list[str]) -> str:
        """The first listed format the guidance writes: a stage Run lists the formats of every fidelity it acts on, and
        each fidelity takes its own. A practice, or a fidelity that writes none of them, takes the first."""
        outputs = guidance.outputs if isinstance(guidance, FidelityGuidance) else {}
        written = [name for name in listed if name in outputs]
        return (written or listed or [""])[0]

    def _item(self, item: Any) -> Any:
        """One Guidance as item names it; none for a string that names none."""
        if not isinstance(item, str):
            return self._mapped(item) if isinstance(item, dict) else item
        text = item.strip()
        mapping = self._json_ref(text)
        if mapping is not None:
            return self._mapped(mapping)
        if _TOOLSET_REF.match(text):
            return self._mapped({"toolset": text})
        named = self._named(text)
        return NamedGuidance(named) if named is not None else None

    def _mapped(self, mapping: dict[str, Any]) -> Any:
        """A ``{toolset, fidelity, format}`` mapping as the practice of the action's set its toolset names, at its
        fidelity; a mapping with constructor arguments of its own, or one whose toolset is no practice of the set, as it
        was sent, for the action to make. A toolset that is no ``module:Class`` ref raises *UnknownGuidance*."""
        toolset = str(mapping.get("toolset") or "")
        if not _TOOLSET_REF.match(toolset):
            raise UnknownGuidance(toolset, self.slugs)
        practice = None if mapping.get("context") else self._practice_of_class(toolset)
        if practice is None:
            return mapping if len(mapping) > 1 else mapping.get("toolset")
        fidelity = str(mapping.get("fidelity") or "")
        return NamedGuidance(practice.fidelities[fidelity] if fidelity else practice, str(mapping.get("format") or ""))

    def _practice_of_class(self, reference: str) -> PracticeGuidance | None:
        toolset_class = ToolsetReference(reference).toolset_class
        return next((practice for practice in self._practices() if type(practice) is toolset_class), None)

    def _named(self, slug: str) -> PracticeGuidance | FidelityGuidance | None:
        """The practice or fidelity slug names among the action's practices: by its slug, such as ``stories`` or
        ``stories-story-map``, else a fidelity by its bare name in kebab case, such as ``story-map``, the first
        practice's in catalogue order when two share it. None for anything else."""
        if not _GUIDANCE_SLUG.match(slug):
            return None
        practices = self._practices()
        named = next((found for practice in practices if (found := practice.answers_to(slug)) is not None), None)
        return named or next((found for practice in practices if (found := practice.fidelity_called(slug)) is not None), None)

    def _json_ref(self, text: str) -> dict[str, Any] | None:
        if not (text.startswith("{") and text.endswith("}")):
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) and parsed.get("toolset") else None


class WorkList:
    """What one guidance action works on: the guidance its call named, read once into its text or into the practices of
    the action's set, and the fidelity the action works at on each practice it lists. The action holds one. The
    fidelity is held here, never on the practice, which every call in a session shares, so a later call on another
    fidelity of the same practice changes nothing this one reads. A list made inside another action's (``outer``) asks
    that list for the practices it works with and the fidelity it works at on a practice it names no fidelity of."""

    def __init__(self, session: Any, outer: WorkList | None = None) -> None:
        self._session = session
        self._outer = outer
        # The guidance argument taken, so naming the same argument again keeps what it built.
        self.worked_on: Any = _NOTHING_WORKED_ON
        self.text: str | None = None
        self._items: list = []
        self._listed: list | None = None
        self._practices: list[PracticeGuidance] | None = None
        self._worked_at: dict[PracticeGuidance, FidelityGuidance | None] = {}

    @property
    def is_inside(self) -> bool:
        """Whether this list was made inside another action's: the action that holds it was started by another."""
        return self._outer is not None

    def take(self, guidance: GuidanceArg) -> None:
        """Work on guidance, read once into the practices and fidelities of the action's set that it names. An
        ``overlays=`` word chooses those pattern overlays on the session first, so the action runs with them."""
        overlays = overlays_named(guidance)
        if overlays is not None and self._session is not None:
            self._session.choose_overlays(overlays)
        argument = GuidanceArgument(guidance, self.practice_set)
        self.worked_on = guidance
        self._listed = None
        self.text = argument.text
        self._items = argument.items if self.text is None else []

    def take_listed(self, worked_on: str | list) -> None:
        """Work on what another action already took: its text, or the Guidance it listed, as the same objects. A
        fidelity ``each`` handed it is its practice, worked at that fidelity."""
        self.worked_on = worked_on
        if isinstance(worked_on, str):
            self.text, self._items, self._listed = worked_on, [], None
            return
        listed = [self._held(item) for item in worked_on]
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

    def listed(self) -> list:
        """The Guidance worked on. A practice CDD has is the session's own instance of it, the one the session's graph
        holds, worked at the fidelity the guidance names (``fidelity_of``), else the fidelity the practice was made at;
        the practice itself stays where it was made. A format the guidance names is the one that fidelity keeps; any
        other guidance is made from its ref."""
        if self.text is not None:
            return []
        if self._listed is None:
            self._listed = [self._worked_on(raw) for raw in self._items]
        return self._listed

    def practice_set(self) -> list[PracticeGuidance]:
        """The practices worked with, made known once: the session's own instances, the ones its graph holds; for no
        session, a set of their own; for a list made inside another action's, that list's."""
        if self._outer is not None:
            return self._outer.practice_set()
        if self._practices is None:
            session = self._session
            self._practices = (
                [output.guidance for output in session.practices.values()] if session is not None else PracticeCatalogue.create_all()
            )
        return self._practices

    def practice_of(self, item: Any) -> Any:
        """The practice item belongs to: a fidelity's practice; item itself for a practice, other guidance, or text."""
        if isinstance(item, FidelityGuidance) and item.practice_guidance is not None:
            return item.practice_guidance
        return item

    def fidelity_of(self, item: Any) -> Any:
        """The fidelity worked at on item, one of the Guidance listed: the one its guidance named, read when it was
        listed; item's current fidelity for guidance no session holds; a fidelity ``each`` handed out is itself, and
        none for text. A list made inside another action's works at the fidelity that one works at, unless it was
        handed a fidelity of its own."""
        if isinstance(item, FidelityGuidance):
            return item
        if isinstance(item, PracticeGuidance) and item in self._worked_at:
            return self._worked_at[item]
        if self._outer is not None:
            return self._outer.fidelity_of(item)
        return getattr(getattr(item, "fidelities", None), "current", None)

    def _held(self, item: Any) -> Any:
        """item as it is listed: a fidelity is its practice, worked at that fidelity; any other Guidance is itself."""
        practice = self.practice_of(item)
        if practice is not item:
            self._worked_at[practice] = item
        return practice

    def _worked_on(self, raw: Any) -> Any:
        """What raw names: a practice of the set, worked at the fidelity and in the format raw names; or guidance made
        from raw when it names none of them."""
        named = raw if isinstance(raw, NamedGuidance) else self._own_counterpart(raw)
        if named is None:
            return AgentToolSet.instantiate(self._held(raw))
        practice = named.practice
        fidelity = named.guidance if named.guidance is not practice else practice.fidelities.current
        if named.format:
            # The fidelity keeps the format it is given in its session, so the next action on it works in it without
            # being told: the kept format is the session's choice, which every chat of the session reads.
            (fidelity if fidelity is not None else practice).format = named.format
        if self._session is not None:
            self._session.practice(practice.key)
        self._worked_at[practice] = fidelity
        return practice

    def _own_counterpart(self, made: Any) -> NamedGuidance | None:
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


@agent_toolset
class GuidanceAction:
    """An action, such as generate, on the guidance a call names, such as stories-story-map, made for the session that
    call works in.

    The cdd server makes a new action for each call (``for_call``), so the guidance a call names, the session it works
    in, and the fidelity it works at on each practice it lists belong to that action alone. The practices themselves
    are the session's, which every call in the session shares, so an action never moves a practice's current fidelity:
    it holds the fidelity it works at (``fidelity_of``) and hands that fidelity to each operation and log line. A board command names its ticket's session in a ``session=`` word,
    because it runs in whichever chat it is sent to; any other call works in the session open in its project. An action
    started inside another (``_inside``) is made for that action's session and works on the same practices, and logs
    nothing: only the action the call asked for has run. An action made for no session, such as one listed for install,
    logs nothing and keeps no format.
    """

    parameter_notes = {"guidance": GUIDANCE_PARAMETER}
    injects_rules: ClassVar[bool] = True
    """Whether the action hands the agent its listed Guidance's rules after it returns; an action that only records
    what exists, such as Document, sets it false."""

    def __init__(self, session: Any = None, call: ToolCall | None = None) -> None:
        super().__init__()
        self._session = session
        # The call this action was made for: every line it logs points at its chat, and it says where a graph build the
        # action starts runs; none in process. An action started inside another holds the same call.
        self.call = call
        self._logged_session_action: str | None = None
        # What this action works on: the guidance its call named, read once, and the fidelity it works at on each
        # practice it lists. An action started inside another holds a list made inside that action's (``_inside``).
        self.work = WorkList(session)

    def for_call(self, call: ToolCall) -> GuidanceAction:
        """An action of this kind made for call and working on the guidance it names: in the session that guidance names
        in a ``session=`` word, else the session open in the call's project, else the session this action was made for.
        A session is space/session's *Session*, which the call opens; the framework never names its class."""
        guidance = call.arguments.get("guidance")
        named = session_file_named(guidance)
        action = self.made_for((call.session_named(named) if named else None) or call.session or self._session, call)
        if guidance is not None:
            action.work.take(guidance)
        return action

    def made_for(self, session: Any, call: ToolCall | None = None) -> GuidanceAction:
        """An action of this kind, set up as this one is, made for session and call."""
        return type(self)(session=session, call=call)

    def session_for(self, call: ToolCall) -> Any:
        """The session this action logs call in: the one it was made for."""
        return self._session

    @property
    def session(self) -> Any:
        """The session this action works in."""
        if self._session is None:
            raise ActionWorksInNoSession(type(self).__name__)
        return self._session

    @property
    def log(self) -> Any:
        """What this action writes in its session's log: each line points at the chat of the call it was made for."""
        return self.session.log.by(self.call.chat if self.call is not None else None)

    @property
    def graph(self) -> Any:
        """The knowledge graph of the session this action works in, which the cdd server holds between calls; an action
        whose agent writes files lists its ``refresh`` as the tool to call with exactly those files."""
        return self.session.graph

    def _overlay_rules(self, paths: list[str] | None = None) -> str:
        """The shared rules of each pattern the work is held to, such as lern_domain_driven, which apply on top of the
        practices' rules: for content paths names, the patterns it was generated with; otherwise, as for generate, the
        patterns the session overlays. None for an action made for no session."""
        if self._session is None:
            return ""
        names = self._patterns_of(paths)
        rules = [self._overlay_rules_of(self.graph.applied_patterns.pattern_named(name), name) for name in names if self._is_pattern(name)]
        return "\n\n".join(part for part in [*rules, self._story_scope(names)] if part)

    def _patterns_of(self, paths: list[str] | None) -> list[str]:
        """The patterns the content at paths was generated with, from the `.context/patterns.md` nearest each path; the
        session's overlays for no paths, or for content no patterns file names, which no generate has recorded yet."""
        root = self.session.work_root
        found = [PatternsFile.nearest(root / path, root) for path in paths or []]
        recorded = [name for patterns in found if patterns is not None for name in patterns.patterns]
        return list(dict.fromkeys(recorded)) or list(self.session.overlays)

    def _is_pattern(self, name: str) -> bool:
        try:
            self.graph.applied_patterns.pattern_named(name)
        except KeyError:
            return False
        return True

    def record_patterns(self, folders: list[Path]) -> str:
        """Record the patterns the session overlays in `.context/patterns.md` at the root of each folder, so validate
        later judges the content with the patterns it was generated with; and say how to name the roles a folder holds
        of a pattern whose layers sit in several folders."""
        overlays = list(self.session.overlays) if self._session is not None else []
        if not overlays:
            return ""
        for folder in folders:
            PatternsFile(folder).record(overlays)
        written = ", ".join(PatternsFile(folder).path.as_posix() for folder in folders) or "none yet"
        roles = [f"- {name}: {', '.join(self._roles_of(name))}" for name in overlays if self._is_pattern(name) and self._roles_of(name)]
        return "\n".join([
            "## Patterns this content is generated with",
            "",
            f"This generate uses {', '.join(overlays)}, and records them in `.context/patterns.md` at the root of each "
            f"folder it writes ({written}). Write the same file, listing these patterns, at the root of any other folder "
            "you write content in. When a pattern's layers sit in several folders, name after the pattern the roles this "
            "folder holds (`- cdd_web_domain_access: Domain, Tool, Contract`); a folder that holds the whole pattern names "
            "none. Keep the patterns and roles already there. The roles each pattern has:",
            "",
            *roles,
        ])

    def _roles_of(self, name: str) -> list[str]:
        """The layers a pattern's table names (`| Layer | File | Role |`), the roles a folder can hold of it."""
        text = self.graph.applied_patterns.pattern_named(name).section_text("Overview")
        rows = text.splitlines()
        header = next((index for index, row in enumerate(rows) if row.strip().startswith("| Layer |")), None)
        if header is None:
            return []
        roles = []
        for row in rows[header + 2:]:
            if not row.strip().startswith("|"):
                break
            roles.append(row.strip().strip("|").split("|")[0].strip())
        return roles

    def _story_scope(self, patterns: list[str]) -> str:
        """The stories this session's increment is about, which generate and validate work on, each with the patterns
        its content was generated with. Stories outside them are other increments' work."""
        stories = list(getattr(self._session, "stories", None) or [])
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

    def _overlay_rules_of(self, pattern: PracticeGuidance, name: str) -> str:
        return (
            f"## Pattern overlay: {name}\n\n"
            f"This session overlays the {name} pattern, so its shared rules below apply on top of the practices' rules. "
            f"Its whole guidance is its instructions, `{pattern.slug}_instructions`.\n\n"
            f"{pattern.section_text('Shared rules')}"
        )

    def wrote(self, paths: list[str | Path]) -> None:
        """Refresh the session's graph with exactly the files this action just wrote, so the graph holds them as they
        are now; nothing watches the files. An action made for no session holds no graph to refresh."""
        if self._session is not None:
            self.graph.refresh([str(path) for path in paths], self.call)

    def source_label(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """What an instruction names as its source: the paths a call names, one per line, else its in-process text. The
        file bodies stay on disk."""
        if paths in ("", None, []):
            return content or ""
        return paths if isinstance(paths, str) else "\n".join(str(entry) for entry in paths)

    def path_named(self, named: str | Path) -> Path:
        """named as a path in this action's session's project; an absolute path stays where it is, in no session too."""
        path = Path(named)
        return path.resolve() if path.is_absolute() else self.session.path_named(path)

    def document_named(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """The document a call names: content, or the files at paths read from this action's session's project; an
        action made for no session, such as one run in process, reads paths as given."""
        return document_in(self._session, content, paths)

    @property
    def operation_type(self) -> type[AgentOperation]:
        """Each ``@agent_tool`` of an action logs its call as the action, such as ``render``."""
        return GuidanceAgentOperation

    def _work_on(self, guidance: GuidanceArg | None = None) -> None:
        """Work on what guidance names: its Guidance, or its text. Naming again what this action already works on keeps
        the Guidance it built, so its operations all work on the same objects."""
        if guidance is None or guidance == self.work.worked_on:
            return
        self.work.take(guidance)

    def practice_of(self, item: Any) -> Any:
        """The practice item belongs to: a fidelity's practice; item itself for a practice, other guidance, or text."""
        return self.work.practice_of(item)

    def listed(self) -> list:
        """The Guidance this action works on (``WorkList.listed``)."""
        return self.work.listed()

    @property
    def practice_slugs(self) -> list[str]:
        """The slug of each practice this action works with, in catalogue order: the words a call names one by."""
        return [practice.slug for practice in self.work.practice_set()]

    def work_on_fidelity(self, fidelity: FidelityGuidance, format: str = "") -> None:
        """Work on fidelity, one fidelity of a practice, held for this action: its practice is the one Guidance this
        action lists, worked at that fidelity, in format when one is named, which the fidelity keeps."""
        self.work.take_fidelity(fidelity, format)

    def fidelity_of(self, item: Any) -> Any:
        """The fidelity this action works at on item, one of the Guidance it lists (``WorkList.fidelity_of``)."""
        return self.work.fidelity_of(item)

    def _session_practice(self, item: Any) -> Any:
        """What item, one of this action's practices, has in the session it works in (its PracticeSessionOutput); none
        when the action works in no session or item is no practice of the session."""
        if self._session is None:
            return None
        return next((output for output in self._session.practices.values() if output.guidance is item), None)

    def _worked_fidelities(self) -> list:
        """What the fidelity this action works at on each listed practice has in this action's session (its
        FidelitySessionOutput), which the lines it logs name. Guidance that is no practice CDD has, and a practice
        worked at no fidelity, are left out: a log line names the fidelity work was done at."""
        found = [self._worked_output(item) for item in self.listed() if not isinstance(item, str)]
        return [worked for worked in found if worked is not None]

    def _worked_output(self, item: Any) -> Any:
        practice = self._session_practice(item)
        fidelity = self.fidelity_of(item) if practice is not None else None
        return fidelity.session_output if fidelity is not None else None

    def _inside(self, action_type: type[GuidanceAction], guidance: str | list | None = None) -> GuidanceAction:
        """An action of action_type started inside this one: made for this action's session and call, and working on
        guidance, this action's text or some of its listed Guidance, or on everything this action works on when
        guidance is none. It holds this action and asks it for the practices and the fidelity it works at, so it works
        on the same objects at the same fidelity, and it logs nothing, since building this action's instructions runs
        its recipe without the agent doing its work."""
        inner = action_type(session=self._session, call=self.call)
        inner.work = WorkList(self._session, outer=self.work)
        inner.work.take_listed(guidance if guidance is not None else self.work.text if self.work.text is not None else self.listed())
        return inner

    def each(self, operation: Callable[[Any], Any]) -> list:
        """Run ``operation`` once on a guidance string, or once per Guidance. A listed practice is handed over as the
        fidelity this action works at on it, which answers its own instructions, templates, examples, rules and
        generate_output, so another call that moves the practice to another fidelity never changes this one's text;
        Guidance with no fidelity is handed over itself. A recipe reads only what the operation returns, so an
        operation gives its text back rather than reading it into nothing."""
        text = self.work.text
        if text is not None:
            return [operation(text)]
        return [operation(self.at_fidelity(item)) for item in self.listed()]

    def as_tool(self) -> GuidanceAction:
        """This action as another action's recipe names it: a tool the agent calls, listed by name, rather than its own
        recipe pasted into the other's instructions with none of the call's arguments."""
        self.mode = "tool"
        return self

    def rules_to_follow(self) -> str:
        """The rules each listed guidance holds the agent to, read from the fidelity this action works at on it: its
        shared rules and that fidelity's, or the guidance text itself. It checks nothing, so it saves no report and logs
        no validate line, which would tell the session board the work had been checked."""
        return "\n\n".join(part for part in self.each(self._rules_of) if part)

    def _rules_of(self, item: Any) -> str:
        return item if isinstance(item, str) else item.checked_rules_text()

    def at_fidelity(self, item: Any) -> Any:
        """item, one of the Guidance this action lists, as the fidelity this action works at on it; item itself when it
        has none."""
        fidelity = self.fidelity_of(item)
        return fidelity if fidelity is not None else item

    def run(self, operation: Callable[[Any], Any], *, action: str = "") -> list:
        """Run ``operation`` on the guidance this action works on: once on its string, or once per Guidance."""
        self.log_running(action)
        try:
            return self.each(operation)
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
        """The open session as an agent acting on this command needs it: its session.json, the project root paths
        are named from, the session's root, and where each listed practice writes. The agent works from the project's
        checkout, so every path it sees starts there; told nothing, it guesses where files go under a moved root."""
        session = self._session
        if session is None or session.session_path is None:
            return ""
        session_json = session.session_file
        root = session.work_root.as_posix()
        project = session.repo_path.as_posix()
        practices = [(item, self._session_practice(item)) for item in self.listed() if not isinstance(item, str)]
        writes = [f"- {item.slug}: {practice.folder.as_posix()}" for item, practice in practices if practice is not None]
        stored = json.dumps(session.fields, indent=2)
        return "\n".join([
            "## Session",
            "",
            f"Session {session.name}, kept in {session_json.resolve().as_posix()}.",
            f"Name paths from the project's root, {project}, or absolute.",
            f"The session's root is {root}.",
            *(["", "Where each listed practice writes:", *writes] if writes else []),
            "",
            "```json",
            stored,
            "```",
        ])

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
    def inject_rules(self, payload: HookPayload) -> dict[str, Any]:
        """Inject listed Guidance rules markdown after this action returns."""
        if not self.injects_rules or not self._payload_is_this_action(payload):
            return {}
        action = self.for_call(payload.call)
        parts, labels = action._listed_inject_parts(payload)
        if not parts:
            return {}
        return {"additional_context": "\n\n".join(parts), "toast": rules_toast(self.slug, labels)}

    def _listed_inject_parts(self, payload: HookPayload) -> tuple[list[str], list[str]]:
        parts: list[str] = []
        labels: list[str] = []
        for guidance in self.listed():
            text = guidance.rules_after_edit(payload) if isinstance(guidance, Guidance) else ""
            if text:
                parts.append(text)
                labels.append(type(guidance).__name__)
        return parts, labels

    def _payload_is_this_action(self, payload: HookPayload) -> bool:
        """True when the hook is about one of the MCP tools this action publishes, however the IDE spells its name:
        ``generate.generate``, or ``mcp__cdd__generate_generate`` in Claude Code. Each tool says whether a spelling names
        it, by the rule the server resolves calls with."""
        return any(tool.is_called(payload.tool_name) for tool in self.tools_for(InstallDestination.MCP))


class FidelityActionRunner:
    """Runs a guidance action on one fidelity, for ``fidelity.actions``: the action is made for the session the
    fidelity's practice works in and holds that fidelity, so it works on it whatever another call works on."""

    def works_on_fidelities(self, action: Any) -> bool:
        """Whether action is a guidance action whose operation takes the guidance a caller names."""
        return issubclass(action.toolset_class, GuidanceAction) and "guidance" in inspect.signature(action.operation).parameters

    def run(self, action: Any, fidelity: Any, arguments: dict[str, Any]) -> Any:
        """Run action on fidelity. A ``format`` the operation does not take is the format the fidelity works in."""
        practice = fidelity.practice_guidance
        made = action.toolset_class(session=practice.session if practice is not None else None)
        taken = inspect.signature(action.operation).parameters
        format = "" if "format" in taken else str(arguments.pop("format", "") or "")
        made.work_on_fidelity(fidelity, format)
        return getattr(made, action.name)(guidance=None, **arguments)


ActionCatalogue.run_actions_with(FidelityActionRunner())
