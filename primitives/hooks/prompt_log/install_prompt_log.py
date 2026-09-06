"""
Merge prompt-log.json hook entries into .cursor/hooks.json.

Usage (from repo root):
    .venv/Scripts/python.exe primitives/hooks/prompt_log/install_prompt_log.py
"""

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FRAGMENT = Path(__file__).with_name("prompt-log.json")
_HOOKS_JSON = _REPO_ROOT / ".cursor" / "hooks.json"
_PYTHON = ".venv/Scripts/python.exe primitives/hooks/prompt_log/prompt_log.py"


def _entry() -> dict:
    return {"command": _PYTHON, "timeout": 10, "failClosed": False}


def _already_present(hooks: dict, event: str) -> bool:
    for item in hooks.get(event, []):
        if "prompt_log.py" in item.get("command", ""):
            return True
    return False


def merge(dest: Path, fragment: dict) -> dict:
    if dest.exists():
        data = json.loads(dest.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "hooks": {}}

    hooks = data.setdefault("hooks", {})
    for event, entries in fragment.get("hooks", {}).items():
        if _already_present(hooks, event):
            continue
        hooks.setdefault(event, []).extend(entries)
    return data


def main():
    fragment = json.loads(_FRAGMENT.read_text(encoding="utf-8"))
    merged = merge(_HOOKS_JSON, fragment)
    _HOOKS_JSON.parent.mkdir(parents=True, exist_ok=True)
    _HOOKS_JSON.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    try:
        from hooks.bootstrap import load
        from hooks.deploy import deploy_dispatch
        from hooks.hook import Hook

        load()
        events = {entry["event"] for entry in Hook.registered()}
        if events:
            deploy_dispatch(_REPO_ROOT, events)
    except ImportError:
        pass
    print(f"Installed prompt_log hooks -> {_HOOKS_JSON}")


if __name__ == "__main__":
    main()
