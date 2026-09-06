"""Cursor hook runtime — dispatch, skill inject, bootstrap, and deploy wiring."""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path bootstrap (Cursor hooks omit PYTHONPATH)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOKS_JSON = _REPO_ROOT / ".cursor" / "hooks.json"
_DISPATCH_DEBUG = Path(__file__).with_suffix(".debug")
_SKILL_INJECT_DEBUG = Path(__file__).with_name("skill_inject.debug")
_NOTIFY_PS1 = Path(__file__).with_name("_notify_test.ps1")

for _category in ("primitives", "utilities", "primitives/hooks"):
    _entry = str(_REPO_ROOT / _category)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from hooks.hook import Hook, HookHarness

DISPATCH_SCRIPT = "primitives/hooks/dispatch.py"
_BOOTSTRAP_MODULES = ("workspace.workspace",)

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def load() -> None:
    """Import toolsets that declare ``@hook`` handlers."""
    for module_name in _BOOTSTRAP_MODULES:
        importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Deploy metadata (harness toggle skills + hooks.json wiring)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HookBinding:
    """One ``@hook`` operation discovered during harness deploy."""

    event: str
    operation: str
    slug: str = ""
    owner: str = ""
    folder: str = ""

    @classmethod
    def from_source(cls, source: dict) -> HookBinding:
        return cls(
            event=str(source.get("event") or ""),
            operation=str(source.get("operation") or ""),
            slug=str(source.get("slug") or source.get("name") or ""),
            owner=str(source.get("owner") or ""),
            folder=str(source.get("folder") or ""),
        )

    def deploy_slug(self) -> str:
        return self.operation or self.slug

    def event_suffix(self) -> str:
        return Hook.normalize_event(self.event)

    def toggle_flag(self) -> Path:
        owner_slug = self.owner.lower() if self.owner else "toolset"
        return (
            Path(".context")
            / "hooks"
            / owner_slug
            / f"{self.operation}_{self.event_suffix()}.enabled"
        )

    def skill_name(self, *, enabled: bool) -> str:
        suffix = "on" if enabled else "off"
        return f"{self.deploy_slug()}_{self.event_suffix()}_{suffix}"

    def overview(self, *, enabled: bool) -> str:
        verb = "Enable" if enabled else "Disable"
        return (
            f"{verb} `{self.deploy_slug()}` hook on "
            f"`{self.event}` ({self.event_suffix().replace('_', ' ')}) "
            f"for {self.owner or 'toolset'}."
        )

    def instructions(self, *, enabled: bool) -> str:
        verb = "Enable" if enabled else "Disable"
        flag = self.toggle_flag()
        body = (
            f"{verb} the `{self.deploy_slug()}` hook on Cursor event `{self.event}`.\n\n"
            f"Flag file: `{flag.as_posix()}`\n"
        )
        if enabled:
            body += (
                "\nCreate the flag file (empty is fine). The hook dispatcher runs "
                f"`{self.operation}` when this flag exists.\n"
            )
            if self.operation == "auto_turn":
                body += (
                    "\nOn `afterAgentResponse`, auto-turn stages all changes under "
                    "the repo root (including new untracked files) and commits after "
                    "each agent reply.\n"
                )
        else:
            body += "\nRemove the flag file so the dispatcher skips this handler.\n"
        return body

    def skill_sources(self) -> list[dict]:
        return [
            {
                "name": self.skill_name(enabled=enabled),
                "overview": self.overview(enabled=enabled),
                "body": self.instructions(enabled=enabled),
                "folder": self.folder,
            }
            for enabled in (True, False)
        ]


def hook_skill_sources(source: dict) -> tuple[list[dict], set[str]]:
    binding = HookBinding.from_source(source)
    events = {binding.event} if binding.event else set()
    return binding.skill_sources(), events


def deploy_dispatch(repo_root: Path, events: set[str]) -> None:
    HookHarness(script=DISPATCH_SCRIPT).sync_dispatch(
        repo_root / ".cursor" / "hooks.json",
        events,
    )


def install_dispatch() -> None:
    """Sync ``dispatch.py`` entries in ``.cursor/hooks.json``."""
    load()
    events = {entry["event"] for entry in Hook.registered()}
    if not events:
        print("No @hook handlers registered — nothing to install.")
        return
    deploy_dispatch(_REPO_ROOT, events)
    print(f"Installed dispatch hooks for {sorted(events)} -> {_HOOKS_JSON}")


# ---------------------------------------------------------------------------
# Shared stdin parsing
# ---------------------------------------------------------------------------


def parse_payload(raw: bytes) -> dict[str, Any]:
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


# ---------------------------------------------------------------------------
# @hook dispatch
# ---------------------------------------------------------------------------


def _dispatch_debug(msg: str) -> None:
    with open(_DISPATCH_DEBUG, "a", encoding="utf-8") as f:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        f.write(f"{ts} {msg}\n")


def _merge_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {"permission": "allow"}
    agent_messages: list[str] = []
    user_messages: list[str] = []
    followup_message: str | None = None
    for item in results:
        if not item:
            continue
        if item.get("permission") == "deny":
            merged["permission"] = "deny"
        if item.get("continue") is False:
            merged["continue"] = False
        value = item.get("user_message")
        if value:
            user_messages.append(str(value))
        value = item.get("agent_message")
        if value:
            agent_messages.append(str(value))
        value = item.get("followup_message")
        if value:
            followup_message = str(value)
    if user_messages:
        merged["user_message"] = "\n".join(user_messages)
    if agent_messages:
        merged["agent_message"] = "\n".join(agent_messages)
    if followup_message:
        merged["followup_message"] = followup_message
    return merged


def _matcher_ok(matcher: str | None, payload: dict[str, Any]) -> bool:
    if not matcher:
        return True
    tool_name = str(payload.get("tool_name") or "")
    return re.search(matcher, tool_name) is not None


def dispatch(payload: dict[str, Any]) -> dict[str, Any]:
    event = str(payload.get("hook_event_name") or "")
    conv = payload.get("conversation_id")
    _dispatch_debug(
        f"EVENT {event!r} conversation_id={conv!r} payload_keys={sorted(payload.keys())}"
    )
    if not event:
        _dispatch_debug("NO_EVENT merged={}")
        return {"permission": "allow"}

    results: list[dict[str, Any]] = []
    enabled: list[str] = []
    for entry in Hook.bindings_for(event):
        if not _matcher_ok(entry.get("matcher"), payload):
            continue
        owner = entry["owner"]
        method = entry["method"]
        if not Hook.is_enabled(owner, method, event):
            continue
        label = f"{owner.__name__}.{method}"
        enabled.append(label)
        instance = owner()
        handler = getattr(instance, method)
        result = handler(payload)
        results.append(result)
        result_keys = sorted((result or {}).keys())
        _dispatch_debug(
            f"HANDLER {label} result_keys={result_keys} result={json.dumps(result or {})}"
        )
    _dispatch_debug(f"ENABLED {enabled or ['(none)']}")
    merged = _merge_results(results)
    _dispatch_debug(f"MERGED {json.dumps(merged)}")
    return merged


def _run_dispatch_hook(raw: bytes) -> None:
    _dispatch_debug(f"ENTRY raw_len={len(raw)} raw={raw[:200]!r}")
    if not raw.strip():
        _dispatch_debug("empty stdin, allowing")
        print(json.dumps({"permission": "allow"}))
        return
    payload = parse_payload(raw)
    event = str(payload.get("hook_event_name") or "")
    if event == "afterAgentResponse":
        try:
            from hooks.prompt_log.prompt_log import append_log, format_after_agent_response

            append_log(format_after_agent_response(payload))
        except OSError:
            pass
    out = dispatch(payload)
    print(json.dumps(out))


# ---------------------------------------------------------------------------
# Skill inject (preToolUse edits + preCompact reset)
# ---------------------------------------------------------------------------

_SKILLS_ROOT = _REPO_ROOT / ".cursor" / "skills"
_STATE_DIR = _REPO_ROOT / ".context" / "sessions" / "_skill_inject"
_DIGEST_LINES = 50

_TAG_TO_SKILL: dict[str, Path] = {
    "@clean-engineering-code": _SKILLS_ROOT
    / "context_tools/clean_engineering/clean_engineering-code/SKILL.md",
    "@clean-engineering-model": _SKILLS_ROOT
    / "context_tools/clean_engineering/clean_engineering-model/SKILL.md",
    "@clean-engineering-modules": _SKILLS_ROOT
    / "context_tools/clean_engineering/clean_engineering-modules/SKILL.md",
    "@clean-engineering": _SKILLS_ROOT / "context_tools/clean_engineering/SKILL.md",
    "@stories-story_map": _SKILLS_ROOT / "context_tools/stories/stories-story_map/SKILL.md",
    "@stories-scenarios": _SKILLS_ROOT / "context_tools/stories/stories-scenarios/SKILL.md",
    "@stories-acceptance_tests": _SKILLS_ROOT
    / "context_tools/stories/stories-acceptance_tests/SKILL.md",
    "@stories": _SKILLS_ROOT / "context_tools/stories/SKILL.md",
    "@ddd-bounded_context": _SKILLS_ROOT / "context_tools/ddd/ddd-bounded_context/SKILL.md",
    "@ddd-building_blocks": _SKILLS_ROOT / "context_tools/ddd/ddd-building_blocks/SKILL.md",
    "@ddd-tactics": _SKILLS_ROOT / "context_tools/ddd/ddd-tactics/SKILL.md",
    "@ddd": _SKILLS_ROOT / "context_tools/ddd/SKILL.md",
    "@bdd-behavior": _SKILLS_ROOT / "context_tools/bdd/bdd-behavior/SKILL.md",
    "@bdd-development": _SKILLS_ROOT / "context_tools/bdd/bdd-development/SKILL.md",
    "@bdd-modules": _SKILLS_ROOT / "context_tools/bdd/bdd-modules/SKILL.md",
    "@bdd": _SKILLS_ROOT / "context_tools/bdd/SKILL.md",
    "@ux-front_end_code": _SKILLS_ROOT / "context_tools/ux/ux-front_end_code/SKILL.md",
    "@ux-mockup": _SKILLS_ROOT / "context_tools/ux/ux-mockup/SKILL.md",
    "@ux-ia": _SKILLS_ROOT / "context_tools/ux/ux-ia/SKILL.md",
    "@ux": _SKILLS_ROOT / "context_tools/ux/SKILL.md",
}

_EDIT_TOOLS = {"Write", "StrReplace", "str_replace_editor", "str_replace_based_edit_tool"}


def _skill_notify(title: str, body: str) -> None:
    if _NOTIFY_PS1.exists():
        subprocess.Popen(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(_NOTIFY_PS1),
                "-Title",
                title,
                "-Body",
                body,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _skill_inject_log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(_SKILL_INJECT_DEBUG, "a", encoding="utf-8") as f:
        f.write(f"{ts} [skill-inject] {msg}\n")


def scan_tag(file_path: str) -> str | None:
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


def mark_injected(conversation_id: str, file_path: str) -> None:
    if not conversation_id:
        return
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = _STATE_DIR / f"{conversation_id}.json"
    try:
        seen = (
            json.loads(state_file.read_text(encoding="utf-8"))
            if state_file.exists()
            else {}
        )
    except (OSError, json.JSONDecodeError):
        seen = {}
    seen.setdefault("files", [])
    if file_path not in seen["files"]:
        seen["files"].append(file_path)
    state_file.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def skill_inject(data: dict[str, Any]) -> dict[str, Any]:
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
        _skill_inject_log(f"already injected tag={tag} file={file_path}")
        return {"permission": "allow"}

    skill_path = _TAG_TO_SKILL[tag]
    digest = skill_digest(skill_path)
    mark_injected(conversation_id, file_path)
    _skill_inject_log(f"injected tag={tag} file={file_path}")
    _skill_notify(
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


def skill_inject_compact(data: dict[str, Any]) -> dict[str, Any]:
    conversation_id = data.get("conversation_id", "")
    if conversation_id:
        state_file = _STATE_DIR / f"{conversation_id}.json"
        if state_file.exists():
            state_file.unlink()
            _skill_inject_log(
                f"reset state on preCompact for conversation={conversation_id}"
            )
        else:
            _skill_inject_log(
                f"preCompact — no state to reset for conversation={conversation_id}"
            )
    return {}


def _run_skill_inject_hook(raw: bytes) -> None:
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
        out = skill_inject_compact(data)
    else:
        out = skill_inject(data)
    print(json.dumps(out))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    os.chdir(_REPO_ROOT)
    if len(sys.argv) > 1 and sys.argv[1] in {"--install", "install"}:
        install_dispatch()
        return

    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return

    try:
        payload = parse_payload(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(json.dumps({"permission": "allow"}))
        return

    event = str(payload.get("hook_event_name") or "")
    if event in {"preToolUse", "preCompact"}:
        _run_skill_inject_hook(raw)
        return

    load()
    _run_dispatch_hook(raw)


if __name__ == "__main__":
    main()
