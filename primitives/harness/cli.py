"""CLI entry for ``python -m harness run -``."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from primitives.harness.repo_paths import prepend_sys_path, repo_root

_REPO_ROOT = repo_root()
prepend_sys_path(_REPO_ROOT)

import primitives.harness.register  # noqa: F401,E402 — wire ToolsetExtensions on startup

from agent_bdd.yaml_fence import _dump_manifest, _fenced  # noqa: E402
from primitives.harness.errors import RunError  # noqa: E402
from primitives.harness.runner import ToolsetRunner  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def _write_response(response: dict[str, Any], destination: str | None, *, plain: bool = False) -> None:
    body = _dump_manifest(response) if plain else _fenced(_dump_manifest(response))
    if destination and destination != "-":
        Path(destination).write_text(body + "\n", encoding="utf-8")
    else:
        print(body)


def _read_request_yaml(source: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required to load YAML")
    text = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    parsed = yaml.safe_load(text)
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise RunError(
            "request must be a YAML mapping",
            response={"ok": False, "error": "invalid request"},
        )
    return parsed


def _run_main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m harness run <request.yaml|-> [-o response.yaml] [--plain]", file=sys.stderr)
        return 1
    target = argv[0]
    output: str | None = None
    plain = False
    index = 1
    while index < len(argv):
        token = argv[index]
        if token == "--plain":
            plain = True
            index += 1
            continue
        if token in ("-o", "--output"):
            if index + 1 >= len(argv):
                raise RunError(
                    "missing value after --output",
                    response={"ok": False, "error": "missing value after --output"},
                )
            output = argv[index + 1]
            index += 2
            continue
        raise RunError(
            f"unknown argument {token!r}",
            response={"ok": False, "error": f"unknown argument: {token}"},
        )
    try:
        request = _read_request_yaml(target)
        response = ToolsetRunner.instance().run_request(request)
        _write_response(response, output, plain=plain)
        return 0
    except RunError as exc:
        _write_response(exc.response, output, plain=plain)
        return 1
    except Exception as exc:
        _write_response({"ok": False, "error": str(exc)}, output, plain=plain)
        return 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(
            "usage: python -m harness run <request.yaml|-> [-o response.yaml] [--plain]",
            file=sys.stderr,
        )
        return 1
    if args[0] == "run":
        return _run_main(args[1:])
    print(
        "usage: python -m harness run <request.yaml|-> [-o response.yaml] [--plain]",
        file=sys.stderr,
    )
    return 1
