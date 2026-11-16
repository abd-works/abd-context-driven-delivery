"""Run clean-engineering validate (and optional python class-model parse) with catalog imports.

Same ``sys.path`` as the CDD MCP host — use this instead of bare ``python -c`` when calling
``validate.validate`` or action toolsets outside Cursor.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def main() -> int:
    args = _arguments()
    _prepare(args.workpath)
    if args.sync_file:
        target = Path(args.sync_file).resolve()
        print(_parsed_classes(target, target.read_text(encoding="utf-8")))
    report = _validated(args.guidance)
    print(report)
    return _exit_code(report)


def _prepare(workpath: str | None) -> None:
    """The MCP host's import path, and the module folder to judge."""
    from harness.installation.repository_toolsets import RepositoryToolsets

    RepositoryToolsets(_REPO).ensure_import_path()
    _use_workpath(workpath)


def _validated(guidance: str) -> str:
    from cdd_guidance.actions.validate.validate import Validate

    return Validate().validate(guidance)


def _exit_code(report: str) -> int:
    """1 when the report's first line flags a failure, else 0."""
    return 1 if "!" in report.splitlines()[0:1] else 0


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate artifacts under a workpath using clean-engineering (or other) guidance.",
    )
    parser.add_argument(
        "--guidance",
        default="clean-engineering-code",
        help="Practice/fidelity slug (default: clean-engineering-code).",
    )
    parser.add_argument(
        "--workpath",
        default=None,
        help="Module folder to judge (default: CDD_PROJECT or harness/agent_tools).",
    )
    parser.add_argument(
        "--sync-file",
        default=None,
        help="Optional .py file to parse with PythonCleanEngineeringModel before validate.",
    )
    return parser.parse_args()


def _use_workpath(workpath: str | None) -> None:
    """Point the validate action at the module folder to judge, the way the MCP host names the project."""
    work = Path(workpath or os.environ.get("CDD_PROJECT") or (_REPO / "harness" / "agent_tools")).resolve()
    os.environ.setdefault("CDD_REPO", str(_REPO))
    os.environ["CDD_PROJECT"] = str(work)


def _parsed_classes(target: Path, source: str) -> str:
    """How many modules and classes the class model reads from target's source."""
    from cdd_guidance.practices.clean_engineering.model.python.python_class_model import (
        PythonCleanEngineeringModel,
    )

    model = PythonCleanEngineeringModel().parse(source)
    classes = sum(len(module.classes) for module in model.modules)
    return f"sync {target}: {len(model.modules)} module(s), {classes} class(es)"


if __name__ == "__main__":
    raise SystemExit(main())
