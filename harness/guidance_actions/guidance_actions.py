"""First-order guidance-action prelude: an action made for its call's session runs an operation on the guidance the call
names."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.name import Name
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.practice_catalogue import PracticeCatalogue
from tools.prompt_notify.prompt_notify import PromptNotify, Toast
from harness.hooks.hooks import Hook

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload
    from space.session.session import PracticeSessionOutput, Session


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
_SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
# What an action works on before it names any guidance; None cannot stand for it, since naming None keeps what it had.
_NOTHING_WORKED_ON = object()
PATHS_NOTE = (
    "paths: a file, a list of files, or a folder. Pass paths on an MCP call. "
    "This action reads them locally. Leave the document body out of the call."
)


def load_document(content: str = "", paths: list[str] | str | None = None) -> str:
    """The in-process text, or the files at paths. Paths win."""
    if paths in ("", None, []):
        return content or ""
    entries = [paths] if isinstance(paths, str) else list(paths)
    return "\n\n".join(_read_entry(Path(entry)) for entry in entries)


def source_label(content: str = "", paths: list[str] | str | None = None) -> str:
    """The path names for an instruction. The file bodies stay on disk."""
    if paths in ("", None, []):
        return content or ""
    if isinstance(paths, str):
        return paths
    return "\n".join(str(entry) for entry in paths)


def _read_entry(path: Path) -> str:
    if path.is_dir():
        files = [
            item
            for item in sorted(path.rglob("*"))
            if item.is_file() and not any(part in _SKIP_PARTS for part in item.parts)
        ]
        return "\n\n".join(
            item.read_text(encoding="utf-8", errors="replace") for item in files
        )
    return path.read_text(encoding="utf-8", errors="replace")


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

    def __init__(self, session: Session | None = None) -> None:
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
        in a ``session=`` word, else the session open in the call's project, else the session this action was made for."""
        guidance = call.arguments.get("guidance")
        action = self.made_for(self._session_named_in(guidance, call.project) or call.session or self._session)
        action._work_on(guidance)
        return action

    def made_for(self, session: Session | None) -> GuidanceAction:
        """An action of this kind, set up as this one is, made for session."""
        return type(self)(session=session)

    def session_for(self, call: ToolCall) -> Session | None:
        """The session this action logs call in: the one it was made for."""
        return self._session

    @property
    def session(self) -> Session:
        """The session this action works in."""
        if self._session is None:
            raise ActionWorksInNoSession(type(self).__name__)
        return self._session

    def _session_named_in(self, guidance: Any, project: Path | None) -> Session | None:
        """The session whose session.json guidance names in a ``session=`` word, a path from the project or an absolute
        one; none when it names none."""
        if not isinstance(guidance, str):
            return None
        named = next((word[len(_SESSION_WORD):] for word in guidance.split() if word.startswith(_SESSION_WORD)), "")
        return self._session_kept_in(Path(named), project) if named else None

    def _session_kept_in(self, session_file: Path, project: Path | None) -> Session:
        # WHY: space sits above the framework, so sessions are imported when an action first needs one.
        from space.repo.repo import Repo
        from space.session.session import Session, SessionNotFoundError

        found = session_file if session_file.is_absolute() or project is None else project / session_file
        if not found.is_file():
            raise SessionNotFoundError(str(session_file))
        return Session.load(found.parent, project or Repo(found.parent).checkout_folder)

    def _discover_operations(self) -> dict[str, AgentOperation]:
        from harness.agent_tools.agent_tools import AgentToolMark, GuidanceAgentOperation

        discovered: dict[str, AgentOperation] = {}
        for name, member in self._marked_members(type(self)):
            if AgentToolMark.marks(member):
                discovered[name] = GuidanceAgentOperation(
                    name=name,
                    callable=self._bound_callable(name, member),
                    toolset=self,
                )
        return discovered

    def _work_on(self, guidance: GuidanceArg | None = None) -> None:
        """Guidance ref or dict: iterate Guidance. Other strings: run once on that text. Naming again what this action
        already works on keeps the Guidance it built, so its operations all work on the same objects."""
        if guidance is None or guidance == self._guidance_worked_on:
            return
        self._guidance_worked_on = guidance
        self._listed_items = None
        listed = self._as_guidance_item(guidance)
        if listed is not None and not isinstance(guidance, list):
            self._guidance_text = None
            self._tool_items = [listed]
            return
        if isinstance(guidance, str):
            self._work_on_text(guidance)
            return
        self._guidance_text = None
        items = []
        for item in list(guidance or []):
            listed = self._as_guidance_item(item)
            items.append(item if listed is None else listed)
        self._tool_items = items

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

    def _work_on_text(self, text: str) -> None:
        """Agents on MCP often send several slugs, a ``format=`` word, and a ``session=`` word in one string; list the
        slugs as Guidance. The session word chose the session this action was made for. Any other word keeps the whole
        string as text, so prose still runs once."""
        refs = self._slug_words(text)
        if refs:
            self._guidance_text = None
            self._tool_items = refs
            return
        self._guidance_text = text
        self._tool_items = []

    def _slug_words(self, text: str) -> list:
        words = [word for word in text.split() if not word.startswith(_SESSION_WORD)]
        formats = [word[len(_FORMAT_WORD):].split(",")[0] for word in words if word.startswith(_FORMAT_WORD)]
        slugs = [slug for word in words if not word.startswith(_FORMAT_WORD) for slug in word.split(",") if slug]
        refs = [self._guidance_slug(slug) for slug in slugs]
        if not refs or None in refs:
            return []
        if not formats or not formats[0]:
            return refs
        return [self._with_format(ref, formats[0]) for ref in refs]

    def _with_format(self, ref: str | dict[str, Any], format: str) -> dict[str, Any]:
        item = dict(ref) if isinstance(ref, dict) else {"toolset": ref}
        item["format"] = format
        return item

    def _as_guidance_item(self, item: Any) -> Any:
        if isinstance(item, dict):
            return item
        if not isinstance(item, str):
            return item
        text = item.strip()
        if text.startswith("{") and text.endswith("}"):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, dict) and parsed.get("toolset"):
                return parsed
        if _TOOLSET_REF.match(text):
            return text
        return self._guidance_slug(text)

    def _guidance_slug(self, text: str) -> str | dict[str, Any] | None:
        if not _GUIDANCE_SLUG.match(text):
            return None
        return PracticeCatalogue.toolset_ref(text)

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

    def _session_practice(self, item) -> PracticeSessionOutput | None:
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

    def each(self, operation):
        """Run ``operation`` once on a guidance string, or once per Guidance."""
        text = self._guidance_text
        if text is not None:
            return [operation(text)]
        return [operation(item) for item in self.listed()]

    def run(self, operation, *, action: str = "") -> list:
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
        project = session.repo_from_session().as_posix()
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
    @Hook("postToolUse")
    def inject_rules(self, payload: HookPayload) -> dict[str, Any]:
        """Inject listed Guidance rules markdown after this action returns."""
        if type(self).__name__ == "Document" or not self._payload_is_this_action(payload):
            return {}
        action = self.for_call(ToolCall(payload.tool_input, payload.project))
        parts, labels = action._listed_inject_parts(payload)
        if not parts:
            return {}
        echo = PromptNotify()
        echo.toast_roots = payload.workspace_roots
        echo.show_ide_toast(PromptNotify().inject_rules_toast(Name(type(self).__name__).kebab, labels))
        return {"additional_context": "\n\n".join(parts)}

    def _listed_inject_parts(self, payload: HookPayload) -> tuple[list[str], list[str]]:
        parts: list[str] = []
        labels: list[str] = []
        for guidance in self.listed():
            text = self._listed_guidance_rules(guidance, payload)
            if not text:
                continue
            parts.append(text)
            labels.append(type(guidance).__name__)
        return parts, labels

    def _listed_guidance_rules(self, guidance: Any, payload: HookPayload) -> str:
        rules = getattr(guidance, "rules", None)
        if rules is None:
            return ""
        globbed = getattr(rules, "inject_rules", None)
        if Hook.disabled_on(globbed):
            return ""
        if callable(globbed):
            text = (globbed(payload).get("additional_context") or "").strip()
            if text:
                return text
        return (getattr(rules, "markdown", None) or "").strip()

    def _payload_is_this_action(self, payload: HookPayload) -> bool:
        tool = payload.tool_name.lower()
        if not tool:
            return False
        name = Name(type(self).__name__)
        aliases = {name.snake, name.kebab, "".join(name.words)}
        return any(alias and alias in tool for alias in aliases)
