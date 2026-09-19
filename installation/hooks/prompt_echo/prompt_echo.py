"""
Prompt echo hook — detect CDD action, practice, fidelity, and guideline use.

Fires on preToolUse. Matches MCP names (`sketch.sketch`, `bdd-behavior()`),
CallMcpTool wrappers, skill/rule paths, and legacy YAML `action:` fences.

Off when the class is annotated ``@Hooks(disabled=True)``.
"""

from __future__ import annotations

import re
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
from installation.hooks.hooks import Hook

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


@agent_toolset
class PromptEcho:
    """Echo detected action, practice, fidelity, and guideline names on preToolUse."""

    @Hook("preToolUse")
    def on_pre_tool_use(self, payload: dict) -> dict:
        return handle(payload)


def handle(data: dict) -> dict:
    tool_name = data.get("tool_name", "")
    if not tool_name:
        return {"permission": "allow"}
    detected = detect(data)
    if not detected:
        return {"permission": "allow"}
    kind, label = detected
    echo = f"\u2705 Got the hook!  {kind.title()} \u2192 {label}"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stderr.write(f"{ts} [prompt-echo] tool={tool_name} {kind}={label}\n")
    return {
        "permission": "allow",
        "user_message": echo,
    }
