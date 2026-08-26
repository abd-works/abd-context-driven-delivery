"""Run turn yaml sequence — one toolset instance (turn state persists)."""
from __future__ import annotations

from pathlib import Path

import yaml

from context_tools.clean_engineering.clean_engineering import CleanEngineering

CLI = Path("utilities/git/_cli.py")
INIT = Path("utilities/git/__init__.py")

SEQUENCE = [
    "_req_begin_correction.yaml",
    "_req_correction.yaml",
    "_req_finish_correction.yaml",
]


def main() -> None:
    improved = (
        f"--- {CLI.as_posix()} ---\n{CLI.read_text(encoding='utf-8')}\n\n"
        f"--- {INIT.as_posix()} ---\n{INIT.read_text(encoding='utf-8')}"
    )
    ce = CleanEngineering(
        fidelity="modules", path="utilities/git", session="workflow-package", workspace="."
    )
    ce.workspace.open(ce)
    for name in SEQUENCE:
        req = yaml.safe_load(Path(name).read_text(encoding="utf-8"))
        tool = req["tool"]
        args = dict(req.get("arguments") or {})
        if name == "_req_correction.yaml":
            args["improved"] = improved
        getattr(ce, tool)(**args)
        print(f"{name}: ok")


if __name__ == "__main__":
    main()
