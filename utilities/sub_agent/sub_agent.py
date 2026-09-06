# @toolset-manifest python -m tools manifest sub_agent.sub_agent:SubAgent
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Sub-agent decorator - marks a tool as a non-blocking background sub-agent launch.

Usage::

    @sub_agent
    @agent_instructions
    def run(self, tools: list, actions: list | None = None) -> str:
        \"\"\"Full instructions for the sub-agent go here - inline in the docstring.\"\"\"

When the agent reads the manifest it will see ``kind: sub_agent`` with
``launch: non_blocking``.  It must launch a background sub-agent using
the ``instructions`` text rather than executing the work inline.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable

from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import _SignatureReader


@dataclass(frozen=True)
class SubAgentTool:
    """One sub-agent-dispatched capability on a toolset.

    Appears in the manifest as ``kind: sub_agent`` so the calling agent knows
    to launch a non-blocking background sub-agent instead of running inline.
    """

    name: str
    callable: Callable[..., Any]

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.callable)

    @property
    def signature_entry(self) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "kind": "sub_agent",
            "launch": "non_blocking",
        }
        if self.instructions:
            entry["instructions"] = self.instructions
        reader = _SignatureReader.instance()
        parameters = reader.simple_parameters(self.callable)
        if parameters:
            entry["parameters"] = parameters
        returns = reader.simple_return_type(self.callable)
        if returns:
            entry["returns"] = returns
        return entry

    def add_to_signature(self, signature: dict[str, Any]) -> None:
        signature[self.name] = self.signature_entry


def sub_agent(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as a non-blocking sub-agent launch.

    Stack on top of ``@agent_tool`` or ``@agent_instructions``::

        @sub_agent
        @agent_instructions
        def run(self, tools: list, actions: list | None = None) -> str:
            \"\"\"Instructions sent verbatim to the sub-agent.\"\"\"

    The inner decorator runs first.  ``@sub_agent`` then sets ``_is_sub_agent = True``
    and suppresses ``_is_agent_tool`` so standard tool discovery skips it and
    ``discover_sub_agent_tools`` picks it up instead.
    """
    func._is_sub_agent = True  # type: ignore[attr-defined]
    func._is_agent_tool = False  # type: ignore[attr-defined]
    return func


def discover_sub_agent_tools(instance: Any) -> dict[str, SubAgentTool]:
    """Return all ``@sub_agent``-marked methods on *instance* as ``SubAgentTool`` objects."""
    discovered: dict[str, SubAgentTool] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_sub_agent", False):
            discovered[name] = SubAgentTool(name=name, callable=getattr(instance, name))
    return discovered


@agentic_toolset
class SubAgent:
    """Slash ``/sub-agent`` runs this prompt, listed context tools, and listed actions as one non-blocking sub-agent.

    Listed actions manage their own session lifecycle — do not wrap them in a turn wrapper.
    When actions is missing or empty, the worker does the context-tool work then calls /turn.
    ``context_tools`` is on AgenticToolset (via ``@agentic_toolset``) — same loader iterate/repair use for ``arguments.tools``.
    """

    @prompt(name="sub-agent")
    @sub_agent
    @agent_instructions
    def run(self, tools: list, actions: list | None = None, prompt: str | None = None) -> str:
        """Run the listed context tools and actions as one non-blocking sub-agent.

        tools — context tools (same arguments.tools as iterate / repair / generate).
        actions — optional other action kits (iterate, generate, grill, …) to run with those context tools.
        prompt — the task for the sub-agent. Uses the current chat context when omitted.

        The parent sees kind: sub_agent / launch: non_blocking and does not wait.
        Inside this sub-agent: follow this prompt. Do not inline any of that on the parent.

        Model — before launch, read ``.context/sessions/{session}/model`` for the current
        work session (or ``sessions/default`` when none). When that file has a model id,
        pass it as the sub-agent model (Task/tool model parameter). When unset, inherit
        the parent chat model. Never set disable-model-invocation.

    When actions is listed and non-empty: run each listed action with the listed
    context tools. Listed action kits already manage their own session lifecycle.
    Do not wrap those in a separate turn wrapper. This kit does not open a work
    session itself when actions are listed.

    When actions is missing or empty: do not leave the worker on a bare context-tool
    tools run. Do the work, then call **/turn** (``workspace.workspace:Turn``,
    tool ``turn``) with context_tool, action, utility, subject, and message.
    Report branch and commit back to the parent.
        """
        """Bring in every listed context tool (AgenticToolset.context_tools)."""
        for host in self.context_tools(tools):
            host
        if actions:
            """Run every listed action kit with those context tools."""
            for kit in self.context_tools(actions):
                kit
        else:
            """Do the context-tool work, then call turn (workspace.workspace:Turn, tool turn); report branch and commit."""
        return "Sub-agent launched with listed context tools and actions."
