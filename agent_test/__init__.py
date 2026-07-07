"""agent_test — shared cursor-agent test primitives.

Public API:
    AgentSession   — persistent chat session
    AgentResult    — structured run outcome
    JudgeResult    — AI judge outcome
    AgentTest      — base pytest class (Given / When / Then)
"""
from agent_test.agent_test import (
    AgentResult,
    AgentSession,
    AgentTest,
    JudgeResult,
)

__all__ = ["AgentResult", "AgentSession", "AgentTest", "JudgeResult"]
