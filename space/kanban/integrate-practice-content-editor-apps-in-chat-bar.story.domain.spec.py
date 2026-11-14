"""Integrate Practice Content Editor Apps In Chat Bar at the domain tier, every scenario, on App and ServerHealth
themselves. npm is stubbed and so is the chat bar's launch (`StubbedLaunch`), so a press proves it installs, launches,
and opens each app only when its status needs it, and starts no server. The heavy domain spec replays the same
scenarios launching each app's real server."""

from space.kanban.editor_apps_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "integrate-practice-content-editor-apps-in-chat-bar"), DomainTier()))
