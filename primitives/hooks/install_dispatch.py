"""Merge dispatch.py hook entries into .cursor/hooks.json."""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "_ensure_paths",
    Path(__file__).with_name("_ensure_paths.py"),
)
_ensure = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_ensure)
_REPO_ROOT = _ensure.ensure_repo_paths(Path(__file__))
_HOOKS_JSON = _REPO_ROOT / ".cursor" / "hooks.json"

from hooks.bootstrap import load
from hooks.deploy import deploy_dispatch
from hooks.hook import Hook


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
