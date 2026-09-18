"""
Prompt echo hook — detects action skill references in prompts.

Fires on preToolUse. Parses tool input for known action names, then echoes
what was detected via user_message so the user sees it in the chat.

Off when the class is annotated ``@hooks(disabled=True)``.
"""

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
from installation.hooks.hooks import hook, hooks

ACTIONS = frozenset({
    "car-inspect",
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
    "travel-to",
    "validate",
})


def _detect_action(data: dict) -> str | None:
    """Find an action name in the tool's input content."""
    tool_input = data.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return None

    searchable = ""
    # Shell command text (catches `action: generate` in the YAML fence)
    searchable += tool_input.get("command", "") + " "
    # Read file path (catches .cursor/skills/actions/generate/SKILL.md)
    searchable += tool_input.get("file_path", "") + " "
    searchable += tool_input.get("path", "") + " "

    lower = searchable.lower()
    for action in ACTIONS:
        if action.lower() in lower:
            return action
    return None


@hooks(disabled=True)
@agent_toolset
class PromptEcho:
    """Echo detected action names on preToolUse."""

    @hook("preToolUse")
    def on_pre_tool_use(self, payload: dict) -> dict:
        return handle(payload)


def handle(data: dict) -> dict:
    tool_name = data.get("tool_name", "")
    if not tool_name:
        return {"permission": "allow"}

    action = _detect_action(data)

    if action:
        echo = f"\u2705 Got the hook!  Action \u2192 {action}"
    else:
        return {"permission": "allow"}

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stderr.write(f"{ts} [prompt-echo] tool={tool_name} action={action}\n")

    return {
        "permission": "allow",
        "user_message": echo,
    }
