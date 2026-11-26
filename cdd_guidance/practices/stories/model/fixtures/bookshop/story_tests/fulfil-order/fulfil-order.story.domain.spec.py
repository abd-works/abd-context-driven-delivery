"""Fulfil Order at the domain tier: the shared scenarios on Order itself."""

from story_tests.shared_stories import DomainTier, load_shared, replay

globals().update(replay(load_shared(__file__, "fulfil-order"), DomainTier()))
