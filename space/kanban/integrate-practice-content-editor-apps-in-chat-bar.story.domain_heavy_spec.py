"""Integrate Practice Content Editor Apps In Chat Bar at the domain tier, every scenario: each press that launches an
app starts the throwaway app's real server with node, so this replays on the heavy suite."""

from space.kanban.editor_apps_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "integrate-practice-content-editor-apps-in-chat-bar"), DomainTier(starts_servers=True)))
