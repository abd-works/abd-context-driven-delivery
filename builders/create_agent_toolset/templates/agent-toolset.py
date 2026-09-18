# Fill placeholders, then delete this comment block.
#
#   {ClassName}          PascalCase class name
#   {description}        class docstring — toolset description
#   {constructor_param}  constructor parameter name
#   {type}               Python type annotation
#   {constructor_instructions}
#   {property_name}      observable state
#   {tool_name}          @agent_tool verb
#   {tool_description}
#   {action_name}        @agent_instructions name
#   {action_param}
#   {action_instruction}
#   {mid_action_prose}

from __future__ import annotations

from agent_tools import agent_instructions, agent_tool, agent_toolset, tools


@agent_toolset
class {ClassName}:
    """{description}"""

    def __init__(self, {constructor_param}: {type}) -> None:
        """{constructor_instructions}"""
        self._{constructor_param} = {constructor_param}
        super().__init__()

    @property
    def {property_name}(self) -> {type}:
        """Current {property_name}."""
        return self._{property_name}

    @agent_tool
    def {tool_name}(self) -> str:
        """{tool_description}"""
        ...

    @agent_instructions
    def {action_name}(recipe, {action_param}: str) -> str:
        """{action_instruction}"""
        """{mid_action_prose}"""
        tools(recipe.toolset.{tool_name}())
        return "Instructions for {action_name} - {action_param}: {{{action_param}}}"
