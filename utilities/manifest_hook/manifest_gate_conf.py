"""Manifest hook configuration and IDE notification bridge.

Lives in utilities/manifest_hook/ — utilities that help context tools
govern their generated assets.

Config file: utilities/manifest_hook/.context/conf/manifest_gate.json
  { "mode": "normal" }  or  { "mode": "verbose" }

See: primitives/tools/hooks/.context/manifest-gate-stories-sketch.md
     ("Report Manifest Lifecycle Events").
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from pathlib import Path

_CONF_DIR = Path(__file__).resolve().parent / ".context" / "conf"
_CONF_FILE = _CONF_DIR / "manifest_gate.json"
_DEFAULT_MODE = "normal"
_VALID_MODES = frozenset({"normal", "verbose"})


def read_mode() -> str:
    """Return the configured mode - "normal" or "verbose". Defaults to "normal"
    when the config file is missing, unreadable, or holds an unrecognized value.
    """
    try:
        data = json.loads(_CONF_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _DEFAULT_MODE
    mode = data.get("mode") if isinstance(data, dict) else None
    return mode if mode in _VALID_MODES else _DEFAULT_MODE


_NOTIFIER_URL = "http://127.0.0.1:37291/notify"


def show_os_notification(title: str, body: str, *, error: bool = False) -> None:
    """Send a notification request to the manifest-gate-notifier Cursor extension.

    The extension runs a local HTTP server on port 37291 and calls the
    appropriate vscode.window.show*Message() API on receipt.  The call is
    fire-and-forget with a 1-second timeout; if the extension is not running
    the error is silently swallowed so the hook never blocks on notification.

    Called from both the hook (manifest_gate.py) and the CLI (_confirm_manifest_ran)
    so every manifest run — whether triggered by an agent touching a governed file
    or by a direct CLI call — produces a visible IDE notification.
    """
    payload = json.dumps({
        "title": title,
        "body": body,
        "level": "error" if error else "info",
    }).encode("utf-8")
    req = urllib.request.Request(
        _NOTIFIER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=1):
            pass
    except Exception:
        pass
