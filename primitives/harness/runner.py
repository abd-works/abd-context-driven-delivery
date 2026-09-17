"""Run toolset requests and invoke @agent_instructions from YAML."""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeAlias

from agent_tools.agent_tools import AgentInstructions, AgentOperation, AgentToolSet
from primitives.harness.errors import RunError
from primitives.harness.types import RunRequestDocument, RunResponseDocument, YamlValue
from primitives.harness.toolset_loader import ToolsetLoader

ContextDocument: TypeAlias = dict[str, Any]
ArgumentDocument: TypeAlias = dict[str, Any]


def _required_parameters(func: Callable[..., Any]) -> list[str]:
    sig = inspect.signature(func)
    required: list[str] = []
    for name, param in sig.parameters.items():
        if name in ("self", "cls", "recipe"):
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return required


class _RunValues:
    """Serialize run-response values for YAML-friendly dicts."""

    _instance: "_RunValues | None" = None

    @classmethod
    def instance(cls) -> "_RunValues":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, serializer: "_RunValues | None") -> None:
        cls._instance = serializer

    def serialize_value(self, raw_value: YamlValue) -> YamlValue:
        if isinstance(raw_value, Path):
            return str(raw_value)
        if isinstance(raw_value, dict):
            return {
                key: self.serialize_value(nested_value)
                for key, nested_value in raw_value.items()
            }
        if isinstance(raw_value, list):
            return [self.serialize_value(element) for element in raw_value]
        to_dict = getattr(raw_value, "to_dict", None)
        if callable(to_dict):
            return self.serialize_value(to_dict())
        return raw_value

class ToolsetRunner:
    """Invokes one tool from a YAML request dict. Subclass and replace ``instance()`` to extend."""

    _instance: ToolsetRunner | None = None

    def __init__(self) -> None:
        self._loader = ToolsetLoader.instance()
        self._yaml = _RunValues.instance()

    @classmethod
    def instance(cls) -> ToolsetRunner:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, runner: ToolsetRunner | None) -> None:
        cls._instance = runner

    def run_request(self, request: RunRequestDocument) -> RunResponseDocument:
        from workspace import SessionLog

        parsed = self._parse_run_request(request)
        SessionLog.instance().set_session(parsed.session)
        toolset_cls = self._loader.load(str(parsed.toolset_path))
        instance = self._build_instance(toolset_cls, parsed.context)
        if parsed.action_name:
            return self._run_action(request, parsed, instance)
        return self._run_tool(request, parsed, instance)

    def _run_tool(
        self,
        request: dict[str, Any],
        parsed: "_RunRequest",
        instance: AgentToolSet,
    ) -> dict[str, Any]:
        result = self._invoke_tool(instance, str(parsed.tool_name), parsed.arguments)
        return self._build_tool_response(request, parsed.toolset_path, parsed.tool_name, instance, result)

    def _run_action(
        self,
        request: dict[str, Any],
        parsed: "_RunRequest",
        instance: AgentToolSet,
    ) -> dict[str, Any]:
        return InstructionRunner.instance().run_from_request(
            request,
            toolset_path=parsed.toolset_path,
            action_name=parsed.action_name,
            context=parsed.context,
            arguments=parsed.arguments,
            instance=instance,
        )

    def _parse_run_request(self, request: dict[str, Any]) -> "_RunRequest":
        if not isinstance(request, dict):
            raise RunError("request must be a YAML mapping", response={"ok": False, "error": "invalid request"})
        toolset_path = request.get("toolset")
        if not toolset_path:
            raise RunError("request missing toolset", response={"ok": False, "error": "request missing toolset"})
        tool_name = request.get("tool")
        action_name = request.get("action")
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
        context = self._mapping_field(request, "context", default={})
        arguments = self._mapping_field(request, "arguments", default={})
        session = request.get("session")
        log_control = request.get("log")
        return _RunRequest(
            toolset_path=toolset_path,
            tool_name=tool_name,
            action_name=action_name,
            context=context,
            arguments=arguments,
            session=str(session) if session is not None else None,
            log_control=str(log_control) if log_control is not None else None,
        )

    def _mapping_field(
        self, request: dict[str, Any], field_name: str, *, default: dict[str, Any]
    ) -> dict[str, Any]:
        field_value = request.get(field_name, default)
        if not isinstance(field_value, dict):
            raise RunError(
                f"{field_name} must be a mapping",
                response={"ok": False, "error": f"invalid {field_name}"},
            )
        return field_value

    def _build_instance(self, toolset_cls: type, context: dict[str, Any]) -> AgentToolSet:
        missing = [name for name in _required_parameters(toolset_cls.__init__) if name not in context]
        if missing:
            joined = ", ".join(missing)
            raise RunError(
                f"{toolset_cls.__name__} missing required context params: {joined} — use AskQuestion to get the value from the user",
                response={
                    "ok": False,
                    "error": "missing required context",
                    "missing": missing,
                    "detail": f"Use AskQuestion to collect: {joined}",
                },
            )
        try:
            return toolset_cls(**context)
        except TypeError as exc:
            raise RunError(
                f"invalid context for {toolset_cls.__name__}: {exc}",
                response={"ok": False, "error": "invalid context", "detail": str(exc)},
            ) from exc

    def _invoke_tool(self, instance: AgentToolSet, tool_name: str, arguments: dict[str, Any]) -> Any:
        bound = self._resolve_runnable(instance, tool_name)
        if bound is None:
            raise RunError(
                f"unknown tool {tool_name!r}",
                response={"ok": False, "tool": tool_name, "error": "unknown tool"},
            )
        self._validate_arguments(bound, arguments)
        return getattr(instance, tool_name)(**arguments)

    def _resolve_runnable(self, instance: AgentToolSet, tool_name: str) -> Any:
        """A @agent_tool, or a registered extension member that is not an @agent_instructions."""
        if tool_name in instance.tools:
            return instance.tools[tool_name]
        from primitives.harness.extensions import ToolsetExtensions

        members = ToolsetExtensions.instance().members("sub_agent", instance)
        if tool_name in members:
            return members[tool_name]
        return None

    def _validate_arguments(self, tool: AgentOperation, arguments: dict[str, Any]) -> None:
        missing = [name for name in _required_parameters(tool.callable) if name not in arguments]
        if missing:
            joined = ", ".join(missing)
            raise RunError(
                f"{tool.name} missing required arguments: {joined} — use AskQuestion to get the value from the user",
                response={
                    "ok": False,
                    "tool": tool.name,
                    "error": "missing required arguments",
                    "missing": missing,
                    "detail": f"Use AskQuestion to collect: {joined}",
                },
            )

    def _build_tool_response(
        self,
        request: dict[str, Any],
        toolset_path: Any,
        tool_name: Any,
        instance: AgentToolSet,
        result: Any,
    ) -> dict[str, Any]:
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(toolset_path),
            "tool": str(tool_name),
            "result": self._yaml.serialize_value(result),
        }
        return response


@dataclass(frozen=True)
class _RunRequest:
    toolset_path: Any
    tool_name: Any
    action_name: Any
    context: dict[str, Any]
    arguments: dict[str, Any]
    session: str | None = None
    log_control: str | None = None


@dataclass(frozen=True)
class InstructionRunRequest:
    request: RunRequestDocument
    toolset_path: str
    action_name: str
    context: ContextDocument
    arguments: ArgumentDocument
    instance: Any


@dataclass(frozen=True)
class _RunOutput:
    """Bundles the expansion result and run-request metadata for building a run response."""

    toolset_path: Any
    action_name: Any
    arguments: dict[str, Any]
    instance: Any
    expanded: dict[str, Any]


class InstructionRunner:
    """Invokes one action from a parsed run request."""

    _instance: "InstructionRunner | None" = None

    @classmethod
    def instance(cls) -> "InstructionRunner":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._yaml = _RunValues.instance()

    def validate_toolset(self, toolset_cls: type) -> None:
        AgentToolSet._validate_toolset_class(toolset_cls)

    def run_from_request(self, request: dict[str, Any], **kwargs: Any) -> RunResponseDocument:
        return self.invoke_action(InstructionRunRequest(request=request, **kwargs))

    def _expand_action(
        self,
        action_entry: AgentInstructions,
        request: InstructionRunRequest,
    ) -> dict[str, Any]:
        from primitives.harness.runbook import format_agent_instructions

        expanded = action_entry.expand(request.context, request.arguments)
        instructions = format_agent_instructions(
            instructions=expanded.instructions,
            tools=expanded.tools,
            toolset_path=request.toolset_path,
            context=request.context,
            tool_callables={
                name: operation.callable for name, operation in request.instance.operations.items()
            },
        )
        return {
            "result": expanded.result,
            "instructions": instructions,
            "tools": expanded.tools,
        }

    def _try_expand_action(
        self, action_entry: "AgentInstructions", request: InstructionRunRequest
    ) -> dict[str, Any]:
        """Expand *action_entry* and translate any exception into a RunError."""
        # RunError defined above
        try:
            return self._expand_action(action_entry, request)
        except Exception as exc:
            raise RunError(
                str(exc),
                response={"ok": False, "action": str(request.action_name), "error": str(exc)},
            ) from exc

    def invoke_action(self, request: InstructionRunRequest) -> RunResponseDocument:
        action_name = str(request.action_name)
        if action_name not in request.instance.instructions:
            raise RunError(
                f"unknown action {action_name!r}",
                response={"ok": False, "action": action_name, "error": "unknown action"},
            )
        turn = getattr(request.instance, "turn", None)
        if turn is not None and hasattr(turn, "bind_from_host"):
            workspace = getattr(request.instance, "workspace", None)
            if workspace is not None and getattr(workspace, "current_work_session", None) is None:
                if hasattr(workspace, "open"):
                    try:
                        workspace.open(request.instance)
                    except (ValueError, TypeError):
                        pass
            turn.open(request.instance, action=action_name)
        expanded = self._try_expand_action(request.instance.instructions[action_name], request)
        return self._build_response(request.request, _RunOutput(
            toolset_path=request.toolset_path, action_name=request.action_name,
            arguments=request.arguments, instance=request.instance, expanded=expanded,
        ))

    def _build_response(
        self,
        request: dict[str, Any],
        output: _RunOutput,
    ) -> dict[str, Any]:
        # _RunValues defined above
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(output.toolset_path),
            "action": str(output.action_name),
            "result": output.expanded["result"],
            "instructions": output.expanded["instructions"],
            "arguments": _RunValues.instance().serialize_value(output.arguments),
            "tools": output.expanded["tools"],
        }
        return response
