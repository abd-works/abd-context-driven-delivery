"""First-order guidance-action prelude: an action made for its call's session runs an operation on the guidance the call
names."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, NotRequired, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import InstallDestination
from harness.name.name import Name
from harness.agent_tools.tool_call import ToolCall
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

    def for_call(self, call: ToolCall) -> GuidanceAction:
        """An action of this kind made for call and working on the guidance it names: in the session that guidance names
        in a ``session=`` word, else the session open in the call's project, else the session this action was made for.
        A session is space/session's *Session*, which the call opens; the framework never names its class."""
        guidance = call.arguments.get("guidance")
        named = GuidanceArgument(guidance).session_named if guidance is not None else ""
        action = self.made_for((call.session_named(named) if named else None) or call.session or self._session)
        action._work_on(guidance)
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
        argument = GuidanceArgument(guidance)
        self._guidance_worked_on = guidance
        self._listed_items = None
        self._guidance_text = argument.text
        self._tool_items = argument.items if self._guidance_text is None else []

    def _work_on_listed(self, worked_on: str | list) -> None:
        """Work on what another action already took: its text, or the Guidance it listed, as the same objects."""
        self._guidance_worked_on = worked_on
        if isinstance(worked_on, str):
            self._guidance_text = worked_on
            self._tool_items = []
            self._listed_items = None
            return
        self._guidance_text = None
        self._tool_items = list(worked_on)
        self._listed_items = list(worked_on)

    def guidance_text(self) -> str | None:
        """The string to run this action on, when guidance was not a Guidance list."""
        return self._guidance_text

    def listed(self) -> list:
        """The Guidance this action works on, each practice worked on in this action's session: its practice adopts it,
        and a fidelity the guidance named no format for works in the format it was last given in that session."""
        if self._guidance_text is not None:
            return []
        if self._listed_items is None:
            items = AgentToolSet.instantiate_all(self._tool_items)
            for item, raw in zip(items, self._tool_items):
                self._work_in_session(item, chose_format=self._chooses_format(raw))
            self._listed_items = items
        return self._listed_items

    def _names_format(self, raw: Any) -> bool:
        return isinstance(raw, dict) and bool(raw.get("format"))

    def _chooses_format(self, raw: Any) -> bool:
        """Whether the caller chose this guidance's format: a ref naming one, or guidance already built, which carries
        its own."""
        return self._names_format(raw) or not isinstance(raw, (str, dict))

    def _session_practice(self, item) -> Any:
        """The practice item is, as this action's session holds it; none when the action works in no session or item is
        no practice CDD has."""
        from harness.guidance.guidance import PracticeGuidance

        if self._session is None or not isinstance(item, PracticeGuidance) or not PracticeCatalogue.has(item.key):
            return None
        return self._session.practice(item.key)

    def _work_in_session(self, item, chose_format: bool) -> None:
        """The practice of this action's session works with item. The session was made for this action's call, so no
        other call sees the fidelity and format item works at."""
        practice = self._session_practice(item)
        if practice is None:
            return
        practice.guideline = item
        if not chose_format:
            practice.use_kept_format()

    def _inside(self, action_type: type[GuidanceAction], guidance: str | list | None = None) -> GuidanceAction:
        """An action of action_type started inside this one: made for this action's session and working on guidance,
        this action's text or some of its listed Guidance, or on everything this action works on when guidance is
        none. It works on the same objects, so the session's practices stay the ones this action listed."""
        inner = action_type(session=self._session)
        inner._work_on_listed(
            guidance if guidance is not None else self._guidance_text if self._guidance_text is not None else self.listed()
        )
        return inner

    def each(self, operation: Callable[[Any], Any]) -> list:
        """Run ``operation`` once on a guidance string, or once per Guidance."""
        text = self._guidance_text
        if text is not None:
            return [operation(text)]
        return [operation(item) for item in self.listed()]

    def run(self, operation: Callable[[Any], Any], *, action: str = "") -> list:
        """Run ``operation`` on the guidance this action works on: once on its string, or once per Guidance."""
        self._keep_named_formats()
        self._log_running_action(action)
        try:
            return self.each(operation)
        except BaseException as failure:
            if self._session is not None:
                self._session.log.failure(failure, tool=action or type(self).__name__)
            raise

    def _keep_named_formats(self) -> None:
        """Save the format each listed guidance named on its fidelity in this action's session, so the next action on
        that fidelity, such as the validate that follows a generate, works in it without being told again."""
        for item, raw in zip(self.listed(), self._tool_items):
            practice = self._session_practice(item) if self._names_format(raw) else None
            if practice is not None:
                practice.keep_format()

    def _log_running_action(self, action: str) -> None:
        """Session trail for this run — override on actions such as Validate that log differently."""
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
        root = session.root.as_posix()
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
        action = self.for_call(ToolCall(payload.tool_input, payload.project))
        parts, labels = action._listed_inject_parts(payload)
        if not parts:
            return {}
        return {"additional_context": "\n\n".join(parts), "toast": rules_toast(Name(type(self).__name__).kebab, labels)}

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
