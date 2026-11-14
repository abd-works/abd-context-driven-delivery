"""Integrate Practice Content Editor Apps On Board at the domain tier: the knowledge graph a ticket's graph widget and
the board header open, on the sessions and the board themselves."""

from space.kanban.knowledge_graph_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "integrate-practice-content-editor-apps-on-board"), DomainTier()))
