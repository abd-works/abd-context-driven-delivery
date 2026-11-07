"""
Prompt notify hook — detect CDD action, practice, fidelity, and guideline use.

Fires on preToolUse. Matches MCP names (`sketch.sketch`, `bdd-behavior()`),
CallMcpTool wrappers, skill/rule paths, and legacy YAML `action:` fences.

Off when the class is annotated ``@Hooks(disabled=True)``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

_REPO_ROOT = Path(__file__).resolve().parents[2]

from harness.agent_tools.agent_tools import agent_toolset
from harness.name.name import Name
from harness.installation.destination import noCatalog
from harness.marks.mark import Toast
from harness.hooks.hook_server import TOAST_ARROW, HookPayload, HookServer, rules_toast
from harness.hooks.hooks import Hook

TOAST_NOTICE = ".cursor/prompt-notify-toast.json"
IDE_TOAST_EXTENSION = "cdd.prompt-notify-0.0.1"
_YAML_ACTION = re.compile(r"\baction:\s*([A-Za-z0-9_-]+)", re.I)
_SKIP_BEGIN_FALLBACK = frozenset({"open_workspace", "end", "begin"})
_SAME_BURST_SECONDS = 2
_SKILL_DIRS = ("/.cursor/skills/", "/.claude/skills/")
_RULE_DIRS = ("/.cursor/rules/", "/.claude/rules/")


@noCatalog
@agent_toolset
class PromptNotify:
    """Echo detected action, practice, fidelity, and guideline names on preToolUse."""

    _catalog: ClassVar[list[tuple[str, str]] | None] = None
    _echo_toolsets: ClassVar[list | None] = None
    _installed_extension: ClassVar[Path | None] = None

    def __init__(self, toast_roots: list[Path] | None = None) -> None:
        self.repo: Path | None = None
        self.toast_roots = toast_roots
        self.echo = ""
        self.toast_stamp = ""
        self._begin_tools: dict = {}
        self._begin_toolset = None
        self._toast_dest: Path | None = None

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

    @Hook("preToolUse")
    def on_pre_tool_use(self, payload: HookPayload) -> dict:
        """Toast what the tool call uses in every workspace folder of the chat that made it."""
        self.install_ide_toast_extension()
        result = self.handle(payload, toolsets=self.echo_toolsets())
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
            toolsets if toolsets is not None else self.echo_toolsets()
        )
        for toolset in searched:
            found = self._echo_on_toolset(invoked, toolset)
            if found is not None:
                return found
        return None

    def detect(self, payload: HookPayload) -> tuple[str, str] | None:
        named = self._yaml_action(payload)
        if named:
            return "action", named
        action_names = {self._mcp_tool_name(payload), payload.tool_name}
        return self._catalog_match(self._haystacks(payload), action_names)

    def echo_toolsets(self, repo: Path | None = None) -> list:
        if repo is None and type(self)._echo_toolsets is not None:
            return type(self)._echo_toolsets
        loaded = self._load_echo_toolsets(repo)
        if repo is None:
            type(self)._echo_toolsets = loaded
        return loaded

    @classmethod
    def show_toast(cls, toast: str, workspace_roots: list[Path]) -> Path:
        """Show toast in this checkout and in every workspace folder of the chat it is for. The hook server hands each
        hook's toast here, so a hook names its toast and never this notifier."""
        return cls(toast_roots=workspace_roots).show_ide_toast(toast)

    def show_ide_toast(self, echo: str) -> Path:
        dest = self._toast_path(self.repo)
        self._toast_dest = dest
        self.echo = echo
        self.toast_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message = self._burst_message()
        notice = json.dumps({"message": message, "at": self.toast_stamp}, ensure_ascii=False) + "\n"
        self._write_notice(dest, notice)
        for path in self._toast_destinations(dest):
            self._write_notice(path, notice)
        return dest

    def chat_edit_source(self, payload: HookPayload) -> str:
        """Name the chat that edited the file, so the toast is not shared across chats."""
        title = self._chat_title(payload)
        if not title:
            return "chat edit"
        return f"chat {title} edited file"

    def _chat_title(self, payload: HookPayload) -> str:
        for key in ("conversation_title", "composer_title", "chat_title", "title"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip() and not self._looks_like_path(value):
                return " ".join(value.split())
        named = self._composer_name(payload.conversation_id)
        if named:
            return named
        return self._title_from_transcript(str(payload.get("transcript_path") or ""))

    def _looks_like_path(self, text: str) -> bool:
        compact = " ".join(text.split())
        if compact.startswith("@") or "\\" in compact or "/" in compact:
            return True
        return Path(compact).suffix.lower() in {".md", ".py", ".ts", ".tsx", ".js", ".json"}

    def _composer_name(self, conversation_id: str) -> str:
        if not conversation_id:
            return ""
        db = self._cursor_state_db()
        if db is None or not db.is_file():
            return ""
        try:
            con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
            try:
                stored = con.execute(
                    "SELECT value FROM cursorDiskKV WHERE key = ?",
                    (f"composerData:{conversation_id}",),
                ).fetchone()
            finally:
                con.close()
        except (OSError, sqlite3.Error):
            return ""
        if not stored or stored[0] is None:
            return ""
        raw = stored[0]
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", "replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return ""
        name = data.get("name") if isinstance(data, dict) else ""
        if not isinstance(name, str) or not name.strip() or self._looks_like_path(name):
            return ""
        return " ".join(name.split())

    def _cursor_state_db(self) -> Path | None:
        override = getattr(self, "state_db", None)
        if isinstance(override, Path):
            return override
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        return Path(appdata) / "Cursor" / "User" / "globalStorage" / "state.vscdb"

    def _title_from_transcript(self, transcript_path: str) -> str:
        path = Path(transcript_path)
        if not transcript_path or not path.is_file():
            return ""
        try:
            first = path.open(encoding="utf-8").readline()
        except OSError:
            return ""
        match = re.search(r"<user_query>\s*(.*?)\s*</user_query>", first, re.DOTALL)
        text = match.group(1) if match else ""
        text = re.sub(r"\s+", " ", text).strip()
        if not text or self._looks_like_path(text):
            return ""
        if len(text) <= 60:
            return text
        shortened = text[:60].rsplit(" ", 1)[0]
        return shortened or text[:60]

    def toast_notice(self, echo: str) -> dict[str, str]:
        return {
            "message": echo,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

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
            marked = self.detect_echo(payload, toolsets=toolsets)
            if marked:
                return marked
        return self.detect(payload)

    def _log_echo(self, tool_name: str, kind: str, label: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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
        self._begin_tools = tools
        self._begin_toolset = toolset
        return self._begin_toast(match)

    def _begin_toast(self, match) -> tuple[str, str] | None:
        begin = self._begin_tools.get("begin")
        if begin is None or match.name in _SKIP_BEGIN_FALLBACK:
            return None
        if not self._has_toast(begin.callable):
            return None
        return "action", str(getattr(self._begin_toolset, "slug", match.name)).replace("_", "-")

    def _load_echo_toolsets(self, repo: Path | None) -> list:
        from harness.installer.installer import Installer
        from harness.agent_tools.agent_tools import AgentToolSet

        installer = Installer(repo=repo or _REPO_ROOT)
        return AgentToolSet.from_items(installer.toolsets.collect(), skip_errors=True)

    def _toast_path(self, repo: Path | None) -> Path:
        root = Path(repo) if repo is not None else _REPO_ROOT
        return root / TOAST_NOTICE

    def _write_notice(self, dest: Path, notice: str) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(notice, encoding="utf-8")

    def _workspace_root(self, root: object) -> Path:
        text = str(root).strip().replace("\\", "/")
        slash_drive = re.match(r"^/+([A-Za-z]):/(.*)$", text)
        if slash_drive is not None and sys.platform == "win32":
            text = f"{slash_drive.group(1)}:/{slash_drive.group(2)}"
        return Path(text)

    def _toast_destinations(self, primary: Path) -> list[Path]:
        seen = {primary.resolve()}
        extra: list[Path] = []
        for root in self.toast_roots or []:
            dest = self._workspace_root(root) / TOAST_NOTICE
            try:
                resolved = dest.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            seen.add(resolved)
            extra.append(dest)
        return extra

    def _burst_message(self) -> str:
        dest = self._toast_dest
        echo = self.echo
        stamp = self.toast_stamp
        if dest is None or not dest.is_file():
            return echo
        previous = self._read_toast(dest)
        prev_msg = str(previous.get("message") or "")
        prev_at = self._parse_toast_time(str(previous.get("at") or ""))
        now = self._parse_toast_time(stamp)
        if not prev_msg or prev_at is None or now is None:
            return echo
        if abs((now - prev_at).total_seconds()) > _SAME_BURST_SECONDS:
            return echo
        if self._rules_notice(prev_msg) and self._rules_notice(echo):
            if echo in prev_msg:
                return prev_msg
            return f"{prev_msg}\n\n{echo}"
        return self._join_arrow_toasts(prev_msg, echo)

    def _read_toast(self, dest: Path) -> dict:
        try:
            previous = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return {}
        return previous if isinstance(previous, dict) else {}

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

    def _yaml_action(self, payload: HookPayload) -> str | None:
        for text in self._paths(payload):
            match = _YAML_ACTION.search(text)
            if match:
                return match.group(1).replace("_", "-")
        return None

    def _has_toast(self, operation) -> bool:
        target = operation.fget if isinstance(operation, property) else operation
        inner = getattr(target, "__func__", target)
        return Toast.marks(inner) or Toast.marks(target)

    def _echo_kind_label(self, tool) -> tuple[str, str]:
        toolset = tool.toolset
        if tool.name == "instructions":
            if getattr(toolset, "practice_guidance", None) is not None:
                return "fidelity", tool.slug
            return "practice", getattr(toolset, "slug", tool.name)
        if tool.name == "begin":
            return "action", getattr(toolset, "slug", tool.name)
        return "action", tool.name.replace("_", "-")

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

    def _parse_toast_time(self, stamp: str) -> datetime | None:
        try:
            return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _rules_notice(self, text: str) -> bool:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return bool(lines) and all(line.startswith("rules injected") for line in lines)

    def _rules_rest(self, rest: str) -> bool:
        lowered = rest.strip().lower()
        return lowered.startswith("rules :") or lowered.startswith("rules:")

    def _guidance_names_from_toast_rest(self, rest: str) -> list[str]:
        text = rest.strip()
        lowered = text.lower()
        if lowered.startswith("rules :") or lowered.startswith("rules:"):
            text = text.split(":", 1)[1]
        names: list[str] = []
        for chunk in text.split(","):
            name = chunk.strip()
            if name.endswith(" rules"):
                name = name[: -len(" rules")].strip()
            if name and name not in names:
                names.append(name)
        return names

    def _join_arrow_toasts(self, previous: str, incoming: str) -> str:
        if incoming in previous:
            return previous
        if TOAST_ARROW not in previous or TOAST_ARROW not in incoming:
            return f"{previous}; {incoming}"
        prev_src, prev_rest = previous.split(TOAST_ARROW, 1)
        inc_src, inc_rest = incoming.split(TOAST_ARROW, 1)
        if prev_src.strip() != inc_src.strip() or not self._rules_rest(prev_rest) or not self._rules_rest(inc_rest):
            return f"{previous}; {incoming}"
        names: list[str] = []
        for name in self._guidance_names_from_toast_rest(
            prev_rest
        ) + self._guidance_names_from_toast_rest(inc_rest):
            if name not in names:
                names.append(name)
        return rules_toast(prev_src.strip(), names)


HookServer.show_toasts_with(PromptNotify.show_toast)
