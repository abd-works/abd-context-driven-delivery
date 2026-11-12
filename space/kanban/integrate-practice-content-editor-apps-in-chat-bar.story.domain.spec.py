"""Integrate Practice Content Editor Apps In Chat Bar at the domain tier: the scenarios that start no server, on App
and ServerHealth themselves. The scenarios that install or launch an app start its server, so they replay on the
heavy tiers."""

from space.kanban.editor_apps_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

STARTS_NO_SERVER = [
    "A press on the Story UI editor readies it by its status and opens it beside the chat: running",
    "An install that fails says what failed and how to fix it",
    "A press on the Graph app readies it by its status and opens it beside the chat: running",
    "A press on the CDD Kanban readies it by its status and opens it beside the chat: running",
]

globals().update(replay(load_shared(__file__, "integrate-practice-content-editor-apps-in-chat-bar"), DomainTier(), only=STARTS_NO_SERVER))
