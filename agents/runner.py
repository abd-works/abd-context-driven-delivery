"""Run @action requests against a toolset instance."""
from __future__ import annotations

from typing import Any

from agents.action import ActionExpander, ActionValidator
from tools.tool import ManifestYaml, RunError, Toolset


class ActionRunner:
    """Invokes one action from a parsed run request."""

    _instance: ActionRunner | None = None

    def __init__(self) -> None:
        self._expander = ActionExpander.instance()
        self._yaml = ManifestYaml.instance()

    @classmethod
    def instance(cls) -> ActionRunner:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_toolset(self, toolset_cls: type) -> None:
        ActionValidator.instance().validate_class(toolset_cls)

    def run(
        self,
        request: dict[str, Any],
        *,
        toolset_path: Any,
        action_name: Any,
        context: dict[str, Any],
        arguments: dict[str, Any],
        instance: Toolset,
    ) -> dict[str, Any]:
        if action_name not in instance.actions:
            raise RunError(
                f"unknown action {action_name!r}",
                response={"ok": False, "action": action_name, "error": "unknown action"},
            )
        action_entry = instance.actions[str(action_name)]
        try:
            expanded = self._expander.expand(
                action_func=action_entry.callable,
                toolset_path=str(toolset_path),
                context=context,
                arguments=arguments,
                tool_callables={name: tool.callable for name, tool in instance.tools.items()},
                instance=instance,
            )
        except Exception as exc:
            raise RunError(
                str(exc),
                response={"ok": False, "action": action_name, "error": str(exc)},
            ) from exc
        return self._build_response(
            request, toolset_path, action_name, arguments, instance, expanded
        )

    def _build_response(
        self,
        request: dict[str, Any],
        toolset_path: Any,
        action_name: Any,
        arguments: dict[str, Any],
        instance: Toolset,
        expanded: dict[str, Any],
    ) -> dict[str, Any]:
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(toolset_path),
            "action": str(action_name),
            "result": expanded["result"],
            "instructions": expanded["instructions"],
            "arguments": self._yaml.serialize_value(arguments),
            "tools": expanded["tools"],
        }
        if request.get("include_resources", True):
            response["resources"] = self._yaml.serialize_value(instance.resources)
        return response
