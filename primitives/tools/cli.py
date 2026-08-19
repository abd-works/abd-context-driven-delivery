"""CLI entry for python -m tools - manifest and run subcommands."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Bootstrap repo paths BEFORE any project imports so `python -m tools` works
# without a pre-set PYTHONPATH (mirrors utilities/manifest_hook/manifest_gate.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from agent_bdd import build_runbook, read_manifest  # noqa: E402
from tools.tool import _ManifestYaml, RunError, Toolset, _ToolsetLoader, _ToolsetRunner  # noqa: E402
from utilities.manifest_hook import manifest_gate_conf  # noqa: E402

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
            "       python -m tools run <module>:<Class> --tool NAME [--context k=v] [--arg k=v]\n"
            "       python -m tools run <module>:<Class> --action NAME [--fidelity NAME] [--context k=v] [--arg k=v]\n"
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
        self._confirm_manifest_ran(argv[0])
        return 0

    def _confirm_manifest_ran(self, target: str) -> None:
        """Emit one normal-mode confirmation that a manifest actually ran.

        Runs for every manifest command, whether triggered by a hook touching
        a governed asset or by a direct call like this one with no hook
        involved - the hook is not the only path that runs a manifest.
        Printed to stderr so it never pollutes the manifest body on stdout.
        Also fires a real OS notification so the user sees it in the system
        tray regardless of which chat window triggered the run.
        """
        if manifest_gate_conf.read_mode() not in ("normal", "verbose"):
            return
        print(f"[manifest] ran {target}", file=sys.stderr)
        from utilities.manifest_hook.manifest_gate_conf import show_os_notification
        show_os_notification("Manifest Gate", f"Manifest ran: {target}")

    def _run_main(self, argv: list[str]) -> int:
        if not argv:
            self._print_usage()
            return 1
        output: str | None = None
        plain = False
        try:
            request, output, plain = self._parse_run_invocation(argv)
            response = self._runner.run_request(request)
            self._write_response_yaml(response, output, plain=plain)
            return 0
        except RunError as exc:
            self._write_response_yaml(exc.response, output, plain=plain)
            return 1
        except Exception as exc:
            self._write_response_yaml({"ok": False, "error": str(exc)}, output, plain=plain)
            return 1

    def _parse_run_invocation(
        self, argv: list[str]
    ) -> tuple[dict[str, Any], str | None, bool]:
        target = argv[0]
        output: str | None = None
        plain = False
        tool_name: str | None = None
        action_name: str | None = None
        fidelity: str | None = None
        context: dict[str, Any] = {}
        arguments: dict[str, Any] = {}
        index = 1
        while index < len(argv):
            token = argv[index]
            if token == "--plain":
                plain = True
                index += 1
                continue
            if token in ("-o", "--output"):
                output, index = self._take_flag_value(argv, index, token)
                continue
            if token == "--tool":
                tool_name, index = self._take_flag_value(argv, index, token)
                continue
            if token == "--action":
                action_name, index = self._take_flag_value(argv, index, token)
                continue
            if token == "--fidelity":
                fidelity, index = self._take_flag_value(argv, index, token)
                continue
            if token == "--context":
                key, value, index = self._take_kv_flag(argv, index, token)
                context[key] = value
                continue
            if token in ("--arg", "--argument"):
                key, value, index = self._take_kv_flag(argv, index, token)
                arguments[key] = value
                continue
            raise RunError(
                f"unknown argument {token!r}",
                response={"ok": False, "error": f"unknown argument: {token}"},
            )
        if self._is_toolset_ref(target):
            return (
                self._direct_request(
                    target, tool_name, action_name, fidelity, context, arguments
                ),
                output,
                plain,
            )
        if tool_name or action_name or fidelity or context or arguments:
            raise RunError(
                "class flags require a module:Class target",
                response={"ok": False, "error": "class flags require a module:Class target"},
            )
        return self._read_request_yaml(target), output, plain

    def _is_toolset_ref(self, token: str) -> bool:
        if token == "-" or Path(token).is_file():
            return False
        if "\\" in token or token.startswith("/"):
            return False
        if len(token) >= 2 and token[1] == ":" and token[0].isalpha():
            return False
        return ":" in token

    def _direct_request(
        self,
        toolset: str,
        tool_name: str | None,
        action_name: str | None,
        fidelity: str | None,
        context: dict[str, Any],
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        if tool_name and action_name:
            raise RunError(
                "request must use tool or action, not both",
                response={"ok": False, "error": "tool and action are mutually exclusive"},
            )
        if not tool_name and not action_name:
            raise RunError(
                "request missing tool or action",
                response={"ok": False, "error": "request missing tool or action"},
            )
        request: dict[str, Any] = {"toolset": toolset}
        merged_context = dict(context)
        if fidelity is not None:
            merged_context["fidelity"] = fidelity
        if merged_context:
            request["context"] = merged_context
        if action_name:
            request["action"] = action_name
        else:
            request["tool"] = tool_name
        if arguments:
            request["arguments"] = arguments
        return request

    def _take_flag_value(
        self, argv: list[str], index: int, flag: str
    ) -> tuple[str, int]:
        if index + 1 >= len(argv):
            raise RunError(
                f"missing value after {flag}",
                response={"ok": False, "error": f"missing value after {flag}"},
            )
        return argv[index + 1], index + 2

    def _take_kv_flag(
        self, argv: list[str], index: int, flag: str
    ) -> tuple[str, Any, int]:
        raw, next_index = self._take_flag_value(argv, index, flag)
        if "=" not in raw:
            raise RunError(
                f"{flag} must be key=value",
                response={"ok": False, "error": f"{flag} must be key=value"},
            )
        key, value = raw.split("=", 1)
        return key, self._coerce_cli_value(value), next_index

    def _coerce_cli_value(self, value: str) -> Any:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

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
