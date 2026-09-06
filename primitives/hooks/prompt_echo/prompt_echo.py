"""
Prompt echo hook — detects action skill references in prompts.

Fires on beforeSubmitPrompt. Parses the user prompt for known action
names, then echoes what was detected via user_message so the user sees
it right in the chat.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def parse_hook_payload(raw: bytes) -> dict:
    """Strip BOM(s) the way Cursor sends them, then parse JSON."""
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


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


_DEBUG_LOG = Path(__file__).with_suffix(".debug")


def _debug(msg: str):
    with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        f.write(f"{ts} {msg}\n")


def main():
    raw = sys.stdin.buffer.read()
    _debug(f"ENTRY raw_len={len(raw)} raw={raw[:200]!r}")

    if not raw.strip():
        _debug("empty stdin, allowing")
        print(json.dumps({"permission": "allow"}))
        return

    try:
        data = parse_hook_payload(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        _debug(f"PARSE_ERROR {exc}")
        print(json.dumps({"permission": "allow"}))
        return

    _debug(f"PAYLOAD keys={sorted(data.keys())}")
    out = handle(data)
    _debug(f"OUTPUT {json.dumps(out)}")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
