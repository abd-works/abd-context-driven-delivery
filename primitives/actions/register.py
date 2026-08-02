"""Register Actions with Tools - import this package to attach @action recipes."""
from __future__ import annotations

from primitives.actions.action import _ActionRunRequest, _ActionRunner, _discover_actions, _has_actions
from tools.extensions import ToolsetExtensions

_registered = False


def _agent_capabilities(instance: object) -> list[str]:
    return ["agent"] if _has_actions(instance) else []


def _validate_toolset(toolset_cls: type) -> None:
    _ActionRunner.instance().validate_toolset(toolset_cls)


def _run_action(request, **kwargs):
    return _ActionRunner.instance().invoke_action(_ActionRunRequest(request=request, **kwargs))


def _register() -> None:
    global _registered
    if _registered:
        return
    host = ToolsetExtensions.instance()
    host.register_signature_discoverer(_discover_actions)
    host.register_members("actions", _discover_actions)
    host.register_capability_detector(_agent_capabilities)
    host.register_toolset_validator(_validate_toolset)
    host.register_run_handler("action", _run_action)
    _registered = True


_register()
