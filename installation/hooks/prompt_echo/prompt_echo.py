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

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _category in ("harness", "tools"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agent_tools import agent_toolset
from installation.installer import Destination
from installation.hooks.hooks import Hook


class Echo(Destination):
    """Mark an AgentOperation or AgentInstructions so PromptEcho toasts it."""

    flag = "_echo"

    def __new__(cls, fn=None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(fn):
            return inst.annotate(fn)
        return inst


echo = Echo

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
_CATALOG: list[tuple[str, str]] | None = None


def _compact(text: str) -> str:
    stepped = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    return re.sub(r"[^a-z0-9]+", "-", stepped.lower()).strip("-")


def _walk_skill_tree(root: Path, top_kind: str, found: dict[str, str]) -> None:
    if not root.is_dir():
        return
    for child in root.iterdir():
        if not child.is_dir():
            continue
        token = child.name.replace("_", "-")
        found.setdefault(token, top_kind)
        if top_kind != "practice":
            continue
        for leaf in child.iterdir():
            if leaf.is_dir():
                found.setdefault(leaf.name.replace("_", "-"), "fidelity")


def _walk_rule_tree(root: Path, found: dict[str, str]) -> None:
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


def catalog() -> list[tuple[str, str]]:
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    found: dict[str, str] = {}
    skills = _REPO_ROOT / ".cursor" / "skills"
    _walk_skill_tree(skills / "actions", "action", found)
    _walk_skill_tree(skills / "practices", "practice", found)
    _walk_rule_tree(_REPO_ROOT / ".cursor" / "rules" / "practices", found)
    for name in _FALLBACK_ACTIONS:
        found.setdefault(name.replace("_", "-"), "action")
    _CATALOG = sorted(found.items(), key=lambda item: len(item[0]), reverse=True)
    return _CATALOG


def _mcp_tool_name(data: dict) -> str:
    name = str(data.get("tool_name") or "")
    raw = data.get("tool_input")
    inp = raw if isinstance(raw, dict) else {}
    nested = inp.get("toolName") or inp.get("tool_name") or inp.get("name")
    if isinstance(nested, str) and nested.strip():
        if "mcp" in name.lower() or name in {"CallMcpTool", "call_mcp_tool"}:
            return nested.strip()
        if "." in nested or "-" in nested:
            return nested.strip()
    return name


def _paths(data: dict) -> list[str]:
    raw = data.get("tool_input")
    inp = raw if isinstance(raw, dict) else {}
    found: list[str] = []
    for key in ("path", "file_path", "command"):
        value = inp.get(key)
        if isinstance(value, str) and value.strip():
            found.append(value)
    return found


def _haystacks(data: dict) -> list[str]:
    values = [_mcp_tool_name(data), str(data.get("tool_name") or "")]
    values.extend(_paths(data))
    return [item for item in values if item]


def _token_in(hay: str, token: str) -> bool:
    compacted_hay = f"-{_compact(hay)}-"
    compacted_token = f"-{_compact(token)}-"
    return compacted_token in compacted_hay


def _yaml_action(data: dict) -> str | None:
    for text in _paths(data):
        match = _YAML_ACTION.search(text)
        if match:
            return match.group(1).replace("_", "-")
    return None


_SKIP_BEGIN_FALLBACK = frozenset({"open_workspace", "end", "begin"})
_ECHO_TOOLSETS: list | None = None


def _has_echo(fn) -> bool:
    target = fn.fget if isinstance(fn, property) else fn
    inner = getattr(target, "__func__", target)
    return bool(getattr(inner, "_echo", False) or getattr(target, "_echo", False))


def _echo_kind_label(tool) -> tuple[str, str]:
    toolset = tool.toolset
    if tool.name == "instructions":
        if getattr(toolset, "practice_guidance", None) is not None:
            return "fidelity", tool.slug
        return "practice", getattr(toolset, "slug", tool.name)
    if tool.name == "begin":
        return "action", getattr(toolset, "slug", tool.name)
    return "action", tool.name.replace("_", "-")


def _inherited_echo(toolset, name: str) -> bool:
    for cls in type(toolset).mro():
        member = cls.__dict__.get(name)
        if member is None:
            continue
        target = member.fget if isinstance(member, property) else member
        if _has_echo(target):
            return True
    return False


def _mcp_aliases(tool) -> set[str]:
    toolset = tool.toolset
    slug = str(getattr(toolset, "slug", "") or "")
    names = {f"{slug}.{tool.name}", f"{slug}_{tool.name}", tool.name}
    if getattr(toolset, "practice_guidance", None) is not None:
        names.add(tool.slug)
    if tool.name == "instructions" and slug:
        names.add(slug)
        names.add(f"{slug}.instructions")
    return {item for item in names if item}


def _name_matches(invoked: str, tool) -> bool:
    compact_invoked = _compact(invoked)
    return any(_compact(name) == compact_invoked for name in _mcp_aliases(tool))


def _walk_toolsets(toolsets: list) -> list:
    found: list = []
    for toolset in toolsets:
        found.append(toolset)
        nested = getattr(toolset, "nested_toolsets", None) or []
        for child in nested:
            found.append(child)
    return found


def echo_toolsets(repo: Path | None = None) -> list:
    global _ECHO_TOOLSETS
    if repo is None and _ECHO_TOOLSETS is not None:
        return _ECHO_TOOLSETS
    from installation.installer import Installer
    from harness.agent_tools.agent_tools import AgentToolSet

    installer = Installer(repo=repo or _REPO_ROOT)
    loaded = AgentToolSet.load_toolsets(installer.collect_toolsets(), skip_errors=True)
    if repo is None:
        _ECHO_TOOLSETS = loaded
    return loaded


def detect_echo(data: dict, toolsets: list | None = None) -> tuple[str, str] | None:
    """Return (kind, label) from @echo on the invoked member or inherited begin."""
    invoked = _mcp_tool_name(data)
    if not invoked:
        return None
    hosts = _walk_toolsets(toolsets if toolsets is not None else echo_toolsets())
    for toolset in hosts:
        tools = getattr(toolset, "tools", None) or {}
        if not isinstance(tools, dict):
            continue
        match = next((tool for tool in tools.values() if _name_matches(invoked, tool)), None)
        if match is None:
            continue
        if _has_echo(match.callable):
            return _echo_kind_label(match)
        if match.name == "instructions" and _inherited_echo(toolset, "instructions"):
            return _echo_kind_label(match)
        begin = tools.get("begin")
        if (
            begin is not None
            and match.name not in _SKIP_BEGIN_FALLBACK
            and _has_echo(begin.callable)
        ):
            return "action", str(getattr(toolset, "slug", match.name)).replace("_", "-")
    return None


def detect(data: dict) -> tuple[str, str] | None:
    """Return (kind, label) for a CDD action, practice, fidelity, or guideline."""
    named = _yaml_action(data)
    if named:
        return "action", named
    for hay in _haystacks(data):
        for token, kind in catalog():
            if not _token_in(hay, token):
                continue
            if "/rules/" in hay.replace("\\", "/").lower():
                return "guideline", token
            return kind, token
    return None


TOAST_NOTICE = ".cursor/prompt-echo-toast.json"
IDE_TOAST_EXTENSION = "cdd.prompt-echo-0.0.1"


def toast_notice(echo: str) -> dict[str, str]:
    return {
        "message": echo,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def show_ide_toast(echo: str, repo: Path | None = None) -> Path:
    root = Path(repo) if repo is not None else _REPO_ROOT
    dest = root / TOAST_NOTICE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(toast_notice(echo), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return dest


def install_ide_toast_extension() -> Path:
    source = Path(__file__).resolve().parent / "ide_toast"
    dest = Path.home() / ".cursor" / "extensions" / IDE_TOAST_EXTENSION
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, dirs_exist_ok=True)
    return dest


@agent_toolset
class PromptEcho:
    """Echo detected action, practice, fidelity, and guideline names on preToolUse."""

    @Hook("preToolUse")
    def on_pre_tool_use(self, payload: dict) -> dict:
        result = handle(payload, toolsets=echo_toolsets())
        message = result.get("user_message")
        if message:
            show_ide_toast(str(message))
        return result


def handle(data: dict, toolsets: list | None = None) -> dict:
    tool_name = data.get("tool_name", "")
    if not tool_name:
        return {"permission": "allow"}
    detected = detect_echo(data, toolsets=toolsets) if toolsets is not None else None
    if not detected:
        detected = detect(data)
    if not detected:
        return {"permission": "allow"}
    kind, label = detected
    message = f"{kind.title()} \u2192 {label}"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stderr.write(f"{ts} [prompt-echo] tool={tool_name} {kind}={label}\n")
    return {
        "permission": "allow",
        "user_message": message,
    }
