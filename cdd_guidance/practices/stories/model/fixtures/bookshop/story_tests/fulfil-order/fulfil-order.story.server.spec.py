"""Fulfil Order at the server tier: the shared scenarios through the Bookshop's server."""

from story_tests.shared_stories import ServerTier, load_shared, replay

globals().update(replay(load_shared(__file__, "fulfil-order"), ServerTier()))
