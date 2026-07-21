"""CLI entry for python -m tools — manifest and run subcommands."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tools.tool import _ManifestYaml, RunError, Toolset, _ToolsetLoader, _ToolsetRunner

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


class _ToolsCli:
    """Routes ``python -m tools`` subcommands. Subclass and replace ``instance()`` to extend."""

    _instance: _ToolsCli | None = None

    def __init__(self) -> None:
        self._yaml = _ManifestYaml.instance()
        self._loader = _ToolsetLoader.instance()
        self._runner = _ToolsetRunner.instance()

    @classmethod
    def instance(cls) -> _ToolsCli:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, cli: _ToolsCli | None) -> None:
        cls._instance = cli

    def main(self, argv: list[str] | None = None) -> int:
        args = list(sys.argv[1:] if argv is None else argv)
        if not args:
            self._print_usage()
            return 1
        if args[0] == "manifest":
            return self._manifest_main(args[1:])
        if args[0] == "run":
            return self._run_main(args[1:])
        if args[0] == "agent-spec":
            return self._agent_spec_main(args[1:])
        self._print_usage()
        return 1

    def _print_usage(self) -> None:
        print(
            "usage: python -m tools manifest <module>:<Class> [--json] [--plain]\n"
            "       python -m tools run <request.yaml|-> [-o response.yaml] [--plain]\n"
            "       python -m tools agent-spec <spec.py> [--plain]",
            file=sys.stderr,
        )

    def _manifest_main(self, argv: list[str]) -> int:
        if len(argv) < 1:
            print(
                "usage: python -m tools manifest <module>:<Class> [--json] [--plain]",
                file=sys.stderr,
            )
            return 1
        plain = "--plain" in argv[1:]
        loaded = self._loader.load(argv[0])
        toolset = loaded.manifest
        if "--json" in argv[1:]:
            payload = {
                "tools": [tool.manifest for tool in toolset.tools.values()],
                "resources": [entry.manifest for entry in toolset.resource_entries.values()],
            }
            body = json.dumps(payload, indent=2)
            print(body if plain else self._yaml.fenced(body, lang="json"))
        else:
            body = toolset.front_matter
            print(body if plain else self._yaml.fenced(body))
        return 0

    def _run_main(self, argv: list[str]) -> int:
        if not argv:
            print(
                "usage: python -m tools run <request.yaml|-> [-o response.yaml] [--plain]",
                file=sys.stderr,
            )
            return 1
        source, output, plain = self._parse_run_args(argv)
        try:
            request = self._read_request_yaml(source)
            response = self._runner.run_request(request)
            self._write_response_yaml(response, output, plain=plain)
            return 0
        except RunError as exc:
            self._write_response_yaml(exc.response, output, plain=plain)
            return 1
        except Exception as exc:
            self._write_response_yaml({"ok": False, "error": str(exc)}, output, plain=plain)
            return 1

    def _parse_run_args(self, argv: list[str]) -> tuple[str, str | None, bool]:
        source = argv[0]
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
                        "missing output path after -o",
                        response={"ok": False, "error": "missing output path"},
                    )
                output = argv[index + 1]
                index += 2
                continue
            raise RunError(
                f"unknown argument {token!r}",
                response={"ok": False, "error": f"unknown argument: {token}"},
            )
        return source, output, plain

    def _read_request_yaml(self, source: str) -> dict[str, Any]:
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

    def _write_response_yaml(
        self, response: dict[str, Any], destination: str | None, *, plain: bool = False
    ) -> None:
        payload = (
            self._yaml.dump_manifest(response)
            if plain
            else self._yaml.dump_fenced(response)
        )
        if destination and destination != "-":
            Path(destination).write_text(payload + "\n", encoding="utf-8")
        else:
            print(payload)


    def _agent_spec_main(self, argv: list[str]) -> int:
        if len(argv) < 1:
            print(
                "usage: python -m tools agent-spec <spec.py> [--plain]",
                file=sys.stderr,
            )
            return 1
        plain = "--plain" in argv[1:]
        spec_path = Path(argv[0])
        if not spec_path.is_file():
            print(f"agent-spec: file not found: {spec_path}", file=sys.stderr)
            return 1
        try:
            manifest = read_manifest(spec_path)
            runbook = build_runbook(spec_path)
        except ValueError as exc:
            print(f"agent-spec: {exc}", file=sys.stderr)
            return 1
        payload = runbook.to_dict()
        payload["command"] = manifest.command
        payload["session"] = manifest.session
        payload["judge_session"] = manifest.judge_session
        body = self._yaml.dump_manifest(payload) if yaml else str(payload)
        if yaml and not plain:
            body = self._yaml.fenced(body)
        print(body)
        return 0


def _main(argv: list[str] | None = None) -> int:
    return _ToolsCli.instance().main(argv)
