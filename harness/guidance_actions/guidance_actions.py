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
from harness.agent_tools.chat_pointer import ChatPointer
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.action_catalogue import ActionCatalogue
from harness.guidance.documents import document_in
from harness.guidance.guidance import FidelityGuidance, Guidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.hooks.hook_server import rules_toast
from harness.hooks.hooks import hook
from harness.annotations.annotation import Toast, annotation_kinds

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
        return [item if (named := self._item(item)) is None else named for item in list(self._guidance or [])]

    def _one_item(self) -> Any:
        return self._item(self._guidance)

    def _slug_words(self) -> list:
        words = [word for word in self._guidance.split() if not word.startswith(_SESSION_WORD)]
        formats = [word[len(_FORMAT_WORD):].split(",")[0] for word in words if word.startswith(_FORMAT_WORD)]
        slugs = [slug for word in words if not word.startswith(_FORMAT_WORD) for slug in word.split(",") if slug]
        named = [self._named(slug) for slug in slugs]
        if not named or None in named:
            return []
        format = formats[0] if formats else ""
        return [NamedGuidance(guidance, format) for guidance in named]

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
        was sent, for the action to make."""
        practice = None if mapping.get("context") else self._practice_of_class(str(mapping.get("toolset") or ""))
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

    def __init__(self, session: Any = None, chat: ChatPointer | None = None) -> None:
        super().__init__()
        self._session = session
        # The chat of the call this action was made for: every line it logs points at it.
        self._chat = chat
        # The guidance argument this action works on, so naming the same argument again keeps what it built.
        self._guidance_worked_on: Any = _NOTHING_WORKED_ON
        self._guidance_text: str | None = None
        self._tool_items: list = []
        self._listed_items: list | None = None
        self._logged_session_action: str | None = None
        self._practices: list[PracticeGuidance] | None = None
        # The action this one was started inside; none for the action a call asked for.
        self._outer: GuidanceAction | None = None
        # The fidelity this action works at on each listed practice: the one its guidance named, read once when listed.
        # The action holds it, never the practice, which every call in the session shares, so a later call on another
        # fidelity of the same practice changes nothing this one reads.
        self._worked_at: dict[PracticeGuidance, FidelityGuidance | None] = {}

    def for_call(self, call: ToolCall) -> GuidanceAction:
        """An action of this kind made for call and working on the guidance it names: in the session that guidance names
        in a ``session=`` word, else the session open in the call's project, else the session this action was made for.
        A session is space/session's *Session*, which the call opens; the framework never names its class."""
        guidance = call.arguments.get("guidance")
        named = session_file_named(guidance)
        action = self.made_for((call.session_named(named) if named else None) or call.session or self._session, call.chat)
        if guidance is not None:
            action._take(guidance)
        return action

    def made_for(self, session: Any, chat: ChatPointer | None = None) -> GuidanceAction:
        """An action of this kind, set up as this one is, made for session and the call from chat."""
        return type(self)(session=session, chat=chat)

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
        return self.session.log.by(self._chat)

    @property
    def graph(self) -> Any:
        """The knowledge graph of the session this action works in, which the cdd server holds between calls; an action
        whose agent writes files lists its ``refresh`` as the tool to call with exactly those files."""
        return self.session.graph

    def wrote(self, paths: list[str | Path]) -> None:
        """Refresh the session's graph with exactly the files this action just wrote, so the graph holds them as they
        are now; nothing watches the files. An action made for no session holds no graph to refresh."""
        if self._session is not None:
            self.graph.refresh([str(path) for path in paths])

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
        if guidance is None or guidance == self._guidance_worked_on:
            return
        self._take(guidance)

    def _take(self, guidance: GuidanceArg) -> None:
        """Work on guidance, read once into the practices and fidelities of this action's set that it names."""
        argument = GuidanceArgument(guidance, self._practice_set)
        self._guidance_worked_on = guidance
        self._listed_items = None
        self._guidance_text = argument.text
        self._tool_items = argument.items if self._guidance_text is None else []

    def _work_on_listed(self, worked_on: str | list) -> None:
        """Work on what another action already took: its text, or the Guidance it listed, as the same objects. A
        fidelity ``each`` handed it is its practice, worked at that fidelity."""
        self._guidance_worked_on = worked_on
        if isinstance(worked_on, str):
            self._guidance_text = worked_on
            self._tool_items = []
            self._listed_items = None
            return
        listed = [self._held(item) for item in worked_on]
        self._guidance_text = None
        self._tool_items = list(listed)
        self._listed_items = list(listed)

    def _held(self, item: Any) -> Any:
        """item as this action lists it: a fidelity is its practice, which this action works at that fidelity on; any
        other Guidance is itself."""
        practice = self.practice_of(item)
        if practice is not item:
            self._worked_at[practice] = item
        return practice

    def practice_of(self, item: Any) -> Any:
        """The practice item belongs to: a fidelity's practice; item itself for a practice, other guidance, or text."""
        if isinstance(item, FidelityGuidance) and item.practice_guidance is not None:
            return item.practice_guidance
        return item

    def listed(self) -> list:
        """The Guidance this action works on. A practice CDD has is the session's own instance of it, the one the
        session's graph holds, which this action works at the fidelity the guidance names (``fidelity_of``), else the
        fidelity the practice was made at; the practice itself stays where it was made. A format the guidance names is
        the one that fidelity keeps; any other guidance is made from its ref."""
        if self._guidance_text is not None:
            return []
        if self._listed_items is None:
            self._listed_items = [self._worked_on(raw) for raw in self._tool_items]
        return self._listed_items

    def _practice_set(self) -> list[PracticeGuidance]:
        """The practices this action works with, made known once: its session's own instances, the ones its graph
        holds; for an action made for no session, a set of its own."""
        if self._practices is None:
            session = self._session
            self._practices = (
                [output.guidance for output in session.practices.values()] if session is not None else PracticeCatalogue.create_all()
            )
        return self._practices

    def _worked_on(self, raw: Any) -> Any:
        """What raw names: a practice of this action's set, worked at the fidelity and in the format raw names; or
        guidance made from raw when it names none of them."""
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
        """A practice or fidelity made outside this action's session, such as one a spec makes, as the session's own
        instance of it, at the same fidelity and format; none for an action made for no session, which works on what
        it is handed, and for anything that is no practice of the session's set."""
        if self._session is None or not isinstance(made, (PracticeGuidance, FidelityGuidance)):
            return None
        practice = self.practice_of(made)
        own = next((candidate for candidate in self._practice_set() if type(candidate) is type(practice)), None)
        if own is None:
            return None
        fidelity = made if isinstance(made, FidelityGuidance) else practice.fidelities.current
        format = fidelity.format if fidelity is not None else practice.format
        return NamedGuidance(own.fidelities[fidelity.name] if fidelity is not None else own, format)

    def work_on_fidelity(self, fidelity: FidelityGuidance, format: str = "") -> None:
        """Work on fidelity, one fidelity of a practice, held for this action: its practice is the one Guidance this
        action lists, worked at that fidelity, in format when one is named, which the fidelity keeps."""
        practice = fidelity.practice_guidance
        if format:
            fidelity.format = format
        self._guidance_worked_on = fidelity
        self._guidance_text = None
        self._tool_items = [practice]
        self._listed_items = [practice]
        self._worked_at[practice] = fidelity

    def fidelity_of(self, item: Any) -> Any:
        """The fidelity this action works at on item, one of the Guidance it lists: the one its guidance named, read
        when the action listed it, so another call working on another fidelity of the same practice never changes it;
        item's current fidelity for guidance no session holds, a fidelity ``each`` handed out is itself, and none for
        text."""
        if isinstance(item, FidelityGuidance):
            return item
        if isinstance(item, PracticeGuidance) and item in self._worked_at:
            return self._worked_at[item]
        return getattr(getattr(item, "fidelities", None), "current", None)

    def _session_practice(self, item: Any) -> Any:
        """What item, one of this action's practices, has in the session it works in (its PracticeSessionOutput); none
        when the action works in no session or item is no practice of the session."""
        if self._session is None:
            return None
        return next((output for output in self._session.practices.values() if output.guidance is item), None)

    def _listed_practices(self) -> list:
        """Each listed practice as this action's session holds it at the fidelity this action works at on it, which
        the lines it logs name: that fidelity's FidelitySessionOutput, or the practice's PracticeSessionOutput for a
        practice worked at no fidelity. Guidance that is no practice CDD has is left out."""
        found = [self._worked_output(item) for item in self.listed() if not isinstance(item, str)]
        return [practice for practice in found if practice is not None]

    def _worked_output(self, item: Any) -> Any:
        practice = self._session_practice(item)
        fidelity = self.fidelity_of(item) if practice is not None else None
        held = fidelity.session_output if fidelity is not None else None
        return held if held is not None else practice

    def _inside(self, action_type: type[GuidanceAction], guidance: str | list | None = None) -> GuidanceAction:
        """An action of action_type started inside this one: made for this action's session and working on guidance,
        this action's text or some of its listed Guidance, or on everything this action works on when guidance is
        none. It works on the same objects, so the session's practices stay the ones this action listed, and it logs
        nothing, since building this action's instructions runs its recipe without the agent doing its work."""
        inner = action_type(session=self._session, chat=self._chat)
        inner._outer = self
        inner._practices = self._practices
        inner._worked_at = dict(self._worked_at)
        inner._work_on_listed(
            guidance if guidance is not None else self._guidance_text if self._guidance_text is not None else self.listed()
        )
        return inner

    def each(self, operation: Callable[[Any], Any]) -> list:
        """Run ``operation`` once on a guidance string, or once per Guidance. A listed practice is handed over as the
        fidelity this action works at on it, which answers its own instructions, templates, examples, rules and
        generate_output, so another call that moves the practice to another fidelity never changes this one's text;
        Guidance with no fidelity is handed over itself. A recipe reads only what the operation returns, so an
        operation gives its text back rather than reading it into nothing."""
        text = self._guidance_text
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
        if not action or self._session is None or self._outer is not None or self._logged_session_action == action:
            return
        self._logged_session_action = action
        self._log(action)

    def _log(self, action: str) -> None:
        """Write the line saying this action runs action, naming the practices it works on; an action such as Validate
        that logs differently overrides it."""
        self.log.guidance_action(action, self._listed_practices())

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
        """True when the hook is about one of this action's own MCP tools, whatever prefix the IDE gives its name:
        ``generate.generate``, or ``mcp__cdd__generate_generate`` in Claude Code."""
        called = self._comparable(payload.tool_name.rsplit("__", 1)[-1])
        own = {
            self._comparable(f"{self.slug}.{name}")
            for name, member in self._members.annotated if annotation_kinds.annotated_for(InstallDestination.MCP, member)
        }
        return bool(called) and called in own

    def _comparable(self, tool_name: str) -> str:
        return tool_name.casefold().replace(".", "_").replace("-", "_")


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
