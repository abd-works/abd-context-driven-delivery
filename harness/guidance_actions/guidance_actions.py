"""First-order guidance-action prelude: an action made for its call's session runs an operation on the guidance the call
names."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, NotRequired, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import InstallDestination
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.action_catalogue import ActionCatalogue
from harness.guidance.documents import load_document
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


class GuidanceArgument:
    """The guidance argument a call sends an action, read as what the action works on. It is the Guidance list, one
    Guidance (a ``module:Class`` ref, a slug, a ``{"toolset": ...}`` mapping or its JSON, or a Guidance already made),
    or text the action runs once on. Agents on MCP often send several slugs, a ``format=`` word, and a ``session=`` word
    in one string; the slugs are Guidance, the format word is each one's format, and the session word names the
    session the call is for. A string with any other word is text, so prose still runs once."""

    def __init__(self, guidance: GuidanceArg) -> None:
        self._guidance = guidance

    @property
    def text(self) -> str | None:
        """The text the action runs once on; none when the argument names Guidance."""
        if not isinstance(self._guidance, str) or self._one_item() is not None or self._slug_words():
            return None
        return self._guidance

    @property
    def items(self) -> list:
        """Each Guidance the argument names, as a ref, a ref mapping, or the Guidance itself."""
        one = self._one_item() if not isinstance(self._guidance, list) else None
        if one is not None:
            return [one]
        if isinstance(self._guidance, str):
            return self._slug_words()
        return [item if (named := self._item(item)) is None else named for item in list(self._guidance or [])]

    @property
    def session_named(self) -> str:
        """The session.json a ``session=`` word names, as the session board writes it; empty when none does."""
        if not isinstance(self._guidance, str):
            return ""
        return next((word[len(_SESSION_WORD):] for word in self._guidance.split() if word.startswith(_SESSION_WORD)), "")

    def _one_item(self) -> Any:
        return self._item(self._guidance)

    def _slug_words(self) -> list:
        words = [word for word in self._guidance.split() if not word.startswith(_SESSION_WORD)]
        formats = [word[len(_FORMAT_WORD):].split(",")[0] for word in words if word.startswith(_FORMAT_WORD)]
        slugs = [slug for word in words if not word.startswith(_FORMAT_WORD) for slug in word.split(",") if slug]
        refs = [self._slug_ref(slug) for slug in slugs]
        if not refs or None in refs:
            return []
        if not formats or not formats[0]:
            return refs
        return [{**(ref if isinstance(ref, dict) else {"toolset": ref}), "format": formats[0]} for ref in refs]

    def _item(self, item: Any) -> Any:
        """One Guidance as item names it; none for a string that names none."""
        if not isinstance(item, str):
            return item
        text = item.strip()
        mapping = self._json_ref(text)
        if mapping is not None:
            return mapping
        return text if _TOOLSET_REF.match(text) else self._slug_ref(text)

    def _json_ref(self, text: str) -> dict[str, Any] | None:
        if not (text.startswith("{") and text.endswith("}")):
            return None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) and parsed.get("toolset") else None

    def _slug_ref(self, text: str) -> str | dict[str, Any] | None:
        return PracticeCatalogue.toolset_ref(text) if _GUIDANCE_SLUG.match(text) else None


class _NamedPractice:
    """The practice CDD has that one listed Guidance names, with the fidelity and format it names: a ref, a ref mapping,
    a practice already made, whose current fidelity and format are the ones it names, or one of a practice's fidelities,
    which names its practice at that fidelity and in its format. A mapping with constructor
    arguments of its own, or any other guidance, names no practice of a session."""

    def __init__(self, raw: Any) -> None:
        from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

        self.key: str | None = None
        self.fidelity = ""
        self.format = ""
        if isinstance(raw, PracticeGuidance):
            self._made(raw, raw.fidelities.current)
        elif isinstance(raw, FidelityGuidance) and raw.practice_guidance is not None:
            self._made(raw.practice_guidance, raw)
        elif isinstance(raw, dict) and not raw.get("context"):
            self.key = PracticeCatalogue.key_of(str(raw.get("toolset") or ""))
            self.fidelity = str(raw.get("fidelity") or "")
            self.format = str(raw.get("format") or "")
        elif isinstance(raw, str):
            self.key = PracticeCatalogue.key_of(raw)

    def _made(self, practice: Any, fidelity: Any) -> None:
        """A practice already made, at fidelity, one of its own, or at none."""
        if not PracticeCatalogue.has(practice.key):
            return
        self.key = practice.key
        self.fidelity = fidelity.name if fidelity is not None else ""
        self.format = (fidelity.format if fidelity is not None else practice.format) or ""


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
    in, and the practices it lists belong to that action alone: calls running at once never see each other's, and no
    call changes the session another call reads. A board command names its ticket's session in a ``session=`` word,
    because it runs in whichever chat it is sent to; any other call works in the session open in its project. An action
    started inside another (``_inside``) is made for that action's session and works on the same practices. An action
    made for no session, such as one listed for install, logs nothing and keeps no format.
    """

    parameter_notes = {"guidance": GUIDANCE_PARAMETER}
    injects_rules: ClassVar[bool] = True
    """Whether the action hands the agent its listed Guidance's rules after it returns; an action that only records
    what exists, such as Document, sets it false."""

    def __init__(self, session: Any = None) -> None:
        super().__init__()
        self._session = session
        # The guidance argument this action works on, so naming the same argument again keeps what it built.
        self._guidance_worked_on: Any = _NOTHING_WORKED_ON
        self._guidance_text: str | None = None
        self._tool_items: list = []
        self._listed_items: list | None = None
        self._logged_session_action: str | None = None
        # The fidelity this action works at on each listed practice, by the practice's id: the one its guidance named,
        # read once when listed, so a later call on another fidelity of the same practice does not change this one's.
        self._worked_at: dict[int, Any] = {}

    def for_call(self, call: ToolCall) -> GuidanceAction:
        """An action of this kind made for call and working on the guidance it names: in the session that guidance names
        in a ``session=`` word, else the session open in the call's project, else the session this action was made for.
        A session is space/session's *Session*, which the call opens; the framework never names its class."""
        guidance = call.arguments.get("guidance")
        argument = GuidanceArgument(guidance) if guidance is not None else None
        named = argument.session_named if argument is not None else ""
        action = self.made_for((call.session_named(named) if named else None) or call.session or self._session)
        if argument is not None:
            action._take(guidance, argument)
        return action

    def made_for(self, session: Any) -> GuidanceAction:
        """An action of this kind, set up as this one is, made for session."""
        return type(self)(session=session)

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
        return self._session.document_named(content, paths) if self._session is not None else load_document(content, paths)

    def _discover_operations(self) -> dict[str, AgentOperation]:
        from harness.agent_tools.agent_tools import AgentToolAnnotation, GuidanceAgentOperation

        members = self._members
        return {
            name: GuidanceAgentOperation(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.annotated if AgentToolAnnotation.annotates(member)
        }

    def _work_on(self, guidance: GuidanceArg | None = None) -> None:
        """Work on what guidance names: its Guidance, or its text. Naming again what this action already works on keeps
        the Guidance it built, so its operations all work on the same objects."""
        if guidance is None or guidance == self._guidance_worked_on:
            return
        self._take(guidance, GuidanceArgument(guidance))

    def _take(self, guidance: GuidanceArg, argument: GuidanceArgument) -> None:
        """Work on guidance, as argument, made once from it, reads it."""
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
            self._worked_at[id(practice)] = item
        return practice

    def practice_of(self, item: Any) -> Any:
        """The practice item belongs to: a fidelity's practice; item itself for a practice, other guidance, or text."""
        from harness.guidance.guidance import FidelityGuidance

        if isinstance(item, FidelityGuidance) and item.practice_guidance is not None:
            return item.practice_guidance
        return item

    def guidance_text(self) -> str | None:
        """The string to run this action on, when guidance was not a Guidance list."""
        return self._guidance_text

    def listed(self) -> list:
        """The Guidance this action works on. A practice CDD has is the session's own instance of it, the one the
        session's graph holds, working from now on at the fidelity the guidance names, whose format is the one the
        guidance names, else the one that fidelity last used; any other guidance is made from its ref."""
        if self._guidance_text is not None:
            return []
        if self._listed_items is None:
            self._listed_items = [self._worked_on(raw) for raw in self._tool_items]
        return self._listed_items

    def _worked_on(self, raw: Any) -> Any:
        """What raw names: the session's own practice, worked at the fidelity and format raw names, or guidance made
        from raw when it names no practice of this action's session."""
        named = _NamedPractice(raw)
        if self._session is None or named.key is None:
            return AgentToolSet.instantiate(self._held(raw))
        practice = self._session.practice(named.key).guidance
        fidelity = practice.work_at(named.fidelity) if named.fidelity else practice.fidelities.current
        if named.format:
            # The fidelity keeps the format it is given, so the next action on it works in it without being told.
            (fidelity if fidelity is not None else practice).format = named.format
        self._worked_at[id(practice)] = fidelity
        return practice

    def work_on_fidelity(self, fidelity: Any, format: str = "") -> None:
        """Work on fidelity, one fidelity of a practice, held for this action: its practice is the one Guidance this
        action lists, worked at that fidelity, in format when one is named, which the fidelity keeps."""
        practice = fidelity.practice_guidance
        practice.work_at(fidelity.name)
        if format:
            fidelity.format = format
        self._guidance_worked_on = fidelity
        self._guidance_text = None
        self._tool_items = [practice]
        self._listed_items = [practice]
        self._worked_at[id(practice)] = fidelity

    def fidelity_of(self, item: Any) -> Any:
        """The fidelity this action works at on item, one of the Guidance it lists: the one its guidance named, read
        when the action listed it, so another call working on another fidelity of the same practice never changes it;
        item's current fidelity for guidance no session holds, a fidelity ``each`` handed out is itself, and none for
        text."""
        from harness.guidance.guidance import FidelityGuidance

        if isinstance(item, FidelityGuidance):
            return item
        if id(item) in self._worked_at:
            return self._worked_at[id(item)]
        return getattr(getattr(item, "fidelities", None), "current", None)

    def _session_practice(self, item) -> Any:
        """The practice item is, as this action's session holds it; none when the action works in no session or item is
        no practice CDD has."""
        from harness.guidance.guidance import PracticeGuidance

        if self._session is None or not isinstance(item, PracticeGuidance) or not PracticeCatalogue.has(item.key):
            return None
        return self._session.practice(item.key)

    def _inside(self, action_type: type[GuidanceAction], guidance: str | list | None = None) -> GuidanceAction:
        """An action of action_type started inside this one: made for this action's session and working on guidance,
        this action's text or some of its listed Guidance, or on everything this action works on when guidance is
        none. It works on the same objects, so the session's practices stay the ones this action listed."""
        inner = action_type(session=self._session)
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
                self._session.log.failure(failure, tool=action or type(self).__name__)
            raise

    def log_running(self, action: str) -> None:
        """Log that this action runs action, once, in the session it works in; an action such as Validate that logs
        differently overrides it."""
        if not action or self._session is None or self._logged_session_action == action:
            return
        self._logged_session_action = action
        self.listed()
        self._session.log.guidance_action(action)

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
        stored = session_json.read_text(encoding="utf-8").strip() if session_json.is_file() else "{}"
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
        from harness.guidance.guidance import Guidance

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
