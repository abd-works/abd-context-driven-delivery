"""VSCode agent hook — run header manifests / invoke-edit; block writes until cleared.

beforeReadFile / postToolUse:
  Scan header, run @toolset-manifest, run invoke-edit via ``python -m tools run -``,
  inject output, and clear the path once invoke-edit has been executed.

preToolUse (Write / StrReplace / …):
  Deny mutating edits to files with invoke-edit until that path is cleared.
  Non-mutating tools are always allowed.

afterShellExecution:
  If the agent ran ``python -m tools run`` for a pending invoke-edit action/toolset,
  clear that path (covers hook-side failures or agent-run invoke).

Clearance is stored in hooks/.manifest_gate_clearance.json.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
_HOOKS_DIR = Path(__file__).resolve().parent
_LOG_FILE = _HOOKS_DIR / "manifest_gate.log"
_CLEARANCE_FILE = _HOOKS_DIR / ".manifest_gate_clearance.json"
_MANIFEST_PREFIXES = ("# @toolset-manifest", "# invoke-")
_SCAN_LINES = 15
_CATEGORY_DIRS = ("primitives", "utilities", "context_tools")
_MUTATING_TOOLS = frozenset(
    {
        "Write",
        "StrReplace",
        "EditNotebook",
        "Delete",
        "delete_file",
        "search_replace",
        "write",
    }
)
_INVOKE_EDIT_RE = re.compile(r"^#\s*invoke-edit:\s*(.+)$", re.IGNORECASE)
_MANIFEST_CMD_RE = re.compile(r"^#\s*@toolset-manifest\s+(.+)$", re.IGNORECASE)


def _pythonpath_env() -> dict[str, str]:
    """Env with repo + category dirs on PYTHONPATH for hybrid imports."""
    env = os.environ.copy()
    entries = [str(_REPO_ROOT)] + [str(_REPO_ROOT / name) for name in _CATEGORY_DIRS]
    existing = env.get("PYTHONPATH", "")
    prefix = os.pathsep.join(entries)
    env["PYTHONPATH"] = prefix if not existing else prefix + os.pathsep + existing
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def _log(mode: str, path: str, fired: bool, detail: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = "FIRED" if fired else "skip"
    line = f"{ts} [{mode:4}] {status}  {path}"
    if detail:
        line += f"  — {detail}"
    try:
        with _LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def _find_python() -> str:
    """Prefer the repo venv Python; fall back to this interpreter."""
    for candidate in [
        _REPO_ROOT / ".venv" / "Scripts" / "python.exe",
        _REPO_ROOT / "venv" / "Scripts" / "python.exe",
        _REPO_ROOT / ".venv" / "bin" / "python",
        _REPO_ROOT / "venv" / "bin" / "python",
    ]:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def _norm_path(path: str) -> str:
    try:
        return str(Path(path).resolve())
    except OSError:
        return path


def _load_clearance() -> dict[str, Any]:
    if not _CLEARANCE_FILE.is_file():
        return {}
    try:
        data = json.loads(_CLEARANCE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_clearance(data: dict[str, Any]) -> None:
    try:
        _CLEARANCE_FILE.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError:
        pass


def is_cleared(path: str) -> bool:
    data = _load_clearance()
    entry = data.get(_norm_path(path))
    return isinstance(entry, dict) and entry.get("cleared") is True


def clear_path(path: str, *, detail: str = "") -> None:
    data = _load_clearance()
    key = _norm_path(path)
    pending = data.get("_pending", {})
    if isinstance(pending, dict):
        pending.pop(key, None)
        data["_pending"] = pending
    data[key] = {
        "cleared": True,
        "cleared_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "detail": detail,
    }
    _save_clearance(data)


def mark_pending_invoke(path: str, invoke: dict[str, Any]) -> None:
    data = _load_clearance()
    pending = data.setdefault("_pending", {})
    if not isinstance(pending, dict):
        pending = {}
        data["_pending"] = pending
    pending[_norm_path(path)] = {
        "action": invoke.get("action"),
        "toolset": invoke.get("toolset"),
    }
    _save_clearance(data)


def scan_manifest_lines(path: str) -> list[str]:
    """Return lines starting with manifest prefixes from the first _SCAN_LINES of path."""
    p = Path(path)
    if not p.is_file():
        return []
    lines: list[str] = []
    try:
        with p.open(encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh):
                if i >= _SCAN_LINES:
                    break
                stripped = line.strip()
                if any(stripped.startswith(prefix) for prefix in _MANIFEST_PREFIXES):
                    lines.append(stripped)
    except OSError:
        return []
    return lines


def toolset_from_manifest_lines(manifest_lines: list[str]) -> str | None:
    for line in manifest_lines:
        match = _MANIFEST_CMD_RE.match(line)
        if not match:
            continue
        parts = match.group(1).split()
        if parts:
            return parts[-1]
    return None


def parse_invoke_directive(body: str) -> dict[str, Any]:
    """Parse ``action X | toolset: A:B | context.fidelity modules`` style bodies."""
    result: dict[str, Any] = {"action": None, "toolset": None, "context": {}}
    for raw_part in body.split("|"):
        part = raw_part.strip()
        if not part:
            continue
        lower = part.lower()
        if lower.startswith("action "):
            result["action"] = part[7:].strip()
        elif lower.startswith("toolset:"):
            result["toolset"] = part.split(":", 1)[1].strip()
        elif lower.startswith("context."):
            rest = part[len("context.") :]
            if ":" in rest:
                key, value = rest.split(":", 1)
            else:
                bits = rest.split(None, 1)
                if len(bits) != 2:
                    continue
                key, value = bits
            result["context"][key.strip()] = value.strip()
    return result


def find_invoke_edit(manifest_lines: list[str]) -> dict[str, Any] | None:
    for line in manifest_lines:
        match = _INVOKE_EDIT_RE.match(line)
        if not match:
            continue
        parsed = parse_invoke_directive(match.group(1))
        if not parsed.get("action"):
            return None
        if not parsed.get("toolset"):
            parsed["toolset"] = toolset_from_manifest_lines(manifest_lines)
        if not parsed.get("toolset"):
            return None
        return parsed
    return None


def build_invoke_edit_request(invoke: dict[str, Any]) -> str:
    lines = [f"toolset: {invoke['toolset']}", f"action: {invoke['action']}"]
    context = invoke.get("context") or {}
    if context:
        lines.append("context:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")
    return "\n".join(lines) + "\n"


def run_manifests(manifest_lines: list[str]) -> str:
    """Run each @toolset-manifest command and return the combined output."""
    python = _find_python()
    outputs: list[str] = []
    for line in manifest_lines:
        if not line.startswith("# @toolset-manifest"):
            continue
        cmd_str = line.removeprefix("# @toolset-manifest").strip()
        parts = cmd_str.split()
        if parts and parts[0] == "python":
            parts[0] = python
        try:
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(_REPO_ROOT),
                env=_pythonpath_env(),
                timeout=30,
            )
            if result.stdout and result.stdout.strip():
                outputs.append(result.stdout.strip())
        except (subprocess.TimeoutExpired, OSError):
            pass
    return "\n\n".join(outputs)


def run_invoke_edit(invoke: dict[str, Any]) -> tuple[bool, str]:
    """Run invoke-edit via ``python -m tools run -``.

    Returns (executed, output). ``executed`` means the CLI ran to completion —
    clearance keys off execution, not action ok:true (some actions still error
    on response serialization after producing instructions).
    """
    python = _find_python()
    request = build_invoke_edit_request(invoke)
    try:
        result = subprocess.run(
            [python, "-m", "tools", "run", "-", "--plain"],
            input=request,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(_REPO_ROOT),
            env=_pythonpath_env(),
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, str(exc)
    output = (result.stdout or "").strip()
    if result.stderr and result.stderr.strip():
        output = (output + "\n" + result.stderr.strip()).strip()
    return True, output


def _format_message(
    path: str,
    manifest_lines: list[str],
    manifest_output: str,
    *,
    invoke: dict[str, Any] | None = None,
    invoke_output: str = "",
    blocked: bool = False,
) -> str:
    header = "\n".join(f"  {l}" for l in manifest_lines)
    parts = [
        f"MANIFEST GATE — {path}",
        (
            "EDIT BLOCKED until invoke-edit has been executed for this file."
            if blocked
            else "Header executed. Follow response.instructions only — do not author from source."
        ),
        "",
        header,
        "",
        "Manifest output (injected automatically):",
        manifest_output or "(none)",
    ]
    if invoke:
        req = build_invoke_edit_request(invoke)
        parts.extend(
            [
                "",
                f"invoke-edit → action {invoke['action']} | toolset: {invoke['toolset']}",
                "tools run request:",
                "```yaml",
                req.rstrip(),
                "```",
                "Run: python -m tools run -",
            ]
        )
        if invoke_output:
            parts.extend(["", "invoke-edit output:", invoke_output])
    return "\n".join(parts)


def _user_notification(path: str, *, blocked: bool = False, cleared: bool = False) -> str:
    name = Path(path).name
    if blocked:
        return f"Manifest gate: blocked edit of {name} — run invoke-edit first"
    if cleared:
        return f"Manifest gate: cleared {name} after invoke-edit"
    return f"Manifest gate: ran header for {name}"


def _extract_path(data: dict) -> str:
    """Extract file path from hook payload."""
    ti = data.get("tool_input") or {}
    return (
        ti.get("path")
        or ti.get("file_path")
        or data.get("file_path")
        or ""
    )


def _tool_name(data: dict) -> str:
    return str(data.get("tool_name") or data.get("tool") or "")


def _is_mutating_tool(data: dict) -> bool:
    name = _tool_name(data)
    if name in _MUTATING_TOOLS:
        return True
    ti = data.get("tool_input") or {}
    if ti.get("contents") is not None or ti.get("content") is not None:
        return True
    if ti.get("old_string") is not None or ti.get("new_string") is not None:
        return True
    return False


def _prepare_file(path: str, lines: list[str]) -> tuple[str, dict[str, Any] | None, str, bool]:
    """Run manifest + invoke-edit. Returns (manifest_out, invoke, invoke_out, cleared)."""
    manifest_output = run_manifests(lines)
    invoke = find_invoke_edit(lines)
    invoke_output = ""
    cleared = False
    if invoke:
        executed, invoke_output = run_invoke_edit(invoke)
        if executed:
            clear_path(path, detail=f"invoke-edit {invoke['action']}")
            cleared = True
        else:
            mark_pending_invoke(path, invoke)
    elif manifest_output:
        clear_path(path, detail="manifest only")
        cleared = True
    return manifest_output, invoke, invoke_output, cleared


def handle_before_read_file(data: dict) -> dict:
    """beforeReadFile — execute header; clear when invoke-edit runs."""
    path = _extract_path(data)
    if not path:
        return {}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("read", path, fired=False)
        return {}
    manifest_output, invoke, invoke_output, cleared = _prepare_file(path, lines)
    if not manifest_output and not invoke_output:
        _log("read", path, fired=False, detail="header ran but produced no output")
        return {}
    _log("read", path, fired=True, detail=f"{len(lines)} line(s); cleared={cleared}")
    return {
        "agent_message": _format_message(
            path, lines, manifest_output, invoke=invoke, invoke_output=invoke_output
        ),
        "user_message": _user_notification(path, cleared=cleared),
    }


def handle_post_tool_use(data: dict) -> dict:
    """postToolUse — same prepare/inject as read."""
    path = _extract_path(data)
    if not path:
        return {}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("post", path, fired=False)
        return {}
    manifest_output, invoke, invoke_output, cleared = _prepare_file(path, lines)
    if not manifest_output and not invoke_output:
        _log("post", path, fired=False, detail="header ran but produced no output")
        return {}
    _log("post", path, fired=True, detail=f"{len(lines)} line(s); cleared={cleared}")
    return {
        "additional_context": _format_message(
            path, lines, manifest_output, invoke=invoke, invoke_output=invoke_output
        ),
        "user_message": _user_notification(path, cleared=cleared),
    }


def handle_pre_tool_use(data: dict) -> dict:
    """preToolUse — deny mutating edits until invoke-edit cleared the path."""
    path = _extract_path(data)
    if not path:
        return {"permission": "allow"}
    if not _is_mutating_tool(data):
        return {"permission": "allow"}
    if not Path(path).is_file():
        return {"permission": "allow"}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("pre ", path, fired=False)
        return {"permission": "allow"}

    invoke = find_invoke_edit(lines)
    if invoke is None:
        manifest_output, _, invoke_output, _ = _prepare_file(path, lines)
        _log("pre ", path, fired=True, detail="no invoke-edit; allow")
        return {
            "permission": "allow",
            "agent_message": _format_message(
                path, lines, manifest_output, invoke_output=invoke_output
            ),
            "user_message": _user_notification(path),
        }

    if is_cleared(path):
        manifest_output = run_manifests(lines)
        _log("pre ", path, fired=True, detail="cleared; allow")
        return {
            "permission": "allow",
            "agent_message": _format_message(
                path, lines, manifest_output, invoke=invoke
            ),
            "user_message": _user_notification(path, cleared=True),
        }

    # Not cleared — execute invoke-edit now; allow only if executed.
    manifest_output, invoke, invoke_output, cleared = _prepare_file(path, lines)
    if cleared:
        _log("pre ", path, fired=True, detail="invoke-edit executed; allow")
        return {
            "permission": "allow",
            "agent_message": _format_message(
                path,
                lines,
                manifest_output,
                invoke=invoke,
                invoke_output=invoke_output,
            ),
            "user_message": _user_notification(path, cleared=True),
        }

    _log("pre ", path, fired=True, detail="blocked; invoke-edit not executed")
    return {
        "permission": "deny",
        "agent_message": _format_message(
            path,
            lines,
            manifest_output,
            invoke=invoke,
            invoke_output=invoke_output,
            blocked=True,
        ),
        "user_message": _user_notification(path, blocked=True),
    }


def handle_after_shell(data: dict) -> dict:
    """afterShellExecution — clear pending paths when agent ran matching invoke-edit."""
    command = str(data.get("command") or (data.get("tool_input") or {}).get("command") or "")
    output = str(
        data.get("output")
        or data.get("stdout")
        or data.get("result")
        or data.get("tool_output")
        or ""
    )
    blob = f"{command}\n{output}"
    if "tools run" not in blob.lower():
        return {}

    store = _load_clearance()
    pending = store.get("_pending", {})
    if not isinstance(pending, dict) or not pending:
        return {}

    cleared_names: list[str] = []
    for path, meta in list(pending.items()):
        if not isinstance(meta, dict):
            continue
        action = str(meta.get("action") or "")
        toolset = str(meta.get("toolset") or "")
        if action and action not in blob:
            continue
        if toolset and toolset not in blob:
            continue
        clear_path(path, detail="afterShell invoke-edit")
        cleared_names.append(Path(path).name)

    if not cleared_names:
        return {}
    return {
        "user_message": (
            "Manifest gate: unlocked edit after invoke-edit for "
            + ", ".join(cleared_names)
        )
    }


def parse_hook_payload(raw: bytes) -> dict:
    """Parse the JSON payload sent by Cursor on stdin.

    Cursor prepends two consecutive UTF-8 BOM markers (\\xef\\xbb\\xbf twice).
    Python's utf-8-sig codec only strips one, leaving a second BOM that breaks
    json.loads. We strip all leading BOM bytes before decoding.
    """
    stripped = raw.lstrip(b"\xef\xbb\xbf")
    return json.loads(stripped.decode("utf-8"))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "post"
    raw = sys.stdin.buffer.read()
    data = parse_hook_payload(raw)
    if mode == "read":
        result = handle_before_read_file(data)
    elif mode == "pre":
        result = handle_pre_tool_use(data)
    elif mode == "shell":
        result = handle_after_shell(data)
    else:
        result = handle_post_tool_use(data)
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
