"""Merge dispatch.py hook entries into .cursor/hooks.json."""

import json
from pathlib import Path

from hooks.deploy import deploy_dispatch
from hooks.bootstrap import load
from hooks.hook import Hook

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOKS_JSON = _REPO_ROOT / ".cursor" / "hooks.json"


def main() -> None:
    load()
    events = {entry["event"] for entry in Hook.registered()}
    if not events:
        print("No @hook handlers registered — nothing to install.")
        return
    deploy_dispatch(_REPO_ROOT, events)
    print(f"Installed dispatch hooks for {sorted(events)} -> {_HOOKS_JSON}")


if __name__ == "__main__":
    main()
