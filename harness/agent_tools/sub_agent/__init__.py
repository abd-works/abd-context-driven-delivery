"""Sub-agent toolset — ``from harness.agent_tools.sub_agent import SubAgent, subAgent``."""
from .mark import subAgent


def __getattr__(name: str):
    # The toolset decorates with harness.mcp's ``mcp``, and harness.mcp imports agent_tools;
    # loading it on first use lets either side be imported first.
    from importlib import import_module

    sub_agent = import_module(f"{__name__}.sub_agent")
    try:
        return getattr(sub_agent, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
