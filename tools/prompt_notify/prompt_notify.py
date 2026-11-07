"""
Prompt notify hook — detect CDD action, practice, fidelity, and guideline use.

Fires on preToolUse. Matches MCP names (`sketch.sketch`, `bdd-behavior()`),
CallMcpTool wrappers, and skill/rule paths.

Off when the class is annotated ``@Hooks(disabled=True)``.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import ClassVar

# The CDD checkout this hook runs from: its installed toolsets are the code the hook server runs, so their @Toast annotations
# are read from here whichever project the event came from.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]

from harness.agent_tools.agent_tools import agent_toolset
from harness.name.name import Name
from harness.installation.destination import noCatalog
from harness.annotations.annotation import Toast
from harness.hooks.hook_server import TOAST_ARROW, HookPayload, HookServer, rules_toast
from harness.hooks.hooks import hook
from space.session.session_log import SessionLog

TOAST_NOTICE = ".cursor/prompt-notify-toast.json"
IDE_TOAST_EXTENSION = "cdd.prompt-notify-0.0.1"
_SKIP_BEGIN_FALLBACK = frozenset({"open_workspace", "end", "begin"})
_SAME_BURST_SECONDS = 2
_SKILL_DIRS = ("/.cursor/skills/", "/.claude/skills/")
_RULE_DIRS = ("/.cursor/rules/", "/.claude/rules/")


@noCatalog
@agent_toolset
class PromptNotify:
    """Echo detected action, practice, fidelity, and guideline names on preToolUse."""

    _catalog: ClassVar[list[tuple[str, str]] | None] = None
    _installed_extension: ClassVar[Path | None] = None

    # Each hook event is handled by the hook server's one instance, so nothing about one event is kept on it: two
    # events at once would read each other's values.

    @property
    def catalog(self) -> list[tuple[str, str]]:
        """Every name a tool call can mention, longest first, with its kind: each practice and fidelity CDD has, each
        practice rule file, and each operation an action publishes as a skill. Read from the practice catalogue and the
        action folders once per process, so a toast names only what exists."""
        if type(self)._catalog is None:
            found = {**self._practice_names(), **self._action_names()}
            type(self)._catalog = sorted(found.items(), key=lambda item: len(item[0]), reverse=True)
        return type(self)._catalog

    def _practice_names(self) -> dict[str, str]:
        """Each practice's slug, each fidelity's slug, and each practice rule file's name, which joins the two
        (``bdd-bdd-behavior``)."""
        from harness.guidance.practice_catalogue import PracticeCatalogue

        names: dict[str, str] = {}
        for practice in PracticeCatalogue.practices():
            names[practice.slug] = "practice"
            for fidelity in practice.fidelities:
                names[fidelity.slug] = "fidelity"
                names[f"{practice.slug}-{fidelity.slug}"] = "guideline"
        return names

    def _action_names(self) -> dict[str, str]:
        """Each action in the action catalogue, such as generate, grill, and create-rule."""
        from harness.guidance.action_catalogue import ActionCatalogue

        return {self._compact(name): "action" for name in ActionCatalogue.names()}

    @hook("preToolUse")
    def on_pre_tool_use(self, payload: HookPayload) -> dict:
        """Toast what the tool call uses in every workspace folder of the chat that made it."""
        self.install_ide_toast_extension()
        result = self.handle(payload, toolsets=self.echo_toolsets)
        message = result.get("user_message")
        if message:
            self.show_toast(str(message), payload.workspace_roots)
        return result

    def handle(self, payload: HookPayload, toolsets: list | None = None) -> dict:
        if not payload.tool_name:
            return {"permission": "allow"}
        detected = self._detected(payload, toolsets)
        if not detected:
            return {"permission": "allow"}
        kind, label = detected
        self._log_echo(payload.tool_name, kind, label)
        return {"permission": "allow", "user_message": f"{kind.title()}{TOAST_ARROW}{label}"}

    def detect_echo(
        self, payload: HookPayload, toolsets: list | None = None
    ) -> tuple[str, str] | None:
        invoked = self._mcp_tool_name(payload)
        if not invoked:
            return None
        searched = self._walk_toolsets(
            toolsets if toolsets is not None else self.echo_toolsets
        )
        for toolset in searched:
            found = self._echo_on_toolset(invoked, toolset)
            if found is not None:
                return found
        return None

    def detect(self, payload: HookPayload) -> tuple[str, str] | None:
        action_names = {self._mcp_tool_name(payload), payload.tool_name}
        return self._catalog_match(self._haystacks(payload), action_names)

    @cached_property
    def echo_toolsets(self) -> list:
        """The toolsets the CDD checkout defines, whose @Toast annotations say which tool calls toast; loaded once by the
        hook server's one notifier. A toolset that fails to load raises, so a broken toolset is seen rather than silently
        not toasting."""
        from harness.agent_tools.agent_tools import AgentToolSet
        from harness.installation.repository_toolsets import RepositoryToolsets

        return AgentToolSet.from_items(RepositoryToolsets(_CDD_CHECKOUT).collect())

    def show_toast(self, toast: str, workspace_roots: list[Path]) -> list[Path]:
        """Show toast in every workspace folder of the chat it is for, the toast files written. The hook server hands
        each hook's toast here, so a hook names its toast and never this notifier."""
        return self.show_ide_toast(toast, workspace_roots)

    def show_ide_toast(self, echo: str, workspace_roots: list[Path | str]) -> list[Path]:
        """Write echo as the toast of each workspace folder, joined with a toast written there in the same burst."""
        now = datetime.now(timezone.utc)
        return [ToastFile(folder).show(echo, now) for folder in self._toast_folders(workspace_roots)]

    def install_ide_toast_extension(self) -> Path:
        """Every preToolUse asks for this, so copy the tree once per process."""
        if type(self)._installed_extension is not None:
            return type(self)._installed_extension
        source = Path(__file__).resolve().parent / "ide_toast"
        dest = Path.home() / ".cursor" / "extensions" / IDE_TOAST_EXTENSION
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, dirs_exist_ok=True)
        type(self)._installed_extension = dest
        return dest

    def _detected(self, payload: HookPayload, toolsets: list | None) -> tuple[str, str] | None:
        if toolsets is not None:
            annotated = self.detect_echo(payload, toolsets=toolsets)
            if annotated:
                return annotated
        return self.detect(payload)

    def _log_echo(self, tool_name: str, kind: str, label: str) -> None:
        stamp = SessionLog.timestamp(datetime.now(timezone.utc))
        sys.stderr.write(f"{stamp} [prompt-notify] tool={tool_name} {kind}={label}\n")

    def _catalog_match(
        self, haystacks: list[str], action_names: set[str]
    ) -> tuple[str, str] | None:
        for hay in haystacks:
            posix = hay.replace("\\", "/").lower()
            in_skills = any(folder in posix for folder in _SKILL_DIRS)
            for token, kind in self.catalog:
                if not self._token_in(hay, token):
                    continue
                if kind == "action" and hay not in action_names:
                    continue
                if kind == "guideline" and in_skills:
                    # Rule tokens join folder and file (bdd-bdd-behavior); a skill path's
                    # nested folders can spell the same token without being a rule.
                    continue
                if "/rules/" in hay.replace("\\", "/").lower():
                    return "guideline", token
                return kind, token
        return None

    def _echo_on_toolset(self, invoked: str, toolset) -> tuple[str, str] | None:
        tools = getattr(toolset, "tools", None) or {}
        if not isinstance(tools, dict):
            return None
        match = next(
            (tool for tool in tools.values() if self._name_matches(invoked, tool)),
            None,
        )
        if match is None:
            return None
        if self._has_toast(match.callable):
            return self._echo_kind_label(match)
        if match.name == "instructions" and self._inherited_toast(toolset, "instructions"):
            return self._echo_kind_label(match)
        return self._begin_toast(match, tools, toolset)

    def _begin_toast(self, match, tools: dict, toolset) -> tuple[str, str] | None:
        """The action toast of a toolset whose begin step is annotated, for a tool of that toolset that is not annotated."""
        begin = tools.get("begin")
        if begin is None or match.name in _SKIP_BEGIN_FALLBACK:
            return None
        if not self._has_toast(begin.callable):
            return None
        return "action", Name(str(getattr(toolset, "slug", match.name))).kebab

    def _toast_folders(self, workspace_roots: list[Path | str]) -> list[Path]:
        """Each workspace folder once, as Windows names it when Cursor sends `/c:/...`."""
        folders = [self._workspace_root(root) for root in workspace_roots]
        return list({folder.resolve(): folder for folder in folders}.values())

    def _workspace_root(self, root: object) -> Path:
        text = str(root).strip().replace("\\", "/")
        slash_drive = re.match(r"^/+([A-Za-z]):/(.*)$", text)
        if slash_drive is not None and sys.platform == "win32":
            text = f"{slash_drive.group(1)}:/{slash_drive.group(2)}"
        return Path(text)

    def _compact(self, text: str) -> str:
        return Name(text).kebab

    def _mcp_tool_name(self, payload: HookPayload) -> str:
        name = payload.tool_name
        inp = payload.tool_input
        nested = inp.get("toolName") or inp.get("tool_name") or inp.get("name")
        if isinstance(nested, str) and nested.strip():
            if "mcp" in name.lower() or name in {"CallMcpTool", "call_mcp_tool"}:
                return nested.strip()
            if "." in nested or "-" in nested:
                return nested.strip()
        return name

    def _paths(self, payload: HookPayload) -> list[str]:
        inp = payload.tool_input
        found: list[str] = []
        for key in ("path", "file_path", "command"):
            value = inp.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value)
        return found

    def _haystacks(self, payload: HookPayload) -> list[str]:
        values = [self._mcp_tool_name(payload), payload.tool_name]
        for path in self._paths(payload):
            if self._skill_or_rule_path(path):
                values.append(path)
        return [item for item in values if item]

    def _skill_or_rule_path(self, path: str) -> bool:
        posix = path.replace("\\", "/").lower()
        return any(folder in posix for folder in _SKILL_DIRS + _RULE_DIRS)

    def _token_in(self, hay: str, token: str) -> bool:
        compacted_hay = f"-{self._compact(hay)}-"
        compacted_token = f"-{self._compact(token)}-"
        return compacted_token in compacted_hay

    def _has_toast(self, operation) -> bool:
        target = operation.fget if isinstance(operation, property) else operation
        inner = getattr(target, "__func__", target)
        return Toast.annotates(inner) or Toast.annotates(target)

    def _echo_kind_label(self, tool) -> tuple[str, str]:
        toolset = tool.toolset
        if tool.name == "instructions":
            if getattr(toolset, "practice_guidance", None) is not None:
                return "fidelity", tool.slug
            return "practice", getattr(toolset, "slug", tool.name)
        if tool.name == "begin":
            return "action", getattr(toolset, "slug", tool.name)
        return "action", Name(tool.name).kebab

    def _inherited_toast(self, toolset, name: str) -> bool:
        for cls in type(toolset).mro():
            member = cls.__dict__.get(name)
            if member is None:
                continue
            target = member.fget if isinstance(member, property) else member
            if self._has_toast(target):
                return True
        return False

    def _mcp_aliases(self, tool) -> set[str]:
        toolset = tool.toolset
        slug = str(getattr(toolset, "slug", "") or "")
        names = {f"{slug}.{tool.name}", f"{slug}_{tool.name}", tool.name}
        if getattr(toolset, "practice_guidance", None) is not None:
            names.add(tool.slug)
        if tool.name == "instructions" and slug:
            names.add(slug)
            names.add(f"{slug}.instructions")
        return {item for item in names if item}

    def _name_matches(self, invoked: str, tool) -> bool:
        compact_invoked = self._compact(invoked)
        return any(self._compact(name) == compact_invoked for name in self._mcp_aliases(tool))

    def _walk_toolsets(self, toolsets: list) -> list:
        found: list = []
        for toolset in toolsets:
            found.append(toolset)
            for child in getattr(toolset, "child_toolsets", lambda: ())():
                found.append(child)
        return found


class ToastFile:
    """The toast notice of one workspace folder, ``.cursor/prompt-notify-toast.json``, which the IDE toast extension
    shows. A toast written within a moment of the last one joins it, so a burst of tool calls shows as one toast."""

    def __init__(self, folder: Path) -> None:
        self.path = Path(folder) / TOAST_NOTICE

    def show(self, message: str, now: datetime) -> Path:
        """Write message as this folder's toast, joined with the toast already there when it is from the same burst."""
        notice = {"message": self._joined_with_previous(message, now), "at": SessionLog.timestamp(now)}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(notice, ensure_ascii=False) + "\n", encoding="utf-8")
        return self.path

    def _joined_with_previous(self, message: str, now: datetime) -> str:
        previous = self._previous()
        earlier = str(previous.get("message") or "")
        shown_at = self._time_of(str(previous.get("at") or ""))
        if not earlier or shown_at is None or abs((now - shown_at).total_seconds()) > _SAME_BURST_SECONDS:
            return message
        if self._is_rules_notice(earlier) and self._is_rules_notice(message):
            return earlier if message in earlier else f"{earlier}\n\n{message}"
        return self._join_arrow_toasts(earlier, message)

    def _previous(self) -> dict:
        """The toast shown here last; none when there is none or it was torn by a write still in progress."""
        if not self.path.is_file():
            return {}
        try:
            previous = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return previous if isinstance(previous, dict) else {}

    def _time_of(self, stamp: str) -> datetime | None:
        try:
            return datetime.fromisoformat(stamp)
        except ValueError:
            return None

    def _is_rules_notice(self, text: str) -> bool:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return bool(lines) and all(line.startswith("rules injected") for line in lines)

    def _is_rules_rest(self, rest: str) -> bool:
        lowered = rest.strip().lower()
        return lowered.startswith("rules :") or lowered.startswith("rules:")

    def _guidance_names(self, rest: str) -> list[str]:
        """The guidance names after a toast's arrow, such as `clean engineering code` from `rules : clean engineering
        code rules`."""
        text = rest.strip()
        if self._is_rules_rest(text):
            text = text.split(":", 1)[1]
        names = [chunk.strip().removesuffix(" rules").strip() for chunk in text.split(",")]
        return list(dict.fromkeys(name for name in names if name))

    def _join_arrow_toasts(self, previous: str, incoming: str) -> str:
        if incoming in previous:
            return previous
        if TOAST_ARROW not in previous or TOAST_ARROW not in incoming:
            return f"{previous}; {incoming}"
        previous_source, previous_rest = previous.split(TOAST_ARROW, 1)
        incoming_source, incoming_rest = incoming.split(TOAST_ARROW, 1)
        if previous_source.strip() != incoming_source.strip() or not self._is_rules_rest(previous_rest) or not self._is_rules_rest(incoming_rest):
            return f"{previous}; {incoming}"
        names = list(dict.fromkeys(self._guidance_names(previous_rest) + self._guidance_names(incoming_rest)))
        return rules_toast(previous_source.strip(), names)


HookServer.show_toasts_with(PromptNotify().show_toast)
