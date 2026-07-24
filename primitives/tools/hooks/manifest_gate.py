"""VSCode agent hook — inject manifest instructions on Read and Write tool use.

PostToolUse (Read):  after the agent reads a file, inject its manifest output
                     as additional_context so the agent has instructions before planning.
PreToolUse (Write):  before the agent writes a file, inject its manifest output
                     as agent_message. Always allows — never blocks.

Both modes append a trace line to hooks/manifest_gate.log so you can see when
the hook fires without needing chat visibility.

Usage (from primitives/tools/hooks/manifest-gate.json):
  "command": "python primitives/tools/hooks/manifest_gate.py post"   # PostToolUse / Read
  "command": "python primitives/tools/hooks/manifest_gate.py pre"    # PreToolUse  / Write
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LOG_FILE = Path(__file__).resolve().parent / "manifest_gate.log"
_MANIFEST_PREFIXES = ("# @toolset-manifest", "# invoke-")
_SCAN_LINES = 15
_CATEGORY_DIRS = ("primitives", "utilities", "context_tools")


def _pythonpath_env() -> dict[str, str]:
    """Env with repo + category dirs on PYTHONPATH for hybrid imports."""
    env = os.environ.copy()
    entries = [str(_REPO_ROOT)] + [str(_REPO_ROOT / name) for name in _CATEGORY_DIRS]
    existing = env.get("PYTHONPATH", "")
    prefix = os.pathsep.join(entries)
    env["PYTHONPATH"] = prefix if not existing else prefix + os.pathsep + existing
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
                cwd=str(_REPO_ROOT),
                env=_pythonpath_env(),
                timeout=30,
            )
            if result.stdout.strip():
                outputs.append(result.stdout.strip())
        except (subprocess.TimeoutExpired, OSError):
            pass
    return "\n\n".join(outputs)


def _format_message(path: str, manifest_lines: list[str], manifest_output: str) -> str:
    header = "\n".join(f"  {l}" for l in manifest_lines)
    return (
        f"MANIFEST GATE — {path}\n"
        f"This file has manifest instructions that must be followed before editing:\n\n"
        f"{header}\n\n"
        f"Manifest output (injected automatically):\n{manifest_output}"
    )


def _extract_path(data: dict) -> str:
    """Extract file path from hook payload.

    Cursor uses different payload shapes per event type:
    - preToolUse / postToolUse: path is under tool_input.path or tool_input.file_path
    - afterFileEdit / beforeReadFile: path is at the top level as file_path
    """
    ti = data.get("tool_input") or {}
    return (
        ti.get("path")
        or ti.get("file_path")
        or data.get("file_path")
        or ""
    )


def handle_before_read_file(data: dict) -> dict:
    """beforeReadFile — fires before agent reads a file; inject manifest as agent_message."""
    path = _extract_path(data)
    if not path:
        return {}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("read", path, fired=False)
        return {}
    output = run_manifests(lines)
    if not output:
        _log("read", path, fired=False, detail="manifest ran but produced no output")
        return {}
    _log("read", path, fired=True, detail=f"{len(lines)} manifest line(s)")
    return {"agent_message": _format_message(path, lines, output)}


def handle_post_tool_use(data: dict) -> dict:
    """postToolUse — inject manifest as additional_context."""
    path = _extract_path(data)
    if not path:
        return {}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("post", path, fired=False)
        return {}
    output = run_manifests(lines)
    if not output:
        _log("post", path, fired=False, detail="manifest ran but produced no output")
        return {}
    _log("post", path, fired=True, detail=f"{len(lines)} manifest line(s)")
    return {"additional_context": _format_message(path, lines, output)}


def handle_pre_tool_use(data: dict) -> dict:
    """preToolUse / Write — inject manifest as agent_message; always allow."""
    path = _extract_path(data)
    if not path or not Path(path).is_file():
        return {"permission": "allow"}
    lines = scan_manifest_lines(path)
    if not lines:
        _log("pre ", path, fired=False)
        return {"permission": "allow"}
    output = run_manifests(lines)
    if not output:
        _log("pre ", path, fired=False, detail="manifest ran but produced no output")
        return {"permission": "allow"}
    _log("pre ", path, fired=True, detail=f"{len(lines)} manifest line(s)")
    return {"permission": "allow", "agent_message": _format_message(path, lines, output)}


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
    else:
        result = handle_post_tool_use(data)
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
