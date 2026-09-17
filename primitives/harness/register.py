"""Register @agent_instructions discovery with ToolsetExtensions at import time."""

from __future__ import annotations

from agent_tools.agent_tools import AgentToolSet
from primitives.harness.extensions import ToolsetExtensions
from primitives.harness.runner import InstructionRunRequest, InstructionRunner

_registered = False


def _discover_actions(instance: object):
    return instance._discover_instruction_members()


def _has_actions(instance: object) -> bool:
    return bool(instance._discover_instruction_members())


def _validate_toolset_cls(toolset_cls: type) -> None:
    AgentToolSet._validate_toolset_class(toolset_cls)


def _run_action(request, **kwargs):
    return InstructionRunner.instance().invoke_action(
        InstructionRunRequest(request=request, **kwargs)
    )


def _register() -> None:
    global _registered
    if _registered:
        return
    host = ToolsetExtensions.instance()
    host.register_signature_discoverer(_discover_actions)
    host.register_members("actions", _discover_actions)
    host.register_capability_detector(_agent_capabilities)
    host.register_toolset_validator(_validate_toolset_cls)
    host.register_run_handler("action", _run_action)
    _registered = True


def _agent_capabilities(instance: object) -> list[str]:
    return ["agent"] if _has_actions(instance) else []


_register()
