"""Integrate Practice Content Editor Apps In Chat Bar at the server tier: app.open and server-health.report through
the cdd server, as the chat bar's status row calls them. The domain tier proves every scenario's behaviour; this tier
proves the tools reach it, with a press that installs and launches and a refusal that reaches the caller."""

from space.kanban.editor_apps_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

WIRING = [
    "A press on the CDD Kanban readies it by its status and opens it beside the chat: not installed",
    "An install that fails says what failed and how to fix it",
]

globals().update(replay(load_shared(__file__, "integrate-practice-content-editor-apps-in-chat-bar"), ServerTier(), only=WIRING))
