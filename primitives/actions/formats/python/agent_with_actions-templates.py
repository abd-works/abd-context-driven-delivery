# =============================================================================
# Agent-With-Actions Template - @toolset class with @agent_instructions orchestration recipes
# =============================================================================
# Fill placeholders (delete this block before committing):
#
#   {module_path}        e.g. my_domain.my_module:MyClass
#   {ClassName}          PascalCase class name
#   {description}        one-line description of what this toolset operates on
#   {constructor_param}  primary constructor parameter name (e.g. make, name, id)
#   {type}               Python type annotation (e.g. str, int, float)
#   {constructor_instructions}
#                        agent-visible constructor docstring: describe what gets
#                        created and any personality or flavour to assign
#   {resource_name}      observable state property (e.g. running, speed, status)
#   {tool_name}          verb naming a discrete capability (e.g. start, stop, send)
#   {tool_description}   one-line docstring for the tool
#   {action_name}        camelCase or snake_case orchestration goal (e.g. travelTo)
#   {action_param}       action parameter name (e.g. destination, target, goal)
#   {action_instruction} docstring command to the agent: tell it what to do and why
#   {mid_action_prose}   additional docstring mid-body: options, conditions, style
# =============================================================================

from __future__ import annotations

from primitives.actions.action import agent_instructions
from tools.tool import resource, agent_tool, toolset


@toolset
class {ClassName}:
    """{description}"""

    def __init__(self, {constructor_param}: {type}) -> None:
        """{constructor_instructions}"""
        self._{constructor_param} = {constructor_param}
        super().__init__()

    @property
    @resource
    def {resource_name}(self) -> {type}:
        """Current {resource_name}."""
        return self._{resource_name}

    @agent_tool
    def {tool_name}(self) -> str:
        """{tool_description}"""
        ...

    @agent_instructions
    def {action_name}(self, {action_param}: str) -> str:
        """{action_instruction}"""
        """{mid_action_prose}"""
        self.{tool_name}()
        return "Instructions for {action_name} - {action_param}: {{{action_param}}}"
