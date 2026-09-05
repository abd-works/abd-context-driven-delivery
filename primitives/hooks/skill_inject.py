"""
Skill-inject hook — fires before any file edit (preToolUse: Write / StrReplace).

If the target file has a @skill-tag in its header, injects a digest of that
skill's SKILL.md into agent_message so the agent reads the rules before editing.
Only injects once per conversation per file.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_NOTIFY_PS1 = Path(__file__).parent / "_notify_test.ps1"


def notify(title: str, body: str):
    """Fire a non-blocking system tray balloon tip."""
    if _NOTIFY_PS1.exists():
        subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(_NOTIFY_PS1),
             "-Title", title, "-Body", body],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_ROOT = _REPO_ROOT / ".cursor" / "skills"
_STATE_DIR = _REPO_ROOT / ".context" / "sessions" / "_skill_inject"
_DIGEST_LINES = 50

_TAG_TO_SKILL: dict[str, Path] = {
    "@clean-engineering-code":    _SKILLS_ROOT / "context_tools/clean_engineering/clean_engineering-code/SKILL.md",
    "@clean-engineering-model":   _SKILLS_ROOT / "context_tools/clean_engineering/clean_engineering-model/SKILL.md",
    "@clean-engineering-modules": _SKILLS_ROOT / "context_tools/clean_engineering/clean_engineering-modules/SKILL.md",
    "@clean-engineering":         _SKILLS_ROOT / "context_tools/clean_engineering/SKILL.md",
    "@stories-story_map":         _SKILLS_ROOT / "context_tools/stories/stories-story_map/SKILL.md",
    "@stories-scenarios":         _SKILLS_ROOT / "context_tools/stories/stories-scenarios/SKILL.md",
    "@stories-acceptance_tests":  _SKILLS_ROOT / "context_tools/stories/stories-acceptance_tests/SKILL.md",
    "@stories":                   _SKILLS_ROOT / "context_tools/stories/SKILL.md",
    "@ddd-bounded_context":       _SKILLS_ROOT / "context_tools/ddd/ddd-bounded_context/SKILL.md",
    "@ddd-building_blocks":       _SKILLS_ROOT / "context_tools/ddd/ddd-building_blocks/SKILL.md",
    "@ddd-tactics":               _SKILLS_ROOT / "context_tools/ddd/ddd-tactics/SKILL.md",
    "@ddd":                       _SKILLS_ROOT / "context_tools/ddd/SKILL.md",
    "@bdd-behavior":              _SKILLS_ROOT / "context_tools/bdd/bdd-behavior/SKILL.md",
    "@bdd-development":           _SKILLS_ROOT / "context_tools/bdd/bdd-development/SKILL.md",
    "@bdd-modules":               _SKILLS_ROOT / "context_tools/bdd/bdd-modules/SKILL.md",
    "@bdd":                       _SKILLS_ROOT / "context_tools/bdd/SKILL.md",
    "@ux-front_end_code":         _SKILLS_ROOT / "context_tools/ux/ux-front_end_code/SKILL.md",
    "@ux-mockup":                 _SKILLS_ROOT / "context_tools/ux/ux-mockup/SKILL.md",
    "@ux-ia":                     _SKILLS_ROOT / "context_tools/ux/ux-ia/SKILL.md",
    "@ux":                        _SKILLS_ROOT / "context_tools/ux/SKILL.md",
}

_EDIT_TOOLS = {"Write", "StrReplace", "str_replace_editor", "str_replace_based_edit_tool"}


def parse_payload(raw: bytes) -> dict:
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


def scan_tag(file_path: str) -> str | None:
    """Read first 20 lines of a file and return the first matching @skill-tag."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for _ in range(20):
                line = f.readline()
                if not line:
                    break
                for tag in _TAG_TO_SKILL:
                    if tag in line:
                        return tag
    except OSError:
        pass
    return None


def skill_digest(skill_path: Path) -> str:
    """Return first N lines of the SKILL.md as a digest."""
    try:
        lines = skill_path.read_text(encoding="utf-8").splitlines()
        digest = "\n".join(lines[:_DIGEST_LINES])
        if len(lines) > _DIGEST_LINES:
            digest += f"\n\n... [{len(lines) - _DIGEST_LINES} more lines in {skill_path.name}]"
        return digest
    except OSError:
        return f"[skill file not readable: {skill_path}]"


def already_injected(conversation_id: str, file_path: str) -> bool:
    if not conversation_id:
        return False
    state_file = _STATE_DIR / f"{conversation_id}.json"
    if not state_file.exists():
        return False
    try:
        seen = json.loads(state_file.read_text(encoding="utf-8"))
        return file_path in seen.get("files", [])
    except (OSError, json.JSONDecodeError):
        return False


def mark_injected(conversation_id: str, file_path: str):
    if not conversation_id:
        return
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = _STATE_DIR / f"{conversation_id}.json"
    try:
        seen = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}
    except (OSError, json.JSONDecodeError):
        seen = {}
    seen.setdefault("files", [])
    if file_path not in seen["files"]:
        seen["files"].append(file_path)
    state_file.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def _log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log = Path(__file__).with_suffix(".debug")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{ts} [skill-inject] {msg}\n")


def handle(data: dict) -> dict:
    tool_name = data.get("tool_name", "")
    if tool_name not in _EDIT_TOOLS:
        return {"permission": "allow"}

    tool_input = data.get("tool_input", {})
    file_path = (
        tool_input.get("path")
        or tool_input.get("file_path")
        or tool_input.get("target_file")
        or ""
    )
    if not file_path:
        return {"permission": "allow"}

    tag = scan_tag(file_path)
    if not tag:
        return {"permission": "allow"}

    conversation_id = data.get("conversation_id", "")

    if already_injected(conversation_id, file_path):
        _log(f"already injected tag={tag} file={file_path}")
        return {"permission": "allow"}

    skill_path = _TAG_TO_SKILL[tag]
    digest = skill_digest(skill_path)
    mark_injected(conversation_id, file_path)

    _log(f"injected tag={tag} file={file_path}")

    notify(
        title=f"Skill Gate: {tag}",
        body=f"{Path(file_path).name} — rules injected before edit",
    )

    msg = (
        f"SKILL GATE: {file_path} is governed by `{tag}`.\n"
        f"You MUST follow this skill before editing:\n\n"
        f"{digest}"
    )

    return {
        "permission": "allow",
        "agent_message": msg,
        "user_message": f"\u26a0\ufe0f Skill gate: `{tag}` injected for {Path(file_path).name}",
    }


def handle_compact(data: dict) -> dict:
    """On preCompact, delete the conversation's injection state so skills
    re-inject after the context window is trimmed."""
    conversation_id = data.get("conversation_id", "")
    if conversation_id:
        state_file = _STATE_DIR / f"{conversation_id}.json"
        if state_file.exists():
            state_file.unlink()
            _log(f"reset state on preCompact for conversation={conversation_id}")
        else:
            _log(f"preCompact — no state to reset for conversation={conversation_id}")
    return {}


def main():
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return
    try:
        data = parse_payload(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(json.dumps({"permission": "allow"}))
        return

    event = data.get("hook_event_name", "")
    if event == "preCompact":
        out = handle_compact(data)
    else:
        out = handle(data)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
