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
    args = parser.parse_args()

    from harness.installation.bootstrap import ensure_import_path

    ensure_import_path(_REPO)
    work = Path(
        args.workpath
        or os.environ.get("CDD_PROJECT")
        or (_REPO / "harness" / "agent_tools")
    ).resolve()
    os.environ.setdefault("CDD_REPO", str(_REPO))
    os.environ["CDD_PROJECT"] = str(work)

    if args.sync_file:
        target = Path(args.sync_file).resolve()
        from cdd_guidance.practices.clean_engineering.model.python.python_class_model import (
            PythonCleanEngineeringModel,
        )

        text = target.read_text(encoding="utf-8")
        model = PythonCleanEngineeringModel().parse(text)
        classes = sum(len(module.classes) for module in model.modules)
        print(f"sync {target}: {len(model.modules)} module(s), {classes} class(es)")

    from validate.validate import Validate

    report = Validate().validate(args.guidance)
    print(report)
    if "!" in report.splitlines()[0:1]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
