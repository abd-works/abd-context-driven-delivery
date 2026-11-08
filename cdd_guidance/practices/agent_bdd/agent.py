"""``agent(workspace, session_file)``: the block a spec drives an agent in, ``with agent(...) as run:``.

It picks the kind of block, so it sits above both: the cursor-agent CLI (``agent_cli_bdd.py``) or in-chat inbox files
(``agent_chat_bdd.py``), chosen by ``AGENT_BDD_IN_CHAT``. Each is an *AgentBlock* (``agent_block.py``), which imports
neither.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from cdd_guidance.practices.agent_bdd.agent_block import AgentBlock
from cdd_guidance.practices.agent_bdd.agent_chat_bdd import ChatAgentBlock
from cdd_guidance.practices.agent_bdd.agent_cli_bdd import CliAgentBlock
from cdd_guidance.practices.agent_bdd.conf import AgentBddConf


@contextmanager
def agent(workspace: Path, session_file: Path, *, in_chat: bool | None = None) -> Iterator[AgentBlock]:
    """The agent block for the steps inside: in chat when in_chat is set, or when ``AGENT_BDD_IN_CHAT`` says so, else
    the cursor-agent CLI. The agent's secrets and import paths load here, when a spec runs an agent, so importing the
    practice leaves the MCP host's environment alone."""
    AgentBddConf().configure()
    chosen = _in_chat_from_env() if in_chat is None else in_chat
    block_type = ChatAgentBlock if chosen else CliAgentBlock
    with block_type.opened(workspace, session_file) as block:
        yield block


def _in_chat_from_env() -> bool:
    return os.environ.get("AGENT_BDD_IN_CHAT", "").strip().lower() in {"1", "true", "yes"}
