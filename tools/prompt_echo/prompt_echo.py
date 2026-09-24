"""
Prompt echo hook — detect CDD action, practice, fidelity, and guideline use.

Fires on preToolUse. Matches MCP names (`sketch.sketch`, `bdd-behavior()`),
CallMcpTool wrappers, skill/rule paths, and legacy YAML `action:` fences.

Off when the class is annotated ``@Hooks(disabled=True)``.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.agent_tools import agent_toolset
from installation.destination import Destination
from harness.hooks.hooks import Hook


class Echo(Destination):
    """Mark an AgentOperation or AgentInstructions so PromptEcho toasts it."""

    flag = "_echo"

    def __new__(cls, operation=None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(operation):
            return inst.annotate(operation)
        return inst


echo = Echo

TOAST_NOTICE = ".cursor/prompt-echo-toast.json"
IDE_TOAST_EXTENSION = "cdd.prompt-echo-0.0.1"
_FALLBACK_ACTIONS = (
    "create-rule",
    "createRule",
    "document",
    "generate",
    "grill",
    "iterate",
    "partition",
    "render",
    "repair",
    "satisfy",
    "scan",
    "sketch",
    "validate",
)
_YAML_ACTION = re.compile(r"\baction:\s*([A-Za-z0-9_-]+)", re.I)
_SKIP_BEGIN_FALLBACK = frozenset({"open_workspace", "end", "begin"})
_ARROW = " \u2192 "
_SAME_BURST_SECONDS = 2


@agent_toolset
class PromptEcho:
    """Echo detected action, practice, fidelity, and guideline names on preToolUse."""

    _catalog: ClassVar[list[tuple[str, str]] | None] = None
    _echo_toolsets: ClassVar[list | None] = None

    def __init__(self) -> None:
        self.repo: Path | None = None
        self.toast_roots: list | None = None
        self.echo = ""
        self.toast_stamp = ""
        self.tool_name = ""
        self.echo_kind = ""
        self.echo_label = ""
        self.skill_kind = ""
        self.skill_found: dict[str, str] = {}
        self._begin_tools: dict = {}
        self._begin_toolset = None
        self._toast_dest: Path | None = None

    @property
    def catalog(self) -> list[tuple[str, str]]:
        if type(self)._catalog is not None:
            return type(self)._catalog
        found: dict[str, str] = {}
        skills = _REPO_ROOT / ".cursor" / "skills"
        self.skill_found = found
        self.skill_kind = "action"
        self._walk_skill_tree(skills / "actions")
        self.skill_kind = "practice"
        self._walk_skill_tree(skills / "practices")
        self._walk_rule_tree(_REPO_ROOT / ".cursor" / "rules" / "practices", found)
        for name in _FALLBACK_ACTIONS:
            found.setdefault(name.replace("_", "-"), "action")
        type(self)._catalog = sorted(found.items(), key=lambda item: len(item[0]), reverse=True)
        return type(self)._catalog

    @Hook("preToolUse")
    def on_pre_tool_use(self, hook_payload: dict) -> dict:
        self.install_ide_toast_extension()
        result = self.handle(hook_payload, toolsets=self.echo_toolsets())
        message = result.get("user_message")
        if message:
            self.show_ide_toast(str(message))
        return result

    def handle(self, hook_payload: dict, toolsets: list | None = None) -> dict:
        tool_name = hook_payload.get("tool_name", "")
        if not tool_name:
            return {"permission": "allow"}
        detected = self._detected(hook_payload, toolsets)
        if not detected:
            return {"permission": "allow"}
        kind, label = detected
        self.tool_name = str(tool_name)
        self.echo_kind = kind
        self.echo_label = label
        self._log_echo()
        return {"permission": "allow", "user_message": f"{kind.title()}{_ARROW}{label}"}

    def detect_echo(
        self, hook_payload: dict, toolsets: list | None = None
    ) -> tuple[str, str] | None:
        invoked = self._mcp_tool_name(hook_payload)
        if not invoked:
            return None
        hosts = self._walk_toolsets(
            toolsets if toolsets is not None else self.echo_toolsets()
        )
        for toolset in hosts:
            found = self._echo_on_toolset(invoked, toolset)
            if found is not None:
                return found
        return None

    def detect(self, hook_payload: dict) -> tuple[str, str] | None:
        named = self._yaml_action(hook_payload)
        if named:
            return "action", named
        invoked = self._mcp_tool_name(hook_payload)
        tool_name = str(hook_payload.get("tool_name") or "")
        action_names = {invoked, tool_name}
        return self._catalog_match(self._haystacks(hook_payload), action_names)

    def echo_toolsets(self, repo: Path | None = None) -> list:
        if repo is None and type(self)._echo_toolsets is not None:
            return type(self)._echo_toolsets
        loaded = self._load_echo_toolsets(repo)
        if repo is None:
            type(self)._echo_toolsets = loaded
        return loaded

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

    def inject_rules_toast(self, source: str, labels: list[str]) -> str:
        return f"{source}{_ARROW}rules : {', '.join(labels)}"

    def toast_notice(self, echo: str) -> dict[str, str]:
        return {
            "message": echo,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def install_ide_toast_extension(self) -> Path:
        source = Path(__file__).resolve().parent / "ide_toast"
        dest = Path.home() / ".cursor" / "extensions" / IDE_TOAST_EXTENSION
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, dirs_exist_ok=True)
        return dest

    def _detected(self, hook_payload: dict, toolsets: list | None) -> tuple[str, str] | None:
        if toolsets is not None:
            marked = self.detect_echo(hook_payload, toolsets=toolsets)
            if marked:
                return marked
        return self.detect(hook_payload)

    def _log_echo(self) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sys.stderr.write(
            f"{stamp} [prompt-echo] tool={self.tool_name} {self.echo_kind}={self.echo_label}\n"
        )

    def _catalog_match(
        self, haystacks: list[str], action_names: set[str]
    ) -> tuple[str, str] | None:
        for hay in haystacks:
            for token, kind in self.catalog:
                if not self._token_in(hay, token):
                    continue
                if kind == "action" and hay not in action_names:
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
        if self._has_echo(match.callable):
            return self._echo_kind_label(match)
        if match.name == "instructions" and self._inherited_echo(toolset, "instructions"):
            return self._echo_kind_label(match)
        self._begin_tools = tools
        self._begin_toolset = toolset
        return self._begin_echo(match)

    def _begin_echo(self, match) -> tuple[str, str] | None:
        begin = self._begin_tools.get("begin")
        if begin is None or match.name in _SKIP_BEGIN_FALLBACK:
            return None
        if not self._has_echo(begin.callable):
            return None
        return "action", str(getattr(self._begin_toolset, "slug", match.name)).replace("_", "-")

    def _load_echo_toolsets(self, repo: Path | None) -> list:
        from installation.installer import Installer
        from harness.agent_tools.agent_tools import AgentToolSet

        installer = Installer(repo=repo or _REPO_ROOT)
        return AgentToolSet.from_items(installer.collect_toolsets(), skip_errors=True)

    def _toast_path(self, repo: Path | None) -> Path:
        root = Path(repo) if repo is not None else _REPO_ROOT
        return root / TOAST_NOTICE

    def _write_notice(self, dest: Path, notice: str) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(notice, encoding="utf-8")

    def _toast_destinations(self, primary: Path) -> list[Path]:
        seen = {primary.resolve()}
        extra: list[Path] = []
        for root in self.toast_roots or []:
            dest = Path(str(root)) / TOAST_NOTICE
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
        return self._join_arrow_toasts(prev_msg, echo)

    def _read_toast(self, dest: Path) -> dict:
        try:
            previous = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return {}
        return previous if isinstance(previous, dict) else {}

    def _compact(self, text: str) -> str:
        stepped = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
        return re.sub(r"[^a-z0-9]+", "-", stepped.lower()).strip("-")

    def _walk_skill_tree(self, root: Path) -> None:
        if not root.is_dir():
            return
        found = self.skill_found
        top_kind = self.skill_kind
        for child in root.iterdir():
            if not child.is_dir():
                continue
            token = child.name.replace("_", "-")
            found.setdefault(token, top_kind)
            if top_kind != "practice":
                continue
            self._walk_practice_leaves(child)

    def _walk_practice_leaves(self, child: Path) -> None:
        found = self.skill_found
        for leaf in child.iterdir():
            if leaf.is_dir():
                found.setdefault(leaf.name.replace("_", "-"), "fidelity")

    def _walk_rule_tree(self, root: Path, found: dict[str, str]) -> None:
        if not root.is_dir():
            return
        for child in root.iterdir():
            if child.suffix == ".mdc":
                found.setdefault(child.stem.replace("_", "-"), "guideline")
                continue
            if not child.is_dir():
                continue
            found.setdefault(child.name.replace("_", "-"), "guideline")
            for leaf in child.glob("*.mdc"):
                found.setdefault(
                    f"{child.name}-{leaf.stem}".replace("_", "-"),
                    "guideline",
                )

    def _mcp_tool_name(self, hook_payload: dict) -> str:
        name = str(hook_payload.get("tool_name") or "")
        raw = hook_payload.get("tool_input")
        inp = raw if isinstance(raw, dict) else {}
        nested = inp.get("toolName") or inp.get("tool_name") or inp.get("name")
        if isinstance(nested, str) and nested.strip():
            if "mcp" in name.lower() or name in {"CallMcpTool", "call_mcp_tool"}:
                return nested.strip()
            if "." in nested or "-" in nested:
                return nested.strip()
        return name

    def _paths(self, hook_payload: dict) -> list[str]:
        raw = hook_payload.get("tool_input")
        inp = raw if isinstance(raw, dict) else {}
        found: list[str] = []
        for key in ("path", "file_path", "command"):
            value = inp.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value)
        return found

    def _haystacks(self, hook_payload: dict) -> list[str]:
        values = [self._mcp_tool_name(hook_payload), str(hook_payload.get("tool_name") or "")]
        values.extend(self._paths(hook_payload))
        return [item for item in values if item]

    def _token_in(self, hay: str, token: str) -> bool:
        compacted_hay = f"-{self._compact(hay)}-"
        compacted_token = f"-{self._compact(token)}-"
        return compacted_token in compacted_hay

    def _yaml_action(self, hook_payload: dict) -> str | None:
        for text in self._paths(hook_payload):
            match = _YAML_ACTION.search(text)
            if match:
                return match.group(1).replace("_", "-")
        return None

    def _has_echo(self, operation) -> bool:
        target = operation.fget if isinstance(operation, property) else operation
        inner = getattr(target, "__func__", target)
        return bool(getattr(inner, "_echo", False) or getattr(target, "_echo", False))

    def _echo_kind_label(self, tool) -> tuple[str, str]:
        toolset = tool.toolset
        if tool.name == "instructions":
            if getattr(toolset, "practice_guidance", None) is not None:
                return "fidelity", tool.slug
            return "practice", getattr(toolset, "slug", tool.name)
        if tool.name == "begin":
            return "action", getattr(toolset, "slug", tool.name)
        return "action", tool.name.replace("_", "-")

    def _inherited_echo(self, toolset, name: str) -> bool:
        for cls in type(toolset).mro():
            member = cls.__dict__.get(name)
            if member is None:
                continue
            target = member.fget if isinstance(member, property) else member
            if self._has_echo(target):
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
        if _ARROW not in previous or _ARROW not in incoming:
            return f"{previous}; {incoming}"
        prev_src, prev_rest = previous.split(_ARROW, 1)
        inc_src, inc_rest = incoming.split(_ARROW, 1)
        if prev_src.strip() != inc_src.strip():
            return f"{previous}; {incoming}"
        names: list[str] = []
        for name in self._guidance_names_from_toast_rest(
            prev_rest
        ) + self._guidance_names_from_toast_rest(inc_rest):
            if name not in names:
                names.append(name)
        return f"{prev_src.strip()}{_ARROW}rules : {', '.join(names)}"
