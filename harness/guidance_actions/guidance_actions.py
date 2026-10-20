"""First-order guidance-action prelude — bind guidance, then run the operation."""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any, NotRequired, TypedDict

from harness.agent_tools import AgentToolSet, agent_instructions, agent_toolset, tools
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
_SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__"}
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


def listed(action) -> list:
    """Instantiate Guidance bound on ``action._tool_items`` for guidance-action recipe bodies."""
    if getattr(action, "_guidance_text", None) is not None:
        return []
    raw = getattr(action, "_tool_items", None) or []
    return AgentToolSet.instantiate_all(raw)


@agent_toolset
class GuidanceAction:
    """Bind guidance and run an operation on that string or each listed Guidance."""

    def __init__(self) -> None:
        super().__init__()
        self._guidance_text: str | None = None
        self._tool_items: list = []

    def _bind_guidance(self, guidance: GuidanceArg | None = None) -> None:
        """Guidance ref or dict: iterate Guidance. Other strings: run once on that text."""
        if guidance is None:
            return
        bound = self._as_guidance_item(guidance)
        if bound is not None and not isinstance(guidance, list):
            self._guidance_text = None
            self._tool_items = [bound]
            return
        if isinstance(guidance, str):
            self._guidance_text = guidance
            self._tool_items = []
            return
        self._guidance_text = None
        items = []
        for item in list(guidance or []):
            bound = self._as_guidance_item(item)
            items.append(item if bound is None else bound)
        self._tool_items = items

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
        """Return the Guidance bound on this run from the guidance argument."""
        return listed(self)

    def each(self, operation):
        """Run ``operation`` once on a guidance string, or once per Guidance."""
        text = self._guidance_text
        if text is not None:
            return [operation(text)]
        return [operation(item) for item in self.listed()]

    def run(self, guidance: GuidanceArg, operation, *, action: str = "") -> list:
        """Bind guidance and run ``operation`` on the string or each Guidance."""
        self._bind_guidance(guidance)
        self._log_running_action(action)
        # self.begin(guidance, action=action)
        results = self.each(operation)
        return results

    def _log_running_action(self, action: str) -> None:
        if not action:
            return
        from space.session import Session

        session = Session.current()
        if session is None or session.session_path is None:
            return
        items = self.listed() if self._guidance_text is None else []
        session.log_guidance_action(action, items)

    @echo
    @agent_instructions
    def begin(self, guidance: GuidanceArg | None = None, action: str = "") -> str:
        """Start a guidance action: open the workspace if needed, attach this action to the session turn, and load decision records. A session is optional — the action still runs without one. Follow act_quickly."""
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
        action = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", type(self).__name__).lower()
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
        if getattr(globbed, "_hook_disabled", False):
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
        name = type(self).__name__
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        aliases = {name.lower(), snake, snake.replace("_", "-"), snake.replace("_", "")}
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
