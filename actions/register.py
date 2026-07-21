"""Register Actions with Tools — import this package to attach @action recipes."""
from __future__ import annotations

from actions.action import ActionRunner, discover_actions, has_actions
from tools.extensions import ToolsetExtensions

_registered = False


def _agent_capabilities(instance: object) -> list[str]:
    return ["agent"] if has_actions(instance) else []


def _validate_toolset(toolset_cls: type) -> None:
    ActionRunner.instance().validate_toolset(toolset_cls)


def _run_action(request, **kwargs):
    return ActionRunner.instance().run(request, **kwargs)


def register() -> None:
    global _registered
    if _registered:
        return
    host = ToolsetExtensions.instance()
    host.register_signature_discoverer(discover_actions)
    host.register_members("actions", discover_actions)
    host.register_capability_detector(_agent_capabilities)
    host.register_toolset_validator(_validate_toolset)
    host.register_run_handler("action", _run_action)
    _registered = True


register()
