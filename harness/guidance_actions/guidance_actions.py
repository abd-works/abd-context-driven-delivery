"""First-order guidance-action prelude — bind guidance, then run the operation."""

from __future__ import annotations

import inspect
import json
import re
import threading
from pathlib import Path
from typing import Any, NotRequired, TypedDict

from harness.agent_tools import AgentOperation, AgentToolSet, agent_instructions, agent_toolset, tools
from harness.agent_tools.name import Name
from prompt_notify.prompt_notify import PromptNotify, echo
from harness.hooks.hooks import Hook

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
# What a call has bound before it binds any guidance; None cannot stand for it, since binding None keeps the binding.
_NOTHING_BOUND = object()
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


@agent_toolset
class GuidanceAction:
    """Bind guidance and run an operation on that string or each listed Guidance.

    The MCP server runs calls on several threads against one action, so what a call is working on
    is kept per thread: two calls at once must each answer for their own guidance.

    An action works in one session. An action started inside another is made for that action's session; a board
    command names its ticket's session in a ``session=`` word; any other call works in the chat's current session.

    A call binds the guidance it works on once, when it starts; the action's operations then read it from the action
    through ``listed()``, so each practice it lists is one object, the one its session holds.
    """

    def __init__(self, session: Any = None) -> None:
        super().__init__()
        self._running = threading.local()
        self._made_for = session

    # The guidance argument this call bound, so binding the same argument again in the same call keeps what it built.
    @property
    def _bound_guidance(self) -> Any:
        return getattr(self._running, "bound_guidance", _NOTHING_BOUND)

    @_bound_guidance.setter
    def _bound_guidance(self, guidance: Any) -> None:
        self._running.bound_guidance = guidance

    @property
    def _guidance_text(self) -> str | None:
        return getattr(self._running, "guidance_text", None)

    @_guidance_text.setter
    def _guidance_text(self, text: str | None) -> None:
        self._running.guidance_text = text

    @property
    def _tool_items(self) -> list:
        return getattr(self._running, "tool_items", [])

    @_tool_items.setter
    def _tool_items(self, items: list) -> None:
        self._running.tool_items = items

    @property
    def _logged_session_action(self) -> str | None:
        return getattr(self._running, "logged_session_action", None)

    @_logged_session_action.setter
    def _logged_session_action(self, action: str | None) -> None:
        self._running.logged_session_action = action

    # The session.json a command's session= word named, a path from the project; empty when it named none.
    @property
    def _named_session_file(self) -> str:
        return getattr(self._running, "named_session_file", "")

    @_named_session_file.setter
    def _named_session_file(self, path: str) -> None:
        self._running.named_session_file = path
        self._running.session = None

    @property
    def _listed_items(self) -> list | None:
        return getattr(self._running, "listed_items", None)

    @_listed_items.setter
    def _listed_items(self, items: list | None) -> None:
        self._running.listed_items = items

    @property
    def session(self):
        """The session this action works in: the session.json a command's session= word named, else the session it was
        made for, else the chat's current session. A board command names its ticket's session, which need not be the
        session open in the chat that runs it."""
        found = getattr(self._running, "session", None)
        if found is None:
            found = self._session_to_work_in()
            self._running.session = found
        return found

    def _session_to_work_in(self):
        from space.session import Session

        if self._named_session_file:
            return Session.from_file(self._named_session_file)
        return self._made_for if self._made_for is not None else Session.current()

    def start_call(self) -> None:
        """Begin a new call: one action object serves every call while the MCP server runs, so a call starts with no
        guidance bound, no session found, and no line logged, rather than with the last call's."""
        self._logged_session_action = None
        self._bound_guidance = _NOTHING_BOUND
        self._named_session_file = ""
        self._guidance_text = None
        self._tool_items = []
        self._listed_items = None

    def call_session(self, arguments: dict[str, Any]):
        """The session a call with arguments works in, once it has bound their guidance: a board command names its
        ticket's session in its guidance, which the call's log line belongs in."""
        if "guidance" in arguments:
            self._bind_guidance(arguments.get("guidance"))
        return self.session

    def session_action_for_operation(self, operation: str) -> str:
        """MCP operation name → session action name (``run`` uses the same string)."""
        return operation

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

    def _bind_guidance(self, guidance: GuidanceArg | None = None) -> None:
        """Guidance ref or dict: iterate Guidance. Other strings: run once on that text. Binding what this call already
        bound keeps the Guidance it built, so a call's operations all work on the same objects."""
        if guidance is None or guidance == self._bound_guidance:
            return
        self._bound_guidance = guidance
        self._named_session_file = ""
        self._listed_items = None
        bound = self._as_guidance_item(guidance)
        if bound is not None and not isinstance(guidance, list):
            self._guidance_text = None
            self._tool_items = [bound]
            return
        if isinstance(guidance, str):
            self._bind_guidance_string(guidance)
            return
        self._guidance_text = None
        items = []
        for item in list(guidance or []):
            bound = self._as_guidance_item(item)
            items.append(item if bound is None else bound)
        self._tool_items = items

    def _bind_guidance_string(self, text: str) -> None:
        """Agents on MCP often send several slugs, a ``format=`` word, and a ``session=`` word in one string; list the
        slugs as Guidance and keep the session. Any other word keeps the whole string as text, so prose still runs once."""
        refs = self._slug_words(text)
        if refs:
            self._guidance_text = None
            self._tool_items = refs
            self._named_session_file = next((word[len(_SESSION_WORD):] for word in text.split() if word.startswith(_SESSION_WORD)), "")
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
        return GuidanceCatalog.ref_for(text)

    def guidance_text(self) -> str | None:
        """The string to run this action on, when guidance was not a Guidance list."""
        return self._guidance_text

    def listed(self) -> list:
        """The Guidance bound on this run, each practice worked on in this action's session: its practice adopts it,
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

    def _session_practice(self, item):
        """The practice item is, as this action's session holds it; none when item is no practice CDD has."""
        from harness.guidance.guidance import PracticeGuidance
        from harness.guidance.practice_catalogue import PracticeCatalogue

        if not isinstance(item, PracticeGuidance) or not PracticeCatalogue.has(item.key):
            return None
        return self.session.practice(item.key)

    def _work_in_session(self, item, chose_format: bool) -> None:
        practice = self._session_practice(item)
        if practice is None:
            return
        practice.guideline = item
        if not chose_format:
            practice.use_kept_format()

    def _inside(self, action_type: type, guidance: str | list | None = None):
        """An action of action_type started inside this one: made for this action's session and working on guidance,
        this action's text or some of its listed Guidance, or on everything this action works on when guidance is
        none. It works on the same objects, so the session's practices stay the ones this action listed."""
        inner = action_type(self.session)
        worked_on = guidance if guidance is not None else self._guidance_text if self._guidance_text is not None else self.listed()
        inner._bound_guidance = worked_on
        if isinstance(worked_on, str):
            inner._guidance_text = worked_on
            inner._tool_items = []
        else:
            inner._guidance_text = None
            inner._tool_items = list(worked_on)
            inner._listed_items = list(worked_on)
        return inner

    def each(self, operation):
        """Run ``operation`` once on a guidance string, or once per Guidance."""
        text = self._guidance_text
        if text is not None:
            return [operation(text)]
        return [operation(item) for item in self.listed()]

    def run(self, operation, *, action: str = "") -> list:
        """Run ``operation`` on the guidance this call bound: once on its string, or once per Guidance."""
        self._keep_named_formats()
        self._log_running_action(action)
        try:
            return self.each(operation)
        except BaseException as failure:
            self.session.record_failure(failure, tool=action or type(self).__name__)
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
        if not action:
            return
        if self._logged_session_action == action:
            return
        self._logged_session_action = action
        self.listed()
        self.session.log_guidance_action(action)

    @echo
    @agent_instructions
    def begin(self, guidance: GuidanceArg | None = None, action: str = "") -> str:
        """Start a guidance action: open the workspace if needed, attach this action to the session turn, and load decision records. With no named session the action runs in the main session. Follow act_quickly."""
        self._bind_guidance(guidance)
        tools(self.act_quickly)
        return ""
        # warning = ""
        # session = self.workspace.current_work_session
        # if session is not None:
        #     try:
        #         session.turn
        #         if action:
        #             session.turn.action = action
        #     except (AttributeError, TypeError):
        #         pass
        #     if not warning:
        #         warning = session.branch_warning()
        # return warning

    @property
    def session_context(self) -> str:
        """The open session as an agent acting on this command needs it: its session.json, the project root paths
        are named from, the session's root, and where each listed practice writes. The agent works from the project's
        checkout, so every path it sees starts there; told nothing, it guesses where files go under a moved root."""
        session = self.session
        if session.session_path is None:
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

    @echo
    @Hook("postToolUse")
    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Inject listed Guidance rules markdown after this action returns."""
        if type(self).__name__ == "Document":
            return {}
        data = payload or {}
        if not self._payload_is_this_action(data):
            return {}
        self._bind_guidance_from_payload(data)
        parts, labels = self._listed_inject_parts(data)
        if not parts:
            return {}
        body = "\n\n".join(parts)
        action = Name(type(self).__name__).kebab
        echo = PromptNotify()
        echo.toast_roots = data.get("workspace_roots")
        echo.show_ide_toast(
            PromptNotify().inject_rules_toast(action, labels),
        )
        return {"additional_context": body}

    def _listed_inject_parts(self, data: dict[str, Any]) -> tuple[list[str], list[str]]:
        parts: list[str] = []
        labels: list[str] = []
        for guidance in self.listed():
            text = self._listed_guidance_rules(guidance, data)
            if not text:
                continue
            parts.append(text)
            labels.append(type(guidance).__name__)
        return parts, labels

    def _listed_guidance_rules(self, guidance: Any, data: dict[str, Any]) -> str:
        rules = getattr(guidance, "rules", None)
        if rules is None:
            return ""
        globbed = getattr(rules, "inject_rules", None)
        if Hook.disabled_on(globbed):
            return ""
        if callable(globbed):
            text = (globbed(data).get("additional_context") or "").strip()
            if text:
                return text
        return (getattr(rules, "markdown", None) or "").strip()

    def _payload_is_this_action(self, payload: dict[str, Any]) -> bool:
        tool = str(payload.get("tool_name") or "").lower()
        if not tool:
            return False
        name = Name(type(self).__name__)
        aliases = {name.snake, name.kebab, "".join(name.words)}
        return any(alias and alias in tool for alias in aliases)

    def _bind_guidance_from_payload(self, payload: dict[str, Any]) -> None:
        raw = payload.get("tool_input") or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raw = {}
        if not isinstance(raw, dict):
            return
        if "guidance" in raw:
            self._bind_guidance(raw.get("guidance"))


class GuidanceCatalog:
    """Map a practice or fidelity slug to the toolset ref an action can list."""

    _refs: dict[str, str | dict[str, Any]] | None = None

    @classmethod
    def ref_for(cls, slug: str) -> str | dict[str, Any] | None:
        cls._load()
        return (cls._refs or {}).get(slug)

    @classmethod
    def _load(cls) -> None:
        if cls._refs is not None:
            return
        from harness.installation.installer import Installer
        from harness.agent_tools.agent_tools import AgentToolSet

        installer = Installer()
        refs: dict[str, str | dict[str, Any]] = {}
        practices = installer.repo / "cdd_guidance" / "practices"
        for py_file in installer._iter_collect_files(practices):
            for ref in installer._toolset_refs_in_file(py_file, installer.repo):
                cls._index_ref(refs, ref, AgentToolSet)
        cls._refs = refs

    @classmethod
    def _index_ref(cls, refs: dict[str, str | dict[str, Any]], ref: str, toolsets: Any) -> None:
        try:
            practice = toolsets.instantiate(ref)
        except (ImportError, ModuleNotFoundError, TypeError, ValueError, AttributeError, OSError):
            return
        fidelities = getattr(getattr(practice, "fidelities", None), "entries", None)
        if not isinstance(fidelities, dict) or not fidelities:
            return
        slug = str(getattr(practice, "slug", "") or "")
        if slug and slug not in refs:
            refs[slug] = ref
        for name, child in fidelities.items():
            fidelity_ref = {"toolset": ref, "fidelity": name}
            child_slug = str(getattr(child, "slug", "") or "")
            if child_slug and child_slug not in refs:
                refs[child_slug] = fidelity_ref
            for alias in {name, name.replace("_", "-")}:
                if alias and alias not in refs:
                    refs[alias] = fidelity_ref
