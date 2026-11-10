"""Fixtures for @subAgent specs."""
from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, subAgent


@agent_toolset
class MarkedToolExample:
    @subAgent
    @agent_tool
    def run_check(self) -> str:
        """Run the focused check."""
        return "ok"


@agent_toolset
class MarkedActionExample:
    @subAgent
    @agent_instructions
    def plan_work(self, task: str) -> str:
        """Plan work for {{task}}."""
        "Break the task into steps."
        return "Planned {{task}}"
